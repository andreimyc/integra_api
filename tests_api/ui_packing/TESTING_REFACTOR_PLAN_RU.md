## План рефакторинга тестов: сделать независимыми и структурированными

Ниже перечислены пошаговые действия, как привести ваши тесты к хорошим практикам: независимость, предсказуемость, читаемая структура и повторное использование общих частей. На этом этапе код не меняем — это план внедрения.


### Цели
- Каждый тест самодостаточен и не зависит от запуска других тестов.
- Общая подготовка/фикстуры/клиенты — переиспользуемые и отделены от тестов.
- Ясная структура директорий по доменам API.
- Чёткие правила именования, меток и конфигурации.


### Рекомендуемая структура

```
tests/
  api/
    conftest.py                # общие фикстуры: BASE_URL, auth_token, http/graphQL клиенты, фабрики
    pytest.ini                  # конфигурация pytest (или в корне репозитория)

    clients/                    # домен orders → clients GraphQL
      test_clients_list.py

    company_catalog/            # домен company-catalog
      test_companies_paged.py

    invoicer/                   # домен invoicer
      test_invoices_create.py
      test_invoices_assign.py
      test_invoices_unassign.py

    identity/                   # домен identity
      test_users_get_admin.py

    assets/                     # тестовые артефакты
      Invoice.pdf

    factories/                  # фабрики/билдеры данных (create_invoice, get_first_client, get_company и т.д.)
      __init__.py
      invoicer.py
      orders.py
      company_catalog.py
      identity.py

  common/
    helpers.py                  # утилиты, генерация уникальных значений, валидация схем и пр.
```

Примечания:
- `pytest.ini` можно хранить в корне репозитория. Если он уже есть — дополним.
- Активы (например, `Invoice.pdf`) переносим в `tests/api/assets/` и используем через фикстуру пути.


### Базовые правила
- Тесты не должны зависеть от порядка выполнения и результатов других тестов.
- Любая подготовка данных — внутри самого теста или через фикстуру с `scope="function"`.
- Если объект должен существовать для теста (например, инвойс) — создавайте его в фикстуре/фабрике и удаляйте в финалайзере (если API поддерживает удаление).
- Никакой «предпрогоночной» подгонки через отдельные тесты-подготовители.


### Конфигурация pytest (пример)

```ini
# pytest.ini
[pytest]
testpaths = tests
addopts = -q
markers =
    api: API-тесты
    invoicer: тесты сервиса invoicer
    identity: тесты сервиса identity
    orders: тесты сервиса orders
    company_catalog: тесты сервиса company-catalog
```


### Шаг № 1. Создайте директорию `tests/api` и подпапки по доменам
- Создайте `tests/api/clients`, `tests/api/company_catalog`, `tests/api/invoicer`, `tests/api/identity`, `tests/api/assets`, `tests/api/factories`, `tests/common`.
- Скопируйте `file/Invoice.pdf` в `tests/api/assets/Invoice.pdf` (исходный файл пока не удаляйте до полной миграции).


### Шаг № 2. Вынесите общие фикстуры в `tests/api/conftest.py`
- Фикстуры: `base_url` (читает `BASE_URL` из окружения и нормализует), `auth_token` (как у вас уже есть), `assets_dir` (путь к `tests/api/assets`), `http` (сессия `requests.Session()` с заголовками/куки), `graphql` (утилита для GraphQL POST).
- Все тесты должны использовать эти фикстуры вместо ручной сборки URL/заголовков.


### Шаг № 3. Создайте фабрики данных в `tests/api/factories`
- `orders.py`: `get_first_client(graphql)` — возвращает клиента, без кэширования глобального состояния.
- `company_catalog.py`: `get_first_company(graphql)` — возвращает валидную компанию.
- `invoicer.py`: 
  - `upload_invoice_document(http, assets_dir)` — загружает `Invoice.pdf`, возвращает JSON ответа;
  - `create_invoice(http, base_url, graphql, unique_suffix)` — создаёт инвойс с уникальным номером и возвращает JSON.
- `identity.py`: `get_admin_user_id(graphql)` — возвращает `id` пользователя Admin.

Замечание: фабрики могут принимать параметры для гибкости (валюта, веса, количество упаковок и т.д.), но должны иметь разумные дефолты.


### Шаг № 4. Обновите тесты на использование фабрик и фикстур
- Перенесите тесты в соответствующие доменные каталоги и переименуйте файлы:
  - `tests_api/ui_packing/test_clients.py` → `tests/api/clients/test_clients_list.py`
  - `tests_api/ui_packing/test_companies_paged.py` → `tests/api/company_catalog/test_companies_paged.py`
  - `tests_api/ui_packing/test_loade_file.py` → `tests/api/invoicer/test_invoices_upload_document.py` (или объедините в `test_invoices_create.py` как часть сценария)
  - `tests_api/ui_packing/test_create_invoice_1.py` и `..._2.py` → объедините в `tests/api/invoicer/test_invoices_create.py` с параметризацией
  - `tests_api/ui_packing/test_get_admin_user.py` → `tests/api/identity/test_users_get_admin.py`
  - `tests_api/ui_packing/test_assign_packer_to_invoices.py` → `tests/api/invoicer/test_invoices_assign.py`
  - `tests_api/ui_packing/test_unassign_packer_from_invoices.py` → `tests/api/invoicer/test_invoices_unassign.py`


### Шаг № 5. Сделайте тесты независимыми
- Каждый тест сценария «назначить/снять пакингиста» должен сам создать 1-2 инвойса через фабрику `create_invoice`, затем выполнить действие и проверить результат.
- Не опирайтесь на существование пользователей/компаний/клиентов, кроме явно читаемых через фабрики-ридеры (они сами проверят наличие и дадут понятную ошибку).
- Там, где это возможно, используйте `function`-scope фикстуры, создающие и возвращающие подготовленные данные только для конкретного теста.


### Шаг № 6. Параметризуйте сходные кейсы вместо копирования тестов
- `test_create_invoice_1.py` и `test_create_invoice_2.py` объедините как один тест с `@pytest.mark.parametrize`, различая параметры (например, `packingCount`, `number_suffix`).


### Шаг № 7. Сделайте тестовые номера и имена уникальными
- Генерируйте номер инвойса через фабрику/утилиту с таймстемпом и случайным суффиксом (например, `YYYYMMDDTHHMMSS-<RAND>-INVOICE`).
- Это позволит прогонять тесты параллельно без конфликтов имен.


### Шаг № 8. Добавьте (при наличии API) очистку после тестов
- Если у сервиса есть DELETE/архивация — выполняйте удаление созданных сущностей в финалайзере фикстуры.
- Если нет — для тестовых данных используйте префикс (например, `TEST_`) и периодическую задачу очистки на стенде.


### Шаг № 9. Введите метки pytest
- Пометьте тесты доменными метками (`@pytest.mark.invoicer`, `@pytest.mark.identity`, и т.д.) для удобного таргетированного прогона.


### Шаг № 10. Централизуйте работу с GraphQL и HTTP
- В `conftest.py` сделайте вспомогательные функции/фикстуры:
  - `graphql(query: str, variables: dict) -> Response/JSON`
  - `http` — сессия с кукой `JWT` и нужными заголовками по умолчанию.
- Тесты не должны знать деталей формирования URL/headers.


### Шаг № 11. Храните переменные окружения в одном месте
- Чтение `BASE_URL` и прочих переменных — только в `conftest.py`. Тесты получают уже готовые значения через фикстуры.
- При необходимости — поддержите `.env` через `python-dotenv` (опционально).


### Шаг № 12. Введите единый стиль проверок
- Базовые проверки структуры ответа выносите в небольшие хелперы (например, `assert_has_keys(obj, ["id", "name"])`), чтобы не дублировать.
- На уровне тестов оставляйте проверки бизнес-сценария.


### Шаг № 13. Документируйте как запускать и отлаживать
- В корневом `README` или в этом файле добавьте раздел «Как запускать»:

```bash
pytest -m invoicer
pytest tests/api/invoicer/test_invoices_create.py::test_create_invoice[case1]
pytest -q  # тихий вывод
```


### Шаг № 14. Проверьте параллельный прогон (опционально)
- С `pytest-xdist`: `pytest -n auto`. Убедитесь, что данные независимы, а номера инвойсов уникальны.


### Пример содержимого conftest.py (набросок, для реализации позже)

```python
import os
import pathlib
import pytest
import requests

@pytest.fixture(scope="session")
def base_url():
    url = os.getenv("BASE_URL", "").rstrip("/")
    assert url, "BASE_URL пустой — проверь .env"
    return url

@pytest.fixture(scope="session")
def assets_dir():
    return pathlib.Path(__file__).resolve().parent / "assets"

@pytest.fixture(scope="session")
def http(auth_token):
    session = requests.Session()
    session.headers.update({"Cookie": f"JWT={auth_token};"})
    return session

@pytest.fixture
def graphql(base_url, http):
    def _call(relative_path: str, query: str, variables: dict | None = None):
        url = f"{base_url}{relative_path}"
        payload = {"query": query, "variables": variables or {}}
        headers = {"Content-Type": "application/json"}
        resp = http.post(url, json=payload, headers=headers)
        assert resp.status_code == 200, f"GraphQL error {resp.status_code}: {resp.text}"
        return resp.json()
    return _call
```


### Пример фабрик (набросок интерфейсов)

```python
# factories/invoicer.py
def upload_invoice_document(http, base_url, assets_dir, filename="Invoice.pdf") -> dict: ...
def create_invoice(http, base_url, graphql, unique_suffix: str, **overrides) -> dict: ...

# factories/orders.py
def get_first_client(graphql) -> dict: ...

# factories/company_catalog.py
def get_first_company(graphql) -> dict: ...

# factories/identity.py
def get_admin_user_id(graphql) -> str: ...
```


### Что даст такой рефакторинг
- Независимость: каждый тест сам готовит данные, не полагаясь на другие тесты.
- Переиспользование: общий код (фикстуры, клиенты, фабрики) централизован.
- Масштабирование: добавлять новые сценарии проще — доменная папка, фабрика, тест.
- Стабильность: параллельный прогон, отсутствие гонок имен, меньше «флаппи»-ошибок.


### Чек-лист выполнения
- [ ] Создать структуру директорий и перенести `Invoice.pdf` в `tests/api/assets/`.
- [ ] Добавить `pytest.ini` (или дополнить существующий).
- [ ] Реализовать `conftest.py` с фикстурами `base_url`, `assets_dir`, `http`, `graphql`.
- [ ] Реализовать фабрики (`orders.py`, `company_catalog.py`, `invoicer.py`, `identity.py`).
- [ ] Перенести тесты в доменные каталоги, переименовать и объединить через параметризацию.
- [ ] Удалить зависимость тестов от порядка запуска; заполнить тесты локальной подготовкой данных.
- [ ] (Опционально) Добавить очистку данных или договориться о жизненном цикле тестовых данных.


Если потребуется, могу подготовить шаблон файлов (`conftest.py`, фабрики, обновлённые тесты) в отдельных ветках или коммитах по этому плану.


