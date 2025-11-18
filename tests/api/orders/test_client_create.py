import pytest

from tests.api.factories.orders import create_client
from tests.common.helpers import assert_has_keys


# Тест проверяет создание клиента через REST API заказов
# и базовую структуру ответа, включая формат NIC и опциональный блок company.
@pytest.mark.api  # маркер для всех API-тестов
@pytest.mark.orders  # маркер скоупа: тесты сервиса orders
def test_create_client(http, base_url, graphql):
    # Arrange & Act: создаём клиента через фабрику с уникальным суффиксом
    client = create_client(http, base_url, graphql, unique_suffix="AM")

    # Assert: проверка обязательных полей
    assert_has_keys(client, ["id", "nic", "createdDate"])

    # Проверка структуры ответа
    assert client.get("id"), "ID клиента отсутствует"
    assert client.get("nic"), "NIC клиента отсутствует"
    assert client.get("createdDate"), "Дата создания отсутствует"

    # Проверка формата имени клиента (должно содержать ISO timestamp и '-CLIENT-')
    nic = client["nic"]
    assert "-CLIENT-" in nic, f"Неверный формат NIC: {nic}"
    assert nic.endswith("-CLIENT-AM"), f"NIC должен заканчиваться на '-CLIENT-AM': {nic}"

    # Проверка наличия company в ответе (если возвращается)
    if "company" in client:
        assert client["company"].get("id"), "ID компании в ответе не заполнен"
        assert_has_keys(client["company"], ["id", "nameEn", "nameRu"])

