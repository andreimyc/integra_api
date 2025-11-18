import datetime

from tests.common.helpers import assert_has_keys


def get_first_client(graphql) -> dict:
    """
    Фабрика для получения первого доступного клиента через GraphQL API.

    Args:
        graphql: Функция/фикстура для выполнения GraphQL запросов.

    Returns:
        dict: Первый клиент из списка с полями nic, id и __typename.

    Raises:
        AssertionError: Если список клиентов пуст или у клиента нет ожидаемых полей.
    """
    query = """
    query getAllClients($where: ClientFilterInput, $order: [ClientSortInput!]) {
      clients(where: $where, order: $order) {
        nic
        id
        __typename
      }
    }
    """
    data = graphql("/api/orders/graphql", query, {})
    clients = (data.get("data") or {}).get("clients") or []
    assert clients, f"Список клиентов пуст: {data}"
    first = clients[0]
    assert_has_keys(first, ["nic", "id", "__typename"])
    return first


def get_first_company(graphql) -> dict:
    """
    Фабрика для получения первой доступной компании через GraphQL API.

    Args:
        graphql: Функция/фикстура для выполнения GraphQL запросов.

    Returns:
        dict: Первая компания из списка с полями id, nameEn, nameRu и __typename.

    Raises:
        AssertionError: Если список компаний пуст или у компании нет ожидаемых полей.
    """
    query = """
    query companies($where: CompanyFilterInput, $order: [CompanySortInput!]) {
      companies(where: $where, order: $order) {
        id
        nameEn
        nameRu
        __typename
      }
    }
    """
    variables = {
        "where": {},
        "order": []
    }
    data = graphql("/api/orders/graphql", query, variables)
    companies = (data.get("data") or {}).get("companies") or []
    assert companies, f"Список компаний пуст: {data}"
    first = companies[0]
    assert_has_keys(first, ["id", "nameEn", "nameRu", "__typename"])
    return first


def create_client(http, base_url: str, graphql, unique_suffix: str | None = None, **overrides) -> dict:
    """
    Фабрика для создания клиента через REST API.
    
    Args:
        http: Сессия requests.Session с авторизацией
        base_url: Базовый URL API
        graphql: Функция для выполнения GraphQL запросов
        unique_suffix: Суффикс для уникальности имени клиента (по умолчанию "AM")
        **overrides: Параметры для переопределения дефолтных значений (tariff, printMark и т.д.)
    
    Returns:
        dict: Созданный клиент с полями id, nic, createdDate и др.
    """
    company = get_first_company(graphql)
    
    # Генерация уникального имени клиента
    # Формат: ISO timestamp с миллисекундами и Z (например: 2025-10-17T14:35:08.123Z)
    now = datetime.datetime.utcnow()
    iso_timestamp = now.isoformat(timespec="milliseconds") + "Z"
    suffix = unique_suffix or "AM"
    client_nic = f"{iso_timestamp}-CLIENT-{suffix}"
    
    # Тариф по умолчанию
    default_tariff = {
        "t1Price": 35,
        "exPrice": None,
        "deliveryPrice": 0,
        "pickUpPrice": 3010,
        "insurance": 0,
        "tariffPerKg": 11,
        "tapePrice": 3,
        "citesPrice": 140,
        "controlMarkFursPrice": 150,
        "controlMarkSheepskinsPrice": 100,
    }
    
    # Формирование payload
    payload = {
        "nic": client_nic,
        "company": {
            "id": company["id"],
            "nameEn": company["nameEn"],
            "nameRu": company["nameRu"],
            "__typename": company["__typename"],
        },
        "tariff": overrides.get("tariff", default_tariff),
        "printMark": overrides.get("printMark", False),
        "partnerWarehouses": overrides.get("partnerWarehouses", []),
        "partnerCompanies": overrides.get("partnerCompanies", []),
        "tags": overrides.get("tags", []),
        "clientCodes": overrides.get("clientCodes", None),
        "clientCompanies": overrides.get("clientCompanies", None),
        "clientTransits": overrides.get("clientTransits", None),
        "contactInfos": overrides.get("contactInfos", None),
    }
    
    # Отправка POST запроса
    url = f"{base_url}/api/orders/v1/Client"
    resp = http.post(url, json=payload, headers={"Content-Type": "application/json"})
    assert resp.status_code == 200, f"unexpected status={resp.status_code} body={resp.text}"
    
    client = resp.json()
    assert_has_keys(client, ["id", "nic", "createdDate"])
    return client
