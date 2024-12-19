#!/usr/bin/env python3
import datetime
import time

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from getpass import getpass

PORTAL_ADDRESS = 'https://oktopus.perfectgym.com/clientportal2/#/Login'
BOOK_NOW = 'book now'
CANCEL_BOOKING = 'cancel booking'

class GroupClass:
    name = ''
    class_hour_str = ''
    class_minutes = 0
    class_hour = 0
    reservation_hour = 0
    weekdays = []
    def __init__(self, name, hour, minutes, weekdays):
        self.name = name
        self.class_hour_str = str(hour)+':00'
        self.class_hour = hour
        self.class_minutes = minutes
        self.reservation_hour = hour - 2
        self.weekdays = weekdays


CLASSES = [
    GroupClass('DUMBBELL CROSSFIT WORKOUT', 20, 30,[1, 3, 6]),
    GroupClass('HIIT', 14, 30, [4])
]

def login(driver, email, password):
    driver.get(PORTAL_ADDRESS)

    WebDriverWait(driver, 30).until(
        EC.invisibility_of_element_located((By.CLASS_NAME, 'baf-load-mask'))
    )

    deny_all_button = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable(
            (By.CSS_SELECTOR, '.baf-button.cp-cookies-btn._accept[ng-click*="acceptOnlyNecessaryCookies"]'))        )
    deny_all_button.click()

    login_input = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, 'input[name="Login"]'))
    )

    login_input.clear()
    login_input.send_keys(email)

    password_input = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, 'input[name="Password"]'))
    )
    password_input.clear()
    password_input.send_keys(password)

    login_button = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, '.baf-button.cp-login-btn-login'))
    )

    login_button.click()

def prepare_to_book(driver, class_time):
    path = '//div[contains(@class, "cp-calendar-hour") and contains(text(), "{}")]'.format(class_time)
    WebDriverWait(driver, 30).until(
        EC.invisibility_of_element_located((By.CLASS_NAME, 'baf-load-mask'))
    )

    later_classes = WebDriverWait(driver, 20).until(
        EC.presence_of_element_located(
            (By.XPATH, path))
    )

    driver.execute_script("arguments[0].scrollIntoView(true);", later_classes)

    if not later_classes.is_displayed():
        raise Exception("later classes aren't visible")

def book(driver, name):
    path = f'//div[contains(@class, "calendar-item-name") and contains(., "{name}")]/ancestor::*[contains(@class, "calendar-view-item")]//div[contains(@class, "class-item-actions")]//div[contains(@class, "cp-btn-classes-action")]'
    bookable_button = WebDriverWait(driver, 30).until(
            EC.element_to_be_clickable((By.XPATH, path))
        )
    if not bookable_button.is_displayed():
        print("bookable buttons aren't visible")
        return False

    elements = driver.find_elements(By.XPATH,path)
    print(f"found {len(elements)} classes for {name}")

    for element in elements:
        if element.text.lower() == CANCEL_BOOKING:
            return True
        if element.text.lower() != BOOK_NOW:
            print(f"Skip not ready for booking class {element.text} {name}")
            continue

        driver.execute_script("arguments[0].scrollIntoView(true);", element)
        driver.execute_script("arguments[0].click();", element)
        print(f"Successful click to book {element.text} {name}")
        return True
    return False


# /home/vadim/.local/bin/pyinstaller  main.py --onefile
if __name__ == '__main__':
    print('Enter your login email:')
    login_email = input()
    login_password = getpass()

    chrome_options = Options()
    chrome_options.add_argument("--start-maximized")
    chrome_options.add_argument("--disable-extensions")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-infobars")

    chrome_manager = ChromeDriverManager().install()
    chrome_driver = webdriver.Chrome(service=Service(chrome_manager), options=chrome_options)
    login(chrome_driver, login_email, login_password)
    prepare_to_book(chrome_driver, CLASSES[0].class_hour_str)
    book(chrome_driver, CLASSES[0].name)
    chrome_driver.quit()

    all_not_in_day = True
    all_not_in_hour = True
    all_not_in_minute = True

    while True:
        now = datetime.datetime.now()

        for cls in CLASSES:
            booking_weekdays = cls.weekdays
            reservation_hour = cls.reservation_hour
            class_hour_str = cls.class_hour_str
            class_minutes = cls.class_minutes
            class_name = cls.name

            if now.weekday() not in booking_weekdays:
                print(f"Not in a week day {now.weekday()+1} {class_name}")
                continue

            all_not_in_day = False

            if now.time().hour != reservation_hour:
                print(f"Not in a day hour {now.time()} {class_name}")
                continue

            all_not_in_hour = False

            if not (class_minutes-1 <= now.time().minute < class_minutes+1):
                print(f"Not in a minutes {now.time()} {class_name}")
                continue

            all_not_in_minute = False

            chrome_driver = webdriver.Chrome(service=Service(chrome_manager), options=chrome_options)
            login(chrome_driver, login_email, login_password)

            while datetime.datetime.now().time().minute < class_minutes+1:
                chrome_driver.refresh()
                prepare_to_book(chrome_driver, class_hour_str)
                success = book(chrome_driver, class_name)
                if success:
                    time.sleep(5)
                    break

            chrome_driver.quit()

        if all_not_in_day:
            time.sleep(39600) # 11 hours
        if all_not_in_hour:
            time.sleep(1740) # 29 minutes
        if all_not_in_minute:
            time.sleep(29)

        all_not_in_day = True
        all_not_in_hour = True
        all_not_in_minute = True

