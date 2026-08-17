from __future__ import annotations

import os

import pytest
from selenium import webdriver
from selenium.webdriver.chrome.options import Options


@pytest.fixture(scope='session')
def base_url() -> str:
    return os.getenv('SBERCRM_BASE_URL', 'https://app.sbercrm.com/#/login')


@pytest.fixture()
def driver():
    options = Options()
    options.add_argument('--disable-notifications')
    options.add_argument('--disable-infobars')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--disable-gpu')
    options.add_argument('--disable-extensions')
    options.add_argument('--disable-blink-features=AutomationControlled')
    options.add_experimental_option('excludeSwitches', ['enable-automation'])
    options.add_experimental_option('useAutomationExtension', False)

    # Headless-режим для CI/CD (без графического окружения).
    headless = os.getenv('HEADLESS', 'false').lower() in ('1', 'true', 'yes', 'on')
    if headless:
        options.add_argument('--headless=new')
        options.add_argument('--window-size=1920,1080')
        # User-agent обычного браузера — снижает вероятность детекта автоматизации.
        options.add_argument(
            '--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
            'AppleWebKit/537.36 (KHTML, like Gecko) '
            'Chrome/128.0.0.0 Safari/537.36'
        )
    else:
        options.add_argument('--start-maximized')

    browser = os.getenv('BROWSER', 'chrome').lower()
    if browser == 'chrome':
        drv = webdriver.Chrome(options=options)
    else:
        raise RuntimeError(f'Unsupported browser: {browser}')

    drv.set_page_load_timeout(30)
    yield drv
    drv.quit()
