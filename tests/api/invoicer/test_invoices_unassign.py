import pytest

from tests.api.factories.identity import get_admin_user_id
from tests.api.factories.invoicer import create_invoice


# Тест проверяет, что ранее назначенного упаковщика можно снять с нескольких инвойсов
# через тот же batch-эндпоинт `assign-to-user`, передавая `userId=None`.
@pytest.mark.api  # маркер для всех API-тестов
@pytest.mark.invoicer  # маркер скоупа: тесты сервиса invoicer
def test_unassign_packer_from_multiple_invoices(http, base_url, graphql, assets_dir):
    # Arrange: создаём два инвойса и получаем id пользователя-упаковщика (Admin)
    invoice_id_1 = create_invoice(http, base_url, graphql, unique_suffix="UA", assets_dir=assets_dir)["id"]
    invoice_id_2 = create_invoice(http, base_url, graphql, unique_suffix="UB", assets_dir=assets_dir)["id"]
    user_id = get_admin_user_id(graphql)

    assign_url = f"{base_url}/api/invoicer/invoices/batch/packing/assign-to-user"
    assign_payload = {"invoicesIds": [invoice_id_1, invoice_id_2], "userId": user_id}

    # Act: сначала назначаем упаковщика на инвойсы
    assign_resp = http.post(assign_url, json=assign_payload, headers={"Content-Type": "application/json"})
    assert assign_resp.status_code == 200, f"Назначение не удалось: status={assign_resp.status_code} body={assign_resp.text}"

    # Act: затем снимаем назначение, передавая userId=None
    unassign_payload = {"invoicesIds": [invoice_id_1, invoice_id_2], "userId": None}
    unassign_resp = http.post(assign_url, json=unassign_payload, headers={"Content-Type": "application/json"})

    # Assert: проверяем успешный статус ответа при отвязке упаковщика
    assert unassign_resp.status_code == 200, f"unexpected status={unassign_resp.status_code} body={unassign_resp.text}"


