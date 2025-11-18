import pytest

from tests.api.factories.invoicer import upload_invoice_document


# Тест проверяет загрузку документа инвойса и наличие `id` в ответе
# после успешного вызова соответствующего REST-эндпоинта.
@pytest.mark.api  # маркер для всех API-тестов
@pytest.mark.invoicer  # маркер скоупа: тесты сервиса invoicer
def test_invoice_document_upload(http, base_url, assets_dir):
    # Act: вызываем вспомогательную функцию загрузки документа инвойса
    payload = upload_invoice_document(http, base_url, assets_dir)

    # Assert: в ответе должен присутствовать идентификатор загруженного документа
    assert payload.get("id"), f"Нет id в ответе: {payload}"


