import pytest
from selenium.webdriver.chrome.options import Options


@pytest.fixture
def pytest_setup_options():
    # Use headless Chrome flags that are stable in CI containers.
    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    return options
