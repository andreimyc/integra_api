import os
import pytest
import requests
from dotenv import load_dotenv

@pytest.fixture(scope="session", autouse=True)
def load_env():
    project_root = os.path.dirname(os.path.abspath(__file__))
    dotenv_path = os.path.join(project_root, ".env")
    loaded = load_dotenv(dotenv_path=dotenv_path, override=True)
    assert loaded, f".env не найден/не загружен: {dotenv_path}"

@pytest.fixture(scope="session")
def auth_token():
    base_url = os.getenv("BASE_URL", "").rstrip("/")
    username = os.getenv("USERNAME", "")
    password = os.getenv("PASSWORD", "")

    url = f"{base_url}/api/identity/users/login"
    payload = {
        "userName": username,
        "password": password,
        "type": "otp",
        "useCookies": True,
    }

    response = requests.post(url, json=payload)
    print(f"Status: {response.status_code}")
    print(f"Response: {response.text}")
    assert response.status_code == 200, f"unexpected status={response.status_code} body={response.text}"

    data = response.json()
    token = data.get("accessToken")
    assert token, "accessToken отсутствует в ответе"
    return token

@pytest.fixture(scope="session")
def company_data():
    """
    Фикстура для доступа к данным компании, сохраненным в test_companies_paged.
    Возвращает словарь с данными компании из os.environ.
    Использование в тестах: def test_something(company_data):
        company_id = company_data.get("COMPANY_ID")
    """
    return {
        "COMPANY_ID": os.getenv("COMPANY_ID", ""),
        "COMPANY_EORI": os.getenv("COMPANY_EORI", ""),
        "COMPANY_VAT": os.getenv("COMPANY_VAT", ""),
        "COMPANY_NAME": os.getenv("COMPANY_NAME", ""),
        "COMPANY_COUNTRY_ALPHA2": os.getenv("COMPANY_COUNTRY_ALPHA2", ""),
        "COMPANY_COUNTRY_ID": os.getenv("COMPANY_COUNTRY_ID", ""),
        "COMPANY_COUNTRY_NAME": os.getenv("COMPANY_COUNTRY_NAME", ""),
        "COMPANY_COUNTRY_TYPENAME": os.getenv("COMPANY_COUNTRY_TYPENAME", ""),
    }