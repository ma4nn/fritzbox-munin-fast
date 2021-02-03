#!/usr/bin/env python3
"""
  FritzboxInterface - A munin plugin for Linux to monitor AVM Fritzbox
  Copyright (C) 2015 Christian Stade-Schuldt
  Copyright (C) 2019 Rene Walendy
  Author: Christian Stade-Schuldt, Rene Walendy
  Like Munin, this plugin is licensed under the GNU GPL v2 license
  http://www.opensource.org/licenses/GPL-2.0

  Add the following section to your munin-node's plugin configuration:

  [fritzbox_*]
  env.fritzbox_ip [ip address of the fritzbox]
  env.fritzbox_password [fritzbox password]
  env.fritzbox_user [fritzbox user, set any value if not required]
  env.fritzbox_use_tls [true or false, optional]

  This plugin supports the following munin configuration parameters:
  #%# family=auto contrib
  #%# capabilities=autoconf

  The initial script was inspired by
  https://www.linux-tips-and-tricks.de/en/programming/389-read-data-from-a-fritzbox-7390-with-python-and-bash
  framp at linux-tips-and-tricks dot de
"""

import hashlib
import sys

import requests
from lxml import etree
from FritzboxConfig import FritzboxConfig
from FritzboxFileSession import FritzboxFileSession

class FritzboxInterface:
  config = None
  __session = None
  __baseUri = ""

  # default constructor
  def __init__(self):
    self.config = FritzboxConfig()
    self.__session = FritzboxFileSession(self.config.server, self.config.user, self.config.port)
    self.__baseUri = self.__getBaseUri()

  def __getBaseUri(self):
    DEFAULT_PORTS = (80, 443)
    SCHEMES = ('http', 'https')
    if self.config.port and self.config.port != DEFAULT_PORTS[self.config.useTls]:
        return '{}://{}:{}'.format(SCHEMES[self.config.useTls], self.config.server, self.config.port)
    else:
        return '{}://{}'.format(SCHEMES[self.config.useTls], self.config.server)

  def getPageWithLogin(self, page, data={}):
    return self.__callPageWithLogin(self.__get, page, data)

  def postPageWithLogin(self, page, data={}):
    return self.__callPageWithLogin(self.__post, page, data)

  def __getSessionId(self):
    """Obtains the session id after login into the Fritzbox.
    See https://avm.de/fileadmin/user_upload/Global/Service/Schnittstellen/AVM_Technical_Note_-_Session_ID.pdf
    for details (in German).

    :return: the session id
    """

    headers = {"Accept": "application/xml", "Content-Type": "text/plain"}

    url = '{}/login_sid.lua'.format(self.__baseUri)
    try:
      r = requests.get(url, headers=headers, verify=self.config.certificateFile)
      r.raise_for_status()
    except (requests.exceptions.HTTPError, requests.exceptions.SSLError) as err:
      print(err)
      sys.exit(1)

    params = {}
    root = etree.fromstring(r.content)
    session_id = root.xpath('//SessionInfo/SID/text()')[0]
    if session_id == "0000000000000000":
      challenge = root.xpath('//SessionInfo/Challenge/text()')[0]
      challenge_bf = ('{}-{}'.format(challenge, self.config.password)).encode('utf-16le')
      m = hashlib.md5()
      m.update(challenge_bf)
      response_bf = '{}-{}'.format(challenge, m.hexdigest().lower())
      params['response'] = response_bf
    else:
      return session_id

    params['username'] = self.config.user

    headers = {"Accept": "text/html,application/xhtml+xml,application/xml", "Content-Type": "application/x-www-form-urlencoded"}

    url = '{}/login_sid.lua'.format(self.__baseUri)
    try:
      r = requests.get(url, headers=headers, params=params, verify=self.config.certificateFile)
      r.raise_for_status()
    except (requests.exceptions.HTTPError, requests.exceptions.SSLError) as err:
      print(err)
      sys.exit(1)

    root = etree.fromstring(r.content)
    session_id = root.xpath('//SessionInfo/SID/text()')[0]
    if session_id == "0000000000000000":
      print("ERROR - No SID received because of invalid password")
      sys.exit(0)

    self.__session.saveSessionId(session_id)

    return session_id

  def __callPageWithLogin(self, method, page, data={}):
    session_id = self.__session.loadSessionId()

    if session_id != None:
      try:
        return method(session_id, page, data)
      except (requests.exceptions.HTTPError,
             requests.exceptions.SSLError) as e:
        code = e.response.status_code
        if code != 403:
          print(e)
          sys.exit(1)

    session_id = self.__getSessionId()
    return method(session_id, page, data)

  def __post(self, session_id, page, data={}):
    """Sends a POST request to the Fritzbox and returns the response

    :param session_id: a valid session id
    :param page: the page you are regquesting
    :param data: POST data in a map
    :return: the content of the page
    """

    data['sid'] = session_id

    headers = {"Accept": "application/json", "Content-Type": "application/x-www-form-urlencoded"}

    url = '{}/{}'.format(self.__baseUri, page)

    r = requests.post(url, headers=headers, data=data, verify=self.config.certificateFile)
    r.raise_for_status()

    return r.content

  def __get(self, session_id, page, data={}):
      """Fetches a page from the Fritzbox and returns its content

      :param session_id: a valid session id
      :param page: the page you are regquesting
      :param params: GET parameters in a map
      :return: the content of the page
      """

      headers = {"Accept": "application/xml", "Content-Type": "text/plain"}

      params = data
      params["sid"] = session_id
      url = '{}/{}'.format(self.__baseUri, page)

      r = requests.get(url, headers=headers, params=params, verify=self.config.certificateFile)
      r.raise_for_status()

      return r.content
