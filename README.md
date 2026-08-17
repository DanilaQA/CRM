# SberCRM login Selenium tests

Минимальный каркас автотестов на Python + Selenium + pytest для страницы авторизации `https://app.sbercrm.com/#/login`.

## Структура

- `pages/login_page.py` — Page Object для формы логина
- `tests/test_login_form.py` — позитивные, негативные и граничные проверки
- `conftest.py` — фикстура браузера
- `requirements.txt` — зависимости
- `.github/workflows/ci.yml` — CI/CD пайплайн (GitHub Actions)
- `pytest.ini` — конфигурация pytest
- `.gitignore` — исключения для контроля версий

## Запуск

```bash
pip install -r requirements.txt
pytest -q
```

## Allure-отчёт

Для генерации отчёта Allure нужен установленный CLI (`brew install allure`).

```bash
# 1. Запуск тестов со сбором результатов Allure
pytest -q --alluredir=allure-results

# 2. Генерация HTML-отчёта
allure generate allure-results -o allure-report --clean

# 3. Просмотр отчёта в браузере
allure open allure-report
```

Результаты тестов сохраняются в `allure-results/`, готовый отчёт — в `allure-report/`.

## Переменные окружения

- `BROWSER=chrome` — используемый браузер
- `SBERCRM_BASE_URL` — URL страницы логина, по умолчанию `https://app.sbercrm.com/#/login`
- `HEADLESS=true|false` — headless-режим браузера (обязателен для CI), по умолчанию `false`

## CI/CD (GitHub Actions)

Пайплайн в [`.github/workflows/ci.yml`](.github/workflows/ci.yml) запускает тесты в облаке
на `ubuntu-latest` при каждом push/PR в ветки `main`/`master`, а также вручную через
`workflow_dispatch`.

Что делает пайплайн:

1. Устанавливает Python 3.11.
2. Устанавливает Chrome и ChromeDriver (`browser-actions/setup-chrome`).
3. Устанавливает зависимости из `requirements.txt`.
4. Запускает тесты в headless-режиме (`HEADLESS=true`) со сбором Allure-результатов.
5. Генерирует Allure-отчёт и загружает его как артефакт `allure-report`.
6. Загружает сырые результаты `allure-results` как артефакт.

### Как подключить

1. Инициализируйте git-репозиторий и загрузите проект на GitHub:
   ```bash
   git init
   git add .
   git commit -m "Add SberCRM login tests with CI"
   git remote add origin https://github.com/<user>/<repo>.git
   git push -u origin main
   ```
2. В настройках репозитория (Settings → Secrets and variables → Actions) при необходимости
   добавьте секрет `SBERCRM_BASE_URL` (если URL логина отличается от значения по умолчанию).
3. Пайплайн запустится автоматически. Отчёт Allure доступен во вкладке **Actions** →
   выбранный прогон → артефакт `allure-report` (скачать и открыть `index.html`).

> Примечание: для публикации отчёта на GitHub Pages можно дополнительно использовать
> `actions/deploy-pages` или `peaceiris/actions-gh-pages`.

## Сценарии

Покрыты:

- отображение формы логина
- пустые поля
- пустой логин / пустой пароль
- невалидный формат логина
- слишком длинный логин
- слишком короткий пароль
- общая ошибка при неверных учетных данных
- поведение кнопки `Войти` при пустой отправке формы
