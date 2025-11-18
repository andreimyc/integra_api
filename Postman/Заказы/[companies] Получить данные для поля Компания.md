https://{{URL}}/api/orders/graphql

query companies($where: CompanyFilterInput, $order: [CompanySortInput!]) {
  companies(where: $where, order: $order) {
    id
    nameEn
    nameRu
    __typename
  }
}

{
  "where": {},
  "order": []
}

let response = pm.response.json();

let firstCompany = response.data.companies[0];

pm.environment.set("COMPANY_ID", firstCompany.id);
pm.environment.set("COMPANY_NAME_EN", firstCompany.nameEn);
pm.environment.set("COMPANY_NAME_RU", firstCompany.nameRu);
pm.environment.set("COMPANY_TYPENAME", firstCompany.__typename);

pm.test("Status code is 200", function () {
    pm.response.to.have.status(200);
});