import datetime
from pathlib import Path

from tests.common.helpers import assert_has_keys, random_suffix


def upload_invoice_document(http, base_url: str, assets_dir: Path, filename: str = "Invoice.pdf") -> dict:
    """
    Фабрика для загрузки PDF-документа инвойса в сервис Invoicer.

    Args:
        http: Сессия `requests.Session` с авторизацией.
        base_url: Базовый URL API.
        assets_dir: Каталог с тестовыми файлами (PDF-документами).
        filename: Имя файла инвойса для загрузки (по умолчанию `Invoice.pdf`).

    Returns:
        dict: Описание загруженного документа с полями id, fileName, contentType и fileStoragePath.

    Raises:
        AssertionError: Если файл не найден, статус ответа не 200
            или в ответе отсутствуют ожидаемые поля.
    """
    url = f"{base_url}/api/invoicer/v2/documents"
    file_path = assets_dir / filename
    assert file_path.exists(), f"Файл {file_path} не найден"
    files = {"file": (file_path.name, file_path.read_bytes(), "application/pdf")}
    data = {"documentType": "INVOICE"}
    resp = http.post(url, files=files, data=data)
    assert resp.status_code == 200, f"unexpected status={resp.status_code} body={resp.text}"
    payload = resp.json()
    assert_has_keys(payload, ["id", "fileName", "contentType", "fileStoragePath"])
    return payload


def create_invoice(http, base_url: str, graphql, unique_suffix: str | None = None, **overrides) -> dict:
    """
    Фабрика для создания черновика инвойса через REST API Invoicer.

    Args:
        http: Сессия `requests.Session` с авторизацией.
        base_url: Базовый URL API.
        graphql: Функция/фикстура для выполнения GraphQL запросов (для получения клиента и компании).
        unique_suffix: Суффикс для уникализации номера инвойса (по умолчанию случайный).
        **overrides: Переопределения значений по умолчанию (itemCount, packingCount, grossWeight, netWeight, volume и др.).

    Returns:
        dict: Созданный инвойс с полями id, number, client и sender.

    Raises:
        AssertionError: Если создание инвойса завершилось неуспешно (статус не 200)
            или в ответе отсутствуют ожидаемые поля.
    """
    from tests.api.factories.orders import get_first_client  # local import to avoid cycles
    from tests.api.factories.company_catalog import get_first_company

    client = get_first_client(graphql)
    company = get_first_company(graphql)
    document = upload_invoice_document(http, base_url, overrides.get("assets_dir"))

    now = datetime.datetime.utcnow()
    suffix = unique_suffix or random_suffix()
    invoice_number = f"{now.strftime('%Y%m%dT%H%M%S')}-INVOICE-{suffix}"
    invoice_date = f"{now.date().isoformat()}T00:00:00.000Z"

    country = company.get("country") or {}

    payload = {
        "number": invoice_number,
        "date": invoice_date,
        "type": {"id": "INVOICE", "nameRu": "Инвойс"},
        "endCustomer": {"name": "", "country": None},
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
        "recipient": {"name": "", "country": None},
        "incoterms": None,
        "currency": {"isoCode": "EUR"},
        "sum": 100,
        "itemCount": overrides.get("itemCount", 1),
        "packingCount": overrides.get("packingCount", 1),
        "grossWeight": overrides.get("grossWeight", 1),
        "netWeight": overrides.get("netWeight", 1),
        "documents": [
            {
                "id": document["id"],
                "fileName": document["fileName"],
                # Тип документа в доменной модели
                "documentType": "INVOICE",
                # MIME-типа файла нужен фронту, чтобы корректно обрабатывать PDF
                "contentType": document["contentType"],
                "fileStoragePath": document["fileStoragePath"],
            }
        ],
        "orders": [],
        "wayBills": [],
        "citeses": [],
        "exportDeclarations": [],
        "inEdit": True,
        "volume": overrides.get("volume", 1),
        "client": {
            "nic": client["nic"],
            "id": client["id"],
            "__typename": client["__typename"],
        },
    }

    url = f"{base_url}/api/invoicer/invoices/"
    resp = http.post(url, json=payload, headers={"Content-Type": "application/json"})
    assert resp.status_code == 200, f"unexpected status={resp.status_code} body={resp.text}"
    invoice = resp.json()
    assert_has_keys(invoice, ["id", "number", "client", "sender"])
    return invoice


