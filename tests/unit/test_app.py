import pytest

from exls.app import app


@pytest.mark.unit
def test_app():
    assert app is not None
