from tests.common.helpers import assert_has_keys


def get_first_company(graphql) -> dict:
    """
    Фабрика для получения первой валидной компании из справочника Company Catalog.

    Args:
        graphql: Функция/фикстура для выполнения GraphQL запросов.

    Returns:
        dict: Описание компании с полями id, name, vat, __typename и вложенным объектом country.

    Raises:
        AssertionError: Если список компаний пуст или у компании/страны нет ожидаемых полей.
    """
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
    variables = {"where": {"and": [{"isValid": {"eq": True}}]}}  # noqa: E712
    data = graphql("/api/company-catalog/graphql", query, variables)
    items = ((data.get("data") or {}).get("companiesPaged") or {}).get("items") or []
    assert items, f"Список компаний пуст: {data}"
    first = items[0]
    assert_has_keys(first, ["id", "name", "vat", "__typename"])
    country = first.get("country") or {}
    assert_has_keys(country, ["id", "name", "alpha2", "__typename"])
    return first


