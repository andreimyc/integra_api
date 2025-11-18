https://{{URL}}/api/identity/graphql

query getCreatedUsers($skip: Int, $take: Int, $where: UserModelFilterInput, $order: [UserModelSortInput!]) {
  usersPaged(skip: $skip, take: $take, where: $where, order: $order) {
    totalCount
    items {
      id
      userName
      fullName
      email
      telegramUserName
      roles {
        name
        id
        __typename
      }
      company {
        id
        nameEn
        nameRu
        __typename
      }
      client {
        id
        nic
        __typename
      }
      isEnabled
      __typename
    }
    __typename
  }
}

{
  "skip": 0,
  "take": 100,
  "where": {
    "and": [
      {
        "or": [
          {
            "userName": {
              "contains": "{{USER_NAME_IS_ROLE}}"
            }
          }
        ]
      }
    ]
  },
  "order": []
}

let response = pm.response.json();

pm.test("Проверить, что userName = 'Admin'", function () {
    pm.expect(response.data.usersPaged.items[0].userName).to.eql("Admin");
});

if (response.data.usersPaged.items[0].userName === "Admin") {
    let userId = response.data.usersPaged.items[0].id;
    pm.environment.set("USER_ID_IS_ROLE", userId);
    console.log("ID сохранён в переменную окружения:", userId);
} else {
    console.warn("userName не равен 'Admin', переменная не сохранена");
}
