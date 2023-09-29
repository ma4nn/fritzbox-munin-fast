from unittest.mock import patch
import pytest
from test_response_mock import ResponseMock


@pytest.fixture(autouse=True)
def fixture_version(request):
  with patch('requests.request', side_effect=ResponseMock) as mock_requests:
    mock_requests.side_effect.version = request.param if hasattr(request, "param") else None
    yield
