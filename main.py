#!/usr/bin/env python3
import base64
from datetime import datetime
import time

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


PORTAL_ADDRESS = 'https://oktopus.perfectgym.com/clientportal2/#/Login'
BOOK_NOW = 'book now'

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

    deny_all_button = WebDriverWait(driver, 30).until(
        EC.element_to_be_clickable(
            (By.CSS_SELECTOR, '.baf-button.cp-cookies-btn._accept[ng-click*="acceptOnlyNecessaryCookies"]'))
    )
    driver.execute_script("arguments[0].click();", deny_all_button)

    login_input = WebDriverWait(driver, 30).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, 'input[name="Login"]'))
    )

    login_input.clear()
    login_input.send_keys(email)

    password_input = WebDriverWait(driver, 30).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, 'input[name="Password"]'))
    )
    password_input.clear()
    password_input.send_keys(password)

    login_button = WebDriverWait(driver, 30).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, '.baf-button.cp-login-btn-login'))
    )

    driver.execute_script("arguments[0].click();", login_button)

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
    try:
        path = f"//div[contains(@class, 'calendar-item-name') and contains(., '{name}') and not(contains(., 'LIFT'))]/ancestor::*[contains(@class, 'calendar-view-item')]//div[contains(@class, 'calendar-item-content')]"
        elements = WebDriverWait(driver, 30).until(
                EC.presence_of_all_elements_located((By.XPATH, path))
            )
        print(f"found {len(elements)} classes for {name}")

        for element in elements:
            driver.execute_script("arguments[0].scrollIntoView(true);", element)
            if not element.is_displayed():
                print(f"Element is not displayed {element.text} {name}")
                continue
            driver.execute_script("arguments[0].click();", element)
            print("element clicked")
            button_path = "//*[contains(@class, 'class-details-book-btn') and contains(@class, 'cp-calendar-color-btn')]"

            book_button = WebDriverWait(driver, 30).until(
                EC.element_to_be_clickable((By.XPATH, button_path))
            )
            print("book button found")

            if "cancel" in book_button.text.lower():
                return True
            if "loading" in book_button.text.lower():
                time.sleep(1/100)
            if book_button.text.lower() != BOOK_NOW:
                print(datetime.now().time(), f"Not ready to book {book_button.text} {name}...")

            close_button = WebDriverWait(driver, 30).until(
                EC.element_to_be_clickable((By.XPATH, '//button[contains(@class, "cp-btn-modal-close")]'))
            )
            print("close button found")

            driver.execute_script("arguments[0].click();", book_button)
            print(f"clicked to book {book_button.text} {name}")
            driver.execute_script("arguments[0].click();", close_button)

        return False

    except Exception as e:
        print("Error", e)
        return False


def book_loop(chr_mgr):
    while True:
        all_not_in_day = True
        all_not_in_hour = True
        all_not_in_minute = True
        now = datetime.now()

        for cls in CLASSES:
            booking_weekdays = cls.weekdays
            reservation_hour = cls.reservation_hour
            class_hour_str = cls.class_hour_str
            class_hour = cls.class_hour
            class_minutes = cls.class_minutes
            class_name = cls.name

            if datetime.now().weekday() not in booking_weekdays:
                print(f"Not in a week day {class_name}")
                continue
            all_not_in_day = False

            if now.time().hour < reservation_hour:
                print(f"Too soon for reservation hour {now.time().isoformat('seconds')} {class_name}")
                continue
            all_not_in_hour = False

            if now.time().hour == reservation_hour and now.time().minute < class_minutes - 1:
                print(f"Too soon for reservation minutes {now.time().isoformat('seconds')} {class_name}")
                continue
            all_not_in_minute = False

            chrome_driver = webdriver.Chrome(service=Service(chr_mgr), options=chrome_options)
            try:
                login(chrome_driver, login_email, login_password)
                prepare_to_book(chrome_driver, class_hour_str)
            except Exception as ex:
                print("Failed", ex)
                continue

            while True:
                now = datetime.now().time()
                try:
                    if now.minute < class_minutes + 1 and now.hour == reservation_hour:
                        print("booking...")

                        success = book(chrome_driver, class_name)
                        if success:
                            break
                    elif now.hour < class_hour + 3:
                        print(now, "Failed to book the class quickly - will try to book if someone cancelled")
                        time.sleep(60) # minute
                        success = book(chrome_driver, class_name)
                        if success:
                            break
                    else:
                        print("time sleep")
                        time.sleep(5)
                        break
                except Exception as loop_ex:
                    print("loop failed", loop_ex)
                    continue
            chrome_driver.quit()

        print(all_not_in_day,all_not_in_hour,all_not_in_minute)
        if all_not_in_day:
            time.sleep(39600)  # 11 hours
        if all_not_in_hour:
            time.sleep(1740)  # 29 minutes
        if all_not_in_minute:
            time.sleep(29)


# /home/vadim/.local/bin/pyinstaller  main.py --onefile
if __name__ == '__main__':
    print('Enter your login email:')
    login_email = input()
    login_password = input()
    if not login_email or login_email == '':
        login_email = base64.b64decode('dmFkaW1maWxpbjQ1QGdtYWlsLmNvbQ==').decode('utf-8')

    chrome_options = Options()
    chrome_options.add_argument("--start-maximized")
    chrome_options.add_argument("--disable-extensions")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-infobars")

    chrome_manager = ChromeDriverManager().install()
    chr_driver = webdriver.Chrome(service=Service(chrome_manager), options=chrome_options)
    login(chr_driver, login_email, login_password)
    prepare_to_book(chr_driver, CLASSES[0].class_hour_str)
    book(chr_driver, CLASSES[0].name)
    chr_driver.quit()

    book_loop(chrome_manager)
    chr_driver.quit()



