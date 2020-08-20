from __future__ import unicode_literals
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from django.test import override_settings
from django.urls import reverse

from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

import socket # access low-level network properties

@override_settings(ALLOWED_HOSTS=["*"])
class SeleniumLiveTestCase(StaticLiveServerTestCase):

    DEFAULT_WAIT_TIME = 10
    host = '0.0.0.0'

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.host = socket.gethostbyname(socket.gethostname())
        cls.selenium = webdriver.Remote(
            command_executor='http://selenium:4444/wd/hub',
            desired_capabilities=DesiredCapabilities.CHROME,
        )
        cls.selenium.implicitly_wait(cls.DEFAULT_WAIT_TIME)
        cls.selenium.set_page_load_timeout(cls.DEFAULT_WAIT_TIME)

    @classmethod
    def tearDownClass(cls):
        cls.selenium.quit()
        super().tearDownClass()

    def submit_login(self, username, password):

        WebDriverWait(self.selenium, self.DEFAULT_WAIT_TIME).until(
            EC.presence_of_element_located((By.NAME, "login")))
        WebDriverWait(self.selenium, self.DEFAULT_WAIT_TIME).until(
            EC.presence_of_element_located((By.NAME, "password")))
        WebDriverWait(self.selenium, self.DEFAULT_WAIT_TIME).until(
            EC.presence_of_element_located((By.NAME, "submit-button")))

        username_input = self.selenium.find_element_by_name("login")
        username_input.send_keys(username)
        password_input = self.selenium.find_element_by_name("password")
        password_input.send_keys(password)
        submit_button = self.selenium.find_element_by_name("submit-button")
        submit_button.click()

        WebDriverWait(self.selenium, self.DEFAULT_WAIT_TIME).until(
            EC.presence_of_element_located(
                (By.XPATH, '//div[@class="jumbotron"]')))

    def logout(self):

        self.selenium.get('%s%s' % (self.live_server_url, reverse('account_logout')))
        self.selenium.find_element_by_xpath('//button[@type="submit"]').click()

    def get_homepage(self):
        self.selenium.get('%s%s' % (self.live_server_url, '/'))
