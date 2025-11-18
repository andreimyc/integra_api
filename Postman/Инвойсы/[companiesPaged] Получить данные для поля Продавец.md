[companiesPaged] Получить данные для поля "Продавец"

https://{{URL}}/api/company-catalog/graphql

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

{
  "where": {
    "and": [
      {
        "isValid": {
          "eq": true
        }
      }
    ]
  }
}

let response = pm.response.json();

let firstCompany = response.data.companiesPaged.items[0];

pm.environment.set("COMPANY_ID", firstCompany.id);
pm.environment.set("COMPANY_EORI", firstCompany.eori ?? "null");
pm.environment.set("COMPANY_VAT", firstCompany.vat);
pm.environment.set("COMPANY_NAME", firstCompany.name);
pm.environment.set("COMPANY_COUNTRY_ALPHA2", firstCompany.country.alpha2);
pm.environment.set("COMPANY_COUNTRY_ID", firstCompany.country.id);
pm.environment.set("COMPANY_COUNTRY_NAME", firstCompany.country.name);
pm.environment.set("COMPANY_COUNTRY_TYPENAME", firstCompany.country.__typename);

pm.test("Status code is 200", function () {
    pm.response.to.have.status(200);
});