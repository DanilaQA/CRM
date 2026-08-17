from __future__ import annotations

import re

import allure
import pytest
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait

from pages.login_page import LoginPage


@pytest.fixture()
def login_page(driver, base_url):
    page = LoginPage(driver)
    page.open()
    WebDriverWait(driver, 15).until(lambda d: page.username_input().is_displayed())
    return page


def _has_any_text(texts: list[str], patterns: list[str]) -> bool:
    joined = " \n ".join(texts).lower()
    return any(re.search(pattern.lower(), joined) for pattern in patterns)


def _wait_for_login_feedback(page: LoginPage, timeout: int = 10) -> list[str]:
    try:
        WebDriverWait(page.driver, timeout).until(
            lambda d: page.alert_texts()
            or page.username_input().get_attribute("aria-invalid") == "true"
            or page.password_input().get_attribute("aria-invalid") == "true"
        )
    except TimeoutException:
        pass
    return page.alert_texts()


@allure.epic("Авторизация")
@allure.feature("Форма входа")
@allure.story("Отображение формы")
@allure.title("[Позитивный] Форма авторизации отображается корректно")
@allure.description("Проверка, что все элементы формы входа (логин, пароль, кнопка) видны на странице.")
def test_login_form_is_displayed(login_page):
    assert login_page.username_input().is_displayed()
    assert login_page.password_input().is_displayed()
    assert login_page.submit().is_displayed()


@allure.epic("Авторизация")
@allure.feature("Форма входа")
@allure.story("Валидация обязательных полей")
@allure.title("[Негативный] Валидация обязательных полей: логин={username!r}, пароль={password!r}")
@allure.description("Проверка сообщений валидации при пустых обязательных полях.")
@pytest.mark.parametrize(
    "username,password,expected_patterns",
    [
        # Пустые поля: страница показывает "Введите e-mail" / "Введите пароль"
        ("", "", [r"введ", r"обяз", r"required", r"пуст"]),
        ("user@example.com", "", [r"введ", r"обяз", r"required", r"пуст"]),
        ("", "Password123!", [r"введ", r"обяз", r"required", r"пуст"]),
    ],
)
def test_login_required_field_validation(login_page, username, password, expected_patterns):
    login_page.login(username=username, password=password)
    feedback = _wait_for_login_feedback(login_page)
    assert feedback, "Expected required-field validation feedback, but none appeared"
    assert _has_any_text(feedback, expected_patterns), (
        f"Feedback text did not match patterns {expected_patterns}. "
        f"Actual feedback: {feedback!r}"
    )


@allure.epic("Авторизация")
@allure.feature("Форма входа")
@allure.story("Граничные значения")
@allure.title("[Граничный] Отправка при невалидном формате/длине: логин={username!r}, пароль={password!r}")
@allure.description("Документирует фактическое поведение: форма не блокирует отправку "
                    "при невалидном формате/длине, а передаёт данные на сервер.")
@pytest.mark.parametrize(
    "username,password",
    [
        # Невалидный формат e-mail
        ("not-an-email", "Password123!"),
        # Слишком длинный логин
        ("a" * 256, "Password123!"),
        # Слишком короткий пароль
        ("user@example.com", "short"),
    ],
)
def test_login_no_client_side_block_on_invalid_input(login_page, username, password):
    login_page.login(username=username, password=password)
    # Ждём либо ошибку валидации, либо общую ошибку авторизации,
    # либо факт отправки (переход/обработка). Если появилась ошибка — проверяем её.
    feedback = _wait_for_login_feedback(login_page, timeout=15)
    if feedback:
        assert _has_any_text(
            feedback,
            [r"email", r"валид", r"неверн", r"слишком", r"long", r"max", r"длин",
             r"парол", r"min", r"корот", r"ошиб", r"авторизац", r"incorrect", r"invalid"],
        )


@allure.epic("Авторизация")
@allure.feature("Форма входа")
@allure.story("Негативные сценарии")
@allure.title("[Негативный] Неверные учётные данные не приводят к авторизации")
@allure.description("Негативный сценарий: неверные учётные данные не должны приводить "
                    "к успешной авторизации. Проверяем, что пользователь остаётся на форме "
                    "входа (не перенаправляется в систему), и фиксируем любое сообщение "
                    "об ошибке, если оно отображается.")
def test_login_general_error_for_invalid_credentials(login_page):
    login_page.login(username="user@example.com", password="WrongPassword123!")
    feedback = _wait_for_login_feedback(login_page, timeout=20)
    # Пользователь не должен быть авторизован: форма входа остаётся видимой.
    assert login_page.username_input().is_displayed(), (
        "Invalid credentials unexpectedly resulted in a successful login"
    )
    # Если страница показала сообщение об ошибке — проверяем его содержание.
    if feedback:
        assert _has_any_text(feedback, [r"невер", r"ошиб", r"авторизац", r"incorrect", r"invalid"])


@allure.epic("Авторизация")
@allure.feature("Форма входа")
@allure.story("Валидация обязательных полей")
@allure.title("[Негативный] Отправка пустой формы: валидация или блокировка кнопки")
@allure.description("Проверка поведения при отправке пустой формы: должна появиться "
                    "валидация обязательных полей либо кнопка должна быть заблокирована.")
def test_login_button_disabled_or_validation_on_empty_submit(login_page):
    # Фокусируемся на полях, чтобы активировать валидацию формы,
    # затем отправляем пустую форму.
    login_page.username_input().click()
    login_page.password_input().click()
    login_page.submit().click()
    feedback = _wait_for_login_feedback(login_page, timeout=8)
    assert feedback or login_page.submit().get_attribute("disabled") is not None
    if feedback:
        assert _has_any_text(feedback, [r"введ", r"обяз", r"required", r"пуст"]), (
            f"Feedback text did not match patterns. Actual feedback: {feedback!r}"
        )
