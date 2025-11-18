import pytest

from tests.api.factories.identity import get_admin_user_id
from tests.api.factories.invoicer import create_invoice


# Тест проверяет, что несколько инвойсов можно назначить одному упаковщику
# через batch-эндпоинт `assign-to-user` сервиса invoicer.
@pytest.mark.api  # маркер для всех API-тестов
@pytest.mark.invoicer  # маркер скоупа: тесты сервиса invoicer
def test_assign_packer_to_multiple_invoices(http, base_url, graphql, assets_dir):
    # Arrange: создаём два инвойса и получаем id пользователя-упаковщика (Admin)
    invoice_id_1 = create_invoice(http, base_url, graphql, unique_suffix="A", assets_dir=assets_dir)["id"]
    invoice_id_2 = create_invoice(http, base_url, graphql, unique_suffix="B", assets_dir=assets_dir)["id"]
    user_id = get_admin_user_id(graphql)

    url = f"{base_url}/api/invoicer/invoices/batch/packing/assign-to-user"
    payload = {"invoicesIds": [invoice_id_1, invoice_id_2], "userId": user_id}

    # Act: вызываем REST-эндпоинт назначения упаковщика
    resp = http.post(url, json=payload, headers={"Content-Type": "application/json"})

    # Assert: проверяем успешный статус ответа
    assert resp.status_code == 200, f"unexpected status={resp.status_code} body={resp.text}"


