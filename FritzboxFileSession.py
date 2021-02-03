#!/usr/bin/env python3

import os

class FritzboxFileSession:
  __separator = "__"
  __server = ""
  __user = ""
  __port = None

  # default constructor
  def __init__(self, server: str, user: str, port: int):
    if self.__separator in server or self.__separator in user:
      raise Exception("Reserved string \"" + self.__separator + "__\" in server or user name")

    self.__server = server
    self.__user = user
    self.__port = port

  def __getSessionDir(self):
    return os.getenv('MUNIN_PLUGSTATE') + '/fritzbox'

  def __getSessionFilename(self):
    return self.__server + self.__separator + str(self.__port) + self.__separator + self.__user + '.sid'

  def saveSessionId(self, session_id):
    statedir = self.__getSessionDir()

    if not os.path.exists(statedir):
      os.makedirs(statedir)

    statefilename = statedir + '/' + self.__getSessionFilename()

    with open(statefilename, 'w') as statefile:
      statefile.write(session_id)

  def loadSessionId(self):
    statefilename = self.__getSessionDir() + '/' + self.__getSessionFilename()
    if not os.path.exists(statefilename):
      return None

    with open(statefilename, 'r') as statefile:
      session_id = statefile.readline()
      return session_id