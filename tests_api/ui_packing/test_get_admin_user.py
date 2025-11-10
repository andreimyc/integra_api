import os
import requests
import json


def test_get_admin_user(auth_token):
    base_url = os.getenv("BASE_URL", "").rstrip("/")
    assert base_url, "BASE_URL пустой — проверь .env"

    url = f"{base_url}/api/identity/graphql"

    query = """
    query getCreatedUsers($skip: Int, $take: Int, $where: UserModelFilterInput, $order: [UserModelSortInput!]) {
      usersPaged(skip: $skip, take: $take, where: $where, order: $order) {
        totalCount
        items {
          id
          userName
          fullName
          email
          telegramUserName
          roles {
            name
            id
            __typename
          }
          company {
            id
            nameEn
            nameRu
            __typename
          }
          client {
            id
            nic
            __typename
          }
          isEnabled
          __typename
        }
        __typename
      }
    }
    """

    variables = {
        "skip": 0,
        "take": 100,
        "where": {
            "and": [
                {
                    "or": [
                        {
                            "userName": {
                                "contains": "Admin"
                            }
                        }
                    ]
                }
            ]
        },
        "order": []
    }

    payload = {"query": query, "variables": variables}
    headers = {
        "Cookie": f"JWT={auth_token};",
        "Content-Type": "application/json",
    }

    response = requests.post(url, json=payload, headers=headers)

    assert response.status_code == 200, (
        f"unexpected status={response.status_code} body={response.text}"
    )
    data = response.json()

    # Проверяем базовую структуру ответа
    assert "data" in data, f"Нет поля data в ответе: {json.dumps(data, ensure_ascii=False)}"
    assert "usersPaged" in data["data"], f"Нет usersPaged: {json.dumps(data, ensure_ascii=False)}"

    users_paged = data["data"]["usersPaged"]
    assert "items" in users_paged, f"Нет items в usersPaged: {json.dumps(users_paged, ensure_ascii=False)}"
    assert "totalCount" in users_paged, f"Нет totalCount в usersPaged: {json.dumps(users_paged, ensure_ascii=False)}"

    items = users_paged["items"]
    assert isinstance(items, list), "items должен быть списком"
    assert len(items) > 0, "Список пользователей пуст — пользователь 'Admin' не найден"

    # Проверяем первого пользователя (должен быть Admin)
    first_user = items[0]
    assert "userName" in first_user, f"В пользователе отсутствует поле userName: {json.dumps(first_user, ensure_ascii=False)}"
    assert "id" in first_user, f"В пользователе отсутствует поле id: {json.dumps(first_user, ensure_ascii=False)}"

    # Проверяем, что userName = 'Admin'
    assert first_user["userName"] == "Admin", (
        f"userName не равен 'Admin', получено: {first_user.get('userName')}"
    )

    # Проверяем наличие остальных обязательных полей
    expected_fields = ["id", "userName", "fullName", "email", "isEnabled", "__typename"]
    for key in expected_fields:
        assert key in first_user, f"В пользователе отсутствует поле {key}"

    # Проверяем структуру вложенных объектов (если они присутствуют)
    if "roles" in first_user and first_user["roles"]:
        role = first_user["roles"][0]
        for key in ["name", "id", "__typename"]:
            assert key in role, f"В роли отсутствует поле {key}"

    if "company" in first_user and first_user["company"]:
        company = first_user["company"]
        for key in ["id", "__typename"]:
            assert key in company, f"В компании отсутствует поле {key}"

    if "client" in first_user and first_user["client"]:
        client = first_user["client"]
        for key in ["id", "nic", "__typename"]:
            assert key in client, f"В клиенте отсутствует поле {key}"

    # Извлекаем ID пользователя
    user_id = first_user["id"]
    assert user_id, "ID пользователя пустой"

    # Для отладки первые 2 элемента
#    print(response.text)
#    print(json.dumps(items[:2], ensure_ascii=False, indent=2))
