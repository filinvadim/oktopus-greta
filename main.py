#!/usr/bin/env python3
import datetime

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import StaleElementReferenceException
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time


def login(driver, email, password):
    try:
        driver.get('https://oktopus.perfectgym.com/clientportal2/#/Login')

        WebDriverWait(driver, 30).until(
            EC.invisibility_of_element_located((By.CLASS_NAME, 'baf-load-mask'))
        )
        time.sleep(3)

        deny_all_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable(
                (By.CSS_SELECTOR, '.baf-button.cp-cookies-btn._accept[ng-click*="acceptOnlyNecessaryCookies"]'))        )
        deny_all_button.click()

        login_input = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'input[name="Login"]'))
        )

        login_input.clear()
        login_input.send_keys(email)  # Замените 'your_login' на реальный логин

        password_input = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'input[name="Password"]'))
        )
        password_input.clear()
        password_input.send_keys(password)  # Замените 'your_password' на реальный пароль

        login_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, '.baf-button.cp-login-btn-login'))
        )

        login_button.click()
    except Exception as e:
        print(f"Login error occurred: {e}")

def prepare_to_book(driver, class_time):
    try:
        path = '//div[contains(@class, "cp-calendar-hour") and contains(text(), "{}")]'.format(class_time)
        WebDriverWait(driver, 30).until(
            EC.invisibility_of_element_located((By.CLASS_NAME, 'baf-load-mask'))
        )

        later_classes = WebDriverWait(driver, 20).until(
            EC.presence_of_element_located(
                (By.XPATH, path))
        )

        # Прокрутить до элемента
        driver.execute_script("arguments[0].scrollIntoView(true);", later_classes)

        if not later_classes.is_displayed():
            raise Exception("later classes aren't visible")
    except Exception as e:
        print(f"Prepare for booking error occurred: {e}")

def book(driver):
    try:
        path = '//div[contains(@class, "calendar-item-name") and contains(., "DUMBBELL CROSSFIT WORKOUT")]/ancestor::*[contains(@class, "calendar-view-item")]//div[contains(@class, "class-item-actions")]//div[contains(@class, "cp-btn-classes-action")]'
        bookable_button = WebDriverWait(driver, 30).until(
                EC.element_to_be_clickable((By.XPATH, path))
            )
        if not bookable_button.is_displayed():
            raise Exception("bookable buttons aren't visible")

        elements = driver.find_elements(By.XPATH,path)
        print(f"found {len(elements)} classes")

        for index, element in enumerate(elements):
            if element.text != 'Book now' and element.text != 'Cancel booking':
                print(f"Skip not ready class {element.text}")
                continue
            try:
                driver.execute_script("arguments[0].scrollIntoView(true);", element)
                driver.execute_script("arguments[0].click();", element)
                print(f"Successful click to book {element.text}")
            except Exception as e:
                print(f"Error: {e}")
                return False

        elements = driver.find_elements(By.XPATH, path)
        for element in elements:
            print(f"Class status {element.text}")
            if element.text == 'Cancel booking':
                return True
        return False

    except StaleElementReferenceException as e:
        print(f"Element recreated: {e}")
        return False

if __name__ == '__main__':
    print('Enter your login email:')
    login_email = input()
    print('Enter your password:')
    login_password = input()

    chrome_options = Options()
    chrome_options.add_argument("--start-maximized")
    chrome_options.add_argument("--disable-extensions")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-infobars")

    bookingWeekdays = [1, 3, 4, 6]
    minutes_59 = 3540

    startReservationHourDefault = 18 # minus 22 hours from the class
    startReservationHourSaturday = 12 # minus 22 hours from the class

    classHourDefault = "20:00"
    classHourSaturday = "14:00"

    chrome_driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
    login(chrome_driver, login_email, login_password)
    prepare_to_book(chrome_driver, classHourDefault)
    book(chrome_driver)
    chrome_driver.quit()

    while True:
        now = datetime.datetime.now()

        if now.weekday() not in bookingWeekdays:
            print("NOT IN A BOOKING WEEKDAY")
            midnight = (now + datetime.timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)
            seconds_to_midnight = (midnight - now).total_seconds()
            time.sleep(seconds_to_midnight)
            continue

        time_to_29 = now.replace(minute=29, second=0, microsecond=0)
        time_to_31 = now.replace(minute=29, second=0, microsecond=0)
        if time_to_29 > now >= time_to_31:
            print("NOT IN A BOOKING MINUTES")
            time_to_29 = (now + datetime.timedelta(hours=1)).replace(minute=29, second=0, microsecond=0)
            seconds_to_29 = (time_to_29 - now).total_seconds()
            time.sleep(seconds_to_29)
            continue

        # not friday
        if (now.weekday() != 4 and now.time().hour != startReservationHourDefault) or (
                now.weekday() == 4 and now.time().hour != startReservationHourSaturday
        ):
            print("NOT IN A BOOKING HOUR")
            time.sleep(minutes_59)
            continue

        chrome_driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

        login(chrome_driver, login_email, login_password)

        if now.weekday() != 4:
            prepare_to_book(chrome_driver, classHourDefault)
        else:
            prepare_to_book(chrome_driver, classHourSaturday) # friday

        while book(chrome_driver) is False:
            time.sleep(1/10)

        chrome_driver.quit()

