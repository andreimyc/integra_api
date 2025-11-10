import datetime
import json
import os
from pathlib import Path

import requests


def _load_first_client(base_url: str, auth_token: str) -> dict:
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

    payload = {"query": query, "variables": {}}
    headers = {
        "Cookie": f"JWT={auth_token};",
        "Content-Type": "application/json",
    }

    response = requests.post(url, json=payload, headers=headers)
    assert response.status_code == 200, (
        f"unexpected status={response.status_code} body={response.text}"
    )

    data = response.json()
    assert "data" in data and "clients" in data["data"], (
        f"Некорректный ответ на clients: {json.dumps(data, ensure_ascii=False)}"
    )

    clients = data["data"]["clients"]
    assert clients, "Список клиентов пуст"

    first = clients[0]
    for key in ("nic", "id", "__typename"):
        assert key in first, f"В клиенте отсутствует поле {key}"

    return first


def _load_first_company(base_url: str, auth_token: str) -> dict:
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
    assert response.status_code == 200, (
        f"unexpected status={response.status_code} body={response.text}"
    )

    data = response.json()
    assert (
        "data" in data
        and "companiesPaged" in data["data"]
        and "items" in data["data"]["companiesPaged"]
    ), f"Некорректный ответ на companiesPaged: {json.dumps(data, ensure_ascii=False)}"

    items = data["data"]["companiesPaged"]["items"]
    assert items, "Список компаний пуст"

    first = items[0]
    for key in ("id", "name", "vat", "__typename"):
        assert key in first, f"В компании отсутствует поле {key}"

    country = first.get("country") or {}
    for key in ("id", "name", "alpha2", "__typename"):
        assert key in country, f"В стране отсутствует поле {key}"

    return first


def _upload_invoice_document(base_url: str, auth_token: str) -> dict:
    url = f"{base_url}/api/invoicer/v2/documents"

    asset_path = Path(__file__).resolve().parents[2] / "file" / "Invoice.pdf"
    assert asset_path.exists(), f"Файл {asset_path} не найден"

    files = {
        "file": (asset_path.name, asset_path.read_bytes(), "application/pdf"),
    }
    data = {"documentType": "INVOICE"}
    headers = {
        "Cookie": f"JWT={auth_token};",
    }

    response = requests.post(url, files=files, data=data, headers=headers)
    assert response.status_code == 200, (
        f"unexpected status={response.status_code} body={response.text}"
    )

    payload = response.json()
    for key in ("id", "fileName", "contentType", "fileStoragePath"):
        assert key in payload, (
            f"В ответе отсутствует поле {key}: {json.dumps(payload, ensure_ascii=False)}"
        )

    return payload


def _create_invoice_and_return_id(base_url: str, auth_token: str, number_suffix: str) -> str:
    client = _load_first_client(base_url, auth_token)
    company = _load_first_company(base_url, auth_token)
    document = _upload_invoice_document(base_url, auth_token)

    now = datetime.datetime.utcnow()
    invoice_number = f"{now.strftime('%Y%m%dT%H%M%S')}-UNASSIGN-{number_suffix}"
    invoice_date = f"{now.date().isoformat()}T00:00:00.000Z"

    country = (company.get("country") or {})

    payload = {
        "number": invoice_number,
        "date": invoice_date,
        "type": {
            "id": "INVOICE",
            "nameRu": "Инвойс",
        },
        "endCustomer": {
            "name": "",
            "country": None,
        },
        "sender": {
            "name": "",
            "country": {
                "alpha2": country.get("alpha2"),
                "id": country.get("id"),
                "name": country.get("name"),
                "__typename": country.get("__typename"),
                "nameRu": country.get("name"),
                "nameEn": country.get("name"),
            },
            "company": {
                "eori": company.get("eori"),
                "id": company.get("id"),
                "name": company.get("name"),
                "vat": company.get("vat"),
            },
        },
        "recipient": {
            "name": "",
            "country": None,
        },
        "incoterms": None,
        "currency": {
            "isoCode": "EUR",
        },
        "sum": 100,
        "itemCount": 1,
        "packingCount": 1,
        "grossWeight": 1,
        "netWeight": 1,
        "documents": [
            {
                "id": document["id"],
                "fileName": document["fileName"],
                "documentType": document["contentType"],
                "fileStoragePath": document["fileStoragePath"],
            }
        ],
        "orders": [],
        "wayBills": [],
        "citeses": [],
        "exportDeclarations": [],
        "inEdit": True,
        "volume": 1,
        "client": {
            "nic": client["nic"],
            "id": client["id"],
            "__typename": client["__typename"],
        },
    }

    url = f"{base_url}/api/invoicer/invoices/"
    headers = {
        "Cookie": f"JWT={auth_token};",
        "Content-Type": "application/json",
    }

    response = requests.post(url, json=payload, headers=headers)
    assert response.status_code == 200, (
        f"unexpected status={response.status_code} body={response.text}"
    )

    invoice = response.json()
    assert "id" in invoice, f"В ответе invoice отсутствует поле id: {json.dumps(invoice, ensure_ascii=False)}"
    return invoice["id"]


def _get_admin_user_id(base_url: str, auth_token: str) -> str:
    url = f"{base_url}/api/identity/graphql"
    query = """
    query getCreatedUsers($skip: Int, $take: Int, $where: UserModelFilterInput, $order: [UserModelSortInput!]) {
      usersPaged(skip: $skip, take: $take, where: $where, order: $order) {
        items {
          id
          userName
        }
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
    users = ((data.get("data") or {}).get("usersPaged") or {}).get("items") or []
    assert users, f"Пользователь Admin не найден: {json.dumps(data, ensure_ascii=False)}"
    assert users[0].get("id"), f"У Admin отсутствует id: {json.dumps(users[0], ensure_ascii=False)}"
    return users[0]["id"]


def test_unassign_packer_from_multiple_invoices(auth_token):
    base_url = os.getenv("BASE_URL", "").rstrip("/")
    assert base_url, "BASE_URL пустой — проверь .env"

    # Подготавливаем данные: создаём 2 инвойса и получаем id пользователя (Admin)
    invoice_id_1 = _create_invoice_and_return_id(base_url, auth_token, "A")
    invoice_id_2 = _create_invoice_and_return_id(base_url, auth_token, "B")
    user_id = _get_admin_user_id(base_url, auth_token)

    # Назначаем пакингиста (Admin) для проверки, что сброс работает после назначения
    assign_url = f"{base_url}/api/invoicer/invoices/batch/packing/assign-to-user"
    assign_payload = {
        "invoicesIds": [
            invoice_id_1,
            invoice_id_2,
        ],
        "userId": user_id,
    }
    headers = {
        "Cookie": f"JWT={auth_token};",
        "Content-Type": "application/json",
    }
    assign_response = requests.post(assign_url, json=assign_payload, headers=headers)
    assert assign_response.status_code == 200, (
        f"Назначение не удалось: status={assign_response.status_code} body={assign_response.text}"
    )

    # Сбрасываем назначение пакингиста с нескольких инвойсов (userId = null)
    unassign_payload = {
        "invoicesIds": [
            invoice_id_1,
            invoice_id_2,
        ],
        "userId": None,
    }
    unassign_response = requests.post(assign_url, json=unassign_payload, headers=headers)

    # Ожидаем status code 200
    assert unassign_response.status_code == 200, (
        f"unexpected status={unassign_response.status_code} body={unassign_response.text}"
    )


