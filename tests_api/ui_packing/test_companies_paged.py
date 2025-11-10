import os
import requests
import json


def test_companies_paged(auth_token):
    base_url = os.getenv("BASE_URL", "").rstrip("/")
    assert base_url, "BASE_URL пустой — проверь .env"

    url = f"{base_url}/api/company-catalog/graphql"

    query = """
    query getLegalEntities($where: CompanyDtoFilterInput, $order: [CompanyDtoSortInput!]) {
      companiesPaged(where: $where, order: $order) {
        items {
          id
          eori
          vat
          name
          country {
            alpha2: id
            id
            name
            __typename
          }
          __typename
        }
        __typename
      }
    }
    """

    variables = {
        "where": {
            "and": [
                {
                    "isValid": {
                        "eq": True,
                    }
                }
            ]
        }
    }

    payload = {"query": query, "variables": variables}
    headers = {
        "Cookie": f"JWT={auth_token};",
        "Content-Type": "application/json",
    }

    response = requests.post(url, json=payload, headers=headers)

    assert response.status_code == 200
    data = response.json()

    # Проверяем базовую структуру ответа
    assert "data" in data, f"Нет поля data в ответе: {json.dumps(data, ensure_ascii=False)}"
    assert "companiesPaged" in data["data"], f"Нет companiesPaged: {json.dumps(data, ensure_ascii=False)}"
    assert "items" in data["data"]["companiesPaged"], "Нет items в companiesPaged"

    items = data["data"]["companiesPaged"]["items"]
    assert isinstance(items, list), "items должен быть списком"

    # Если список не пуст — проверим поля первого элемента
    if items:
        first = items[0]
        for key in ["id", "eori", "vat", "name", "__typename"]:
            assert key in first, f"В компании отсутствует поле {key}"

        # country — опционально, но если есть, проверим ключевые поля
        if "country" in first and first["country"] is not None:
            country = first["country"]
            for key in ["id", "name", "alpha2", "__typename"]:
                assert key in country, f"В country отсутствует поле {key}"

    # Для отладки первые 2 элемента
#    print(response.text)
#    print(json.dumps(items[:2], ensure_ascii=False, indent=2))
