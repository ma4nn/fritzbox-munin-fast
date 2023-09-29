from unittest.mock import patch
import pytest
from test_request_mock import RequestMock


@pytest.fixture(autouse=True)
def fixture_version(request):
  with patch('requests.request', side_effect=RequestMock) as mock_requests:
    mock_requests.side_effect.version = request.param if hasattr(request, "param") else None
    yield
