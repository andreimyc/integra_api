import pytest

from tests.api.factories.invoicer import create_invoice
from tests.common.helpers import assert_has_keys


# Тест проверяет создание инвойса в разных сценариях (параметризованные кейсы)
# и базовую структуру ответа: наличие ключевых полей и заполненного клиента.
@pytest.mark.api  # маркер для всех API-тестов
@pytest.mark.invoicer  # маркер скоупа: тесты сервиса invoicer
@pytest.mark.parametrize(
    "case",
    [
        {"suffix": "1AM", "itemCount": 2, "packingCount": 3, "grossWeight": 4, "netWeight": 8, "volume": 6},
        {"suffix": "2AM", "itemCount": 2, "packingCount": 2, "grossWeight": 4, "netWeight": 8, "volume": 6},
    ],
    ids=["invoice_case_1", "invoice_case_2"],
)
def test_create_invoice(http, base_url, graphql, assets_dir, case):
    # Arrange & Act: создаём инвойс через вспомогательную фабрику с параметрами кейса
    invoice = create_invoice(
        http,
        base_url,
        graphql,
        unique_suffix=case["suffix"],
        assets_dir=assets_dir,
        itemCount=case["itemCount"],
        packingCount=case["packingCount"],
        grossWeight=case["grossWeight"],
        netWeight=case["netWeight"],
        volume=case["volume"],
    )

    # Assert: проверяем наличие ключевых полей и заполненность клиента
    assert_has_keys(invoice, ["id", "number", "client", "sender"])
    assert invoice["client"].get("id"), "Клиент в ответе не заполнен"


