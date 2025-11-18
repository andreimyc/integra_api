[clients] Получить данные для поля Клиент

https://{{URL}}/api/orders/graphql

query getAllClients($where: ClientFilterInput, $order: [ClientSortInput!]) {
  clients(where: $where, order: $order) {
    nic
    id
    __typename
  }
}

{}

let response = pm.response.json();

let firstCompany = response.data.clients[0];

pm.environment.set("CLIENT_NIC", firstCompany.nic);
pm.environment.set("CLIENT_ID", firstCompany.id);
pm.environment.set("CLIENT_TYPENAME", firstCompany.__typename);

pm.test("Status code is 200", function () {
    pm.response.to.have.status(200);
});