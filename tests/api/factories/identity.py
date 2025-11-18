def get_admin_user_id(graphql) -> str:
    """
    Фабрика для получения идентификатора пользователя-администратора через GraphQL API Identity.

    Args:
        graphql: Функция/фикстура для выполнения GraphQL запросов.

    Returns:
        str: Идентификатор (id) первого найденного пользователя, у которого имя содержит 'Admin'.

    Raises:
        AssertionError: Если пользователь Admin не найден или у него отсутствует поле id.
    """
    query = """
    query getCreatedUsers($skip: Int, $take: Int, $where: UserModelFilterInput, $order: [UserModelSortInput!]) {
      usersPaged(skip: $skip, take: $take, where: $where, order: $order) {
        items {
          id
          userName
        }
      }
    }
    """
    variables = {
        "skip": 0,
        "take": 100,
        "where": {"and": [{"or": [{"userName": {"contains": "Admin"}}]}]},
        "order": [],
    }
    data = graphql("/api/identity/graphql", query, variables)
    users = ((data.get("data") or {}).get("usersPaged") or {}).get("items") or []
    assert users, f"Пользователь Admin не найден: {data}"
    admin_id = users[0].get("id")
    assert admin_id, f"У Admin отсутствует id: {users[0]}"
    return admin_id


