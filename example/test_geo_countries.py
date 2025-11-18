import os
import requests
import json

def test_get_countries(auth_token):
    base_url = os.getenv("BASE_URL", "").rstrip("/")
    assert base_url, "BASE_URL пустой — проверь .env"

    url = f"{base_url}/api/geo/graphql"

    query = """
    query getCountries($where: CountryFilterInput) {
      countries(where: $where) {
        id
        nameEn
        nameRu
        isoCode
        alpha2
        __typename
      }
    }
    """
    variables = {"where": {}}

    payload = {"query": query, "variables": variables}
    headers = {
        "Cookie": f"JWT={auth_token};",
        "Content-Type": "application/json",
    }

    response = requests.post(url, json=payload, headers=headers)

    assert response.status_code == 200
    data = response.json()
    assert "data" in data and "countries" in data["data"]
    
    # Для отладки первые 3 элемента
#\    countries = data["data"]["countries"]
#    first_three = countries[:3]
#    print(json.dumps(first_three, ensure_ascii=False, indent=2))

