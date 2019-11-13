from django.contrib.staticfiles.testing import StaticLiveServerTestCase

from selenium.webdriver.chrome import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


class SeleniumLiveTestCase(StaticLiveServerTestCase):

    DEFAULT_WAIT_TIME = 30

    @classmethod
    def setUpClass(cls):
        super(SeleniumLiveTestCase, cls).setUpClass()

        opt = webdriver.ChromeOptions()
        opt.add_experimental_option('w3c', False)
        cls.selenium = webdriver.Chrome(chrome_options=opt)

        # cls.selenium = WebDriver()
        cls.selenium.implicitly_wait(cls.DEFAULT_WAIT_TIME)
        cls.selenium.set_page_load_timeout(cls.DEFAULT_WAIT_TIME)

    @classmethod
    def tearDownClass(cls):
        cls.selenium.quit()
        super(SeleniumLiveTestCase, cls).tearDownClass()

    def submit_login(self, username, password):

        WebDriverWait(self.selenium, self.DEFAULT_WAIT_TIME).until(
            EC.presence_of_element_located((By.NAME, "username")))
        WebDriverWait(self.selenium, self.DEFAULT_WAIT_TIME).until(
            EC.presence_of_element_located((By.NAME, "password")))
        WebDriverWait(self.selenium, self.DEFAULT_WAIT_TIME).until(
            EC.presence_of_element_located(
                (By.XPATH, '//input[@type="submit"]')))

        username_input = self.selenium.find_element_by_name("username")
        username_input.send_keys(username)
        password_input = self.selenium.find_element_by_name("password")
        password_input.send_keys(password)

        self.selenium.find_element_by_xpath('//input[@type="submit"]').click()

        WebDriverWait(self.selenium, self.DEFAULT_WAIT_TIME).until(
            EC.presence_of_element_located(
                (By.XPATH, '//div[@class="jumbotron"]')))
        import time
        time.sleep(2)
