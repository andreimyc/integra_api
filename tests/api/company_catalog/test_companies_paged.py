import pytest

from tests.common.helpers import assert_has_keys


# Тест проверяет, что GraphQL-эндпоинт `companiesPaged` возвращает список компаний
# с ожидаемым набором полей как у самой компании, так и у вложенной страны.
@pytest.mark.api  # маркер для всех API-тестов
@pytest.mark.company_catalog  # маркер скоупа: тесты каталога компаний
def test_companies_paged(graphql):
    # Arrange: формируем GraphQL-запрос и фильтры
    query = """
    query getLegalEntities($where: CompanyDtoFilterInput, $order: [CompanyDtoSortInput!]) {
      companiesPaged(where: $where, order: $order) {
        items {
          id
          eori
          vat
          name
          country {
            alpha2: id
            id
            name
            __typename
          }
          __typename
        }
        __typename
      }
    }
    """
    variables = {"where": {"and": [{"isValid": {"eq": True}}]}}

    # Act: выполняем запрос к GraphQL-эндпоинту каталога компаний
    data = graphql("/api/company-catalog/graphql", query, variables)

    # Assert: базовая валидация структуры ответа
    assert "data" in data, f"Нет поля data в ответе: {data}"
    paged = data["data"].get("companiesPaged") or {}
    items = paged.get("items")
    assert isinstance(items, list), "items должен быть списком"

    # При наличии элементов дополнительно проверяем ключевые поля первой компании
    if items:
        first = items[0]
        assert_has_keys(first, ["id", "eori", "vat", "name", "__typename"])

        # Если у компании указана страна, проверяем структуру объекта `country`
        if first.get("country"):
            assert_has_keys(first["country"], ["id", "name", "alpha2", "__typename"])


