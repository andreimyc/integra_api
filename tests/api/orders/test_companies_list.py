import pytest

from tests.common.helpers import assert_has_keys


# Тест проверяет, что GraphQL-эндпоинт `companies` сервиса orders
# возвращает список компаний с ожидаемым набором полей.
@pytest.mark.api  # маркер для всех API-тестов
@pytest.mark.orders  # маркер скоупа: тесты сервиса orders
def test_companies_list(graphql):
    # Arrange: формируем GraphQL-запрос и параметры
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

    # Act: выполняем запрос к GraphQL-эндпоинту orders
    data = graphql("/api/orders/graphql", query, variables)

    # Assert: базовая проверка структуры и содержимого списка компаний
    assert "data" in data, f"Нет поля data в ответе: {data}"
    companies = data["data"].get("companies") or []
    assert isinstance(companies, list), "companies должен быть списком"

    # При наличии элементов проверяем структуру первой компании
    if companies:
        first_company = companies[0]
        assert_has_keys(first_company, ["id", "nameEn", "nameRu", "__typename"])

