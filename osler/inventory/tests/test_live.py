import datetime, collections, random, math
from optparse import Option

from django.urls import reverse
from django.utils.timezone import now

from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from osler import inventory

from selenium.common.exceptions import WebDriverException

from osler.core import models, urls
from osler.core.tests.test_views import build_user
from osler.core.tests.test import SeleniumLiveTestCase
from osler.inventory.tests.factories import DrugFactory

from osler.workup import models as workup_models
from osler.workup.tests.tests import wu_dict

from osler.inventory import models as inventory_models 

import osler.users.tests.factories as user_factories

BASIC_FIXTURES = ['core', 'workup', 'inventory', 'drug_examples']
# I need to find out what my basic fixtures are supposed to be

class TestLiveInventory(SeleniumLiveTestCase):
    fixtures = BASIC_FIXTURES    # what is the point of this line of code?

    def test_check_drugs_present(self):
        '''
        Test that all drugs in drug inventroy are rendered 
        in the table
        '''
        user = build_user(password='password',
                       group_factories=[user_factories.AttendingGroupFactory])
        self.get_homepage()
        self.submit_login(user.username, 'password')
        self.get_url(reverse('inventory:drug-list'))   # go to the inventory page

        drugsInTable = []
        finished = False
        while not finished:
            # find all drug titles on current page and add them to drugsInTable
            drugTitlesOnPage = self.selenium.find_elements(
                By.CSS_SELECTOR, 
                "td:first-child > a"
            )
            drugTitlesOnPageText = [title.text for title in drugTitlesOnPage]
            drugsInTable.extend(drugTitlesOnPageText)

            # select the next page arrow button
            nextPageButton = self.selenium.find_element(  
                By.CSS_SELECTOR,
                "ul.pagination > li:nth-last-of-type(2)"
            )

            # CHECK if this has the disabled class, if it does we are finished (there are no more pages to visit)
            if 'disabled' in nextPageButton.get_attribute('class').split():   
                finished = True
            else:
                nextPageButton.click()

        # get list of names of all drugs in database and assert that list is equal to list of all drug names in database
        allDrugs = inventory_models.Drug.objects.all()
        allDrugNames = [drug.name for drug in allDrugs]
        assert collections.Counter(drugsInTable) == collections.Counter(allDrugNames)
    

    def test_check_dispense_form_submission(self):
        """
        generates random inputs for the dispense form and makes sure no errors are caused
        creates a test drug and tests dispense form with random inputs, deletes test drug when test ends
        """
        # just use a drug on the first page that was generated from the example_drugs fixture
        testDrug = DrugFactory(name = "testDrug")

        # generate random inputs for dispense form
        testDrugStock = testDrug.stock
        dispenseAmount = math.floor(random.random()*testDrugStock)

        activePatients = models.Patient.objects.filter("active")   # I don't think this works
        randomPatientIndex = math.floor(random.random()*len(activePatients))

        # TEST THE RANDOM INPUTS
        # click dispense form button
        self.selenium.find_element(
            By.XPATH,
            "/html[@class='no-js']/body/div[@id='root']/div[@class='container']/div/table[@id='drug-list-table']/tbody/tr[1]/td[8]/button[@class='btn btn-success']"
        ).click()
        
        # enter amount to dispense
        self.selenium.find_element(By.ID, "num").send_keys(dispenseAmount)

        # choose random patient from dropdown  (we want to pick the randomPatientIndexth entry in the dropdown list)
        # do I need to to open the dropdown first?
        patientDropdown = self.selenium.find_element(By.ID, "patient_pk")
        patientDropdown.click()
        patientChoices = patientDropdown.self.selenium.find_element(By.NAME, "option")
        patientChoices[randomPatientIndex].click()

        # click the dispense button (will the test automatically fail if a django error is caused?)
        self.selenium.find_element(
            By.XPATH,
            "/html/body/div[5]/div/div/form/div[3]/button[2]"
        ).click()

    """
    More test ideas:




    """




                    










        

