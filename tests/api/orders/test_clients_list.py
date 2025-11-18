import pytest

from tests.common.helpers import assert_has_keys


# Тест проверяет, что GraphQL-эндпоинт `clients` сервиса orders
# возвращает список клиентов с ожидаемым набором полей.
@pytest.mark.api  # маркер для всех API-тестов
@pytest.mark.orders  # маркер скоупа: тесты сервиса orders
def test_clients_list(graphql):
    # Arrange: формируем GraphQL-запрос
    query = """
    query getAllClients($where: ClientFilterInput, $order: [ClientSortInput!]) {
      clients(where: $where, order: $order) {
        nic
        id
        __typename
      }
    }
    """

    # Act: выполняем запрос к GraphQL-эндпоинту orders
    data = graphql("/api/orders/graphql", query, {})

    # Assert: базовая проверка структуры и содержимого списка клиентов
    assert "data" in data, f"Нет поля data в ответе: {data}"
    clients = (data["data"].get("clients")) or []
    assert isinstance(clients, list), "clients должен быть списком"

    # При наличии элементов проверяем структуру первого клиента
    if clients:
        assert_has_keys(clients[0], ["nic", "id", "__typename"])

