import os
import requests
import json


def test_clients(auth_token):
    base_url = os.getenv("BASE_URL", "").rstrip("/")
    assert base_url, "BASE_URL пустой — проверь .env"

    url = f"{base_url}/api/orders/graphql"

    query = """
    query getAllClients($where: ClientFilterInput, $order: [ClientSortInput!]) {
      clients(where: $where, order: $order) {
        nic
        id
        __typename
      }
    }
    """

    variables = {}

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
    assert "clients" in data["data"], f"Нет clients: {json.dumps(data, ensure_ascii=False)}"

    clients = data["data"]["clients"]
    assert isinstance(clients, list), "clients должен быть списком"

    # Если список не пуст — проверим поля первого элемента
    if clients:
        first = clients[0]
        for key in ["nic", "id", "__typename"]:
            assert key in first, f"В клиенте отсутствует поле {key}"

    # Для отладки первые 2 элемента
#    print(response.text)
#    print(json.dumps(clients[:2], ensure_ascii=False, indent=2))
