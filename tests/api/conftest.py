import os
import pathlib

import pytest
import requests


@pytest.fixture(scope="session")
def base_url(load_env) -> str:
    url = os.getenv("BASE_URL", "").rstrip("/")
    assert url, "BASE_URL пустой — проверь .env"
    return url


@pytest.fixture(scope="session")
def assets_dir() -> pathlib.Path:
    return pathlib.Path(__file__).resolve().parent / "assets"


@pytest.fixture(scope="session")
def http(auth_token: str):
    session = requests.Session()
    session.headers.update({"Cookie": f"JWT={auth_token};"})
    return session


@pytest.fixture
def graphql(base_url: str, http: requests.Session):
    def _call(relative_path: str, query: str, variables: dict | None = None) -> dict:
        url = f"{base_url}{relative_path}"
        payload = {"query": query, "variables": variables or {}}
        headers = {"Content-Type": "application/json"}
        resp = http.post(url, json=payload, headers=headers)
        assert resp.status_code == 200, f"GraphQL error {resp.status_code}: {resp.text}"
        return resp.json()

    return _call


