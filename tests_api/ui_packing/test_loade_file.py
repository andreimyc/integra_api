import os
import json
from pathlib import Path

import requests


def test_invoice_document_upload(auth_token):
    base_url = os.getenv("BASE_URL", "").rstrip("/")
    assert base_url, "BASE_URL пустой — проверь .env"

    url = f"{base_url}/api/invoicer/v2/documents"

    asset_path = Path(__file__).resolve().parents[2] / "file" / "Invoice.pdf"
    assert asset_path.exists(), f"Файл {asset_path} не найден"

    pdf_bytes = asset_path.read_bytes()
    filename = asset_path.name

    files = {
        "file": (filename, pdf_bytes, "application/pdf"),
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

    # Проверяем обязательные поля ответа
    for key in ("id", "fileName", "contentType", "fileStoragePath"):
        assert key in payload, (
            f"В ответе отсутствует поле {key}: {json.dumps(payload, ensure_ascii=False)}"
        )

    # Для отладки
#    print(response.text)