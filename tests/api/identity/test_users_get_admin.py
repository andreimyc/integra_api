import pytest

from tests.common.helpers import assert_has_keys


# Тест проверяет, что GraphQL-эндпоинт `usersPaged` возвращает пользователя Admin
# с ожидаемым набором полей и корректными вложенными объектами `roles`, `company`, `client`.
@pytest.mark.api  # маркер для всех API-тестов
@pytest.mark.identity  # маркер скоупа: тесты сервиса identity
def test_get_admin_user(graphql):
    # Arrange: формируем GraphQL-запрос и параметры фильтрации по пользователю Admin
    query = """
    query getCreatedUsers($skip: Int, $take: Int, $where: UserModelFilterInput, $order: [UserModelSortInput!]) {
      usersPaged(skip: $skip, take: $take, where: $where, order: $order) {
        totalCount
        items {
          id
          userName
          fullName
          email
          telegramUserName
          roles { name id __typename }
          company { id nameEn nameRu __typename }
          client { id nic __typename }
          isEnabled
          __typename
        }
        __typename
      }
    }
    """
    variables = {
        "skip": 0,
        "take": 100,
        "where": {"and": [{"or": [{"userName": {"contains": "Admin"}}]}]},
        "order": [],
    }

    # Act: выполняем запрос к GraphQL-эндпоинту identity
    data = graphql("/api/identity/graphql", query, variables)
    paged = (data.get("data") or {}).get("usersPaged") or {}
    items = paged.get("items") or []

    # Assert: убеждаемся, что пользователь Admin найден и структура его данных корректна
    assert items, "Список пользователей пуст — пользователь 'Admin' не найден"
    first = items[0]
    assert first.get("userName") == "Admin", f"userName не равен 'Admin', получено: {first.get('userName')}"

    # Проверяем наличие ключевых полей у пользователя
    for key in ["id", "userName", "fullName", "email", "isEnabled", "__typename"]:
        assert key in first, f"В пользователе отсутствует поле {key}"

    # При наличии ролей проверяем структуру первой роли
    if first.get("roles"):
        assert_has_keys(first["roles"][0], ["name", "id", "__typename"])

    # При наличии компании проверяем её структуру
    if first.get("company"):
        assert_has_keys(first["company"], ["id", "__typename"])

    # При наличии клиента проверяем его структуру
    if first.get("client"):
        assert_has_keys(first["client"], ["id", "nic", "__typename"])


