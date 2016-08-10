from django.test import TestCase
from django.core.exceptions import ValidationError
from django.utils.timezone import now
from django.core.urlresolvers import reverse

from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from selenium.webdriver.firefox.webdriver import WebDriver
from selenium.common.exceptions import ElementNotVisibleException,\
    WebDriverException
from selenium.webdriver.common.action_chains import ActionChains
from pttrack.test_views import live_submit_login
from selenium.webdriver.common.by import By


from pttrack.test_views import build_provider, log_in_provider
from pttrack.models import Patient, ProviderType, Provider

from . import validators
from . import models
from . import forms


def wu_dict():
    return {
            'clinic_day': models.ClinicDate.objects.first(),
            'chief_complaint': "SOB",
            'diagnosis': "MI",
            'HPI': "f", 'PMH_PSH': "f", 'meds': "f", 'allergies': "f",
            'fam_hx': "f", 'soc_hx': "f",
            'ros': "f", 'pe': "f", 'A_and_P': "f",
            'hr': '89', 'bp': '120/80', 'rr': '16', 't': '98',
            'labs_ordered_internal': 'f', 'labs_ordered_quest': 'f',
            'got_voucher': True,
            'got_imaging_voucher': True,
            'will_return': True,
            'author': Provider.objects.first(),
            'author_type': ProviderType.objects.first(),
            'patient': Patient.objects.first()
        }


class TestModelFieldValidators(TestCase):
    '''
    TestCase to verify that validators are functioning.
    '''

    def test_validate_bp(self):
        '''
        Test our validator for blood pressures. There should be a '/' between
        systolic and diastolic, it should be able to handle 2 and 3 digit
        pressures, and systolic should always be higher than diastolic.
        '''
        self.assertEqual(validators.validate_bp("110/90"), None)
        self.assertEqual(validators.validate_bp("90/50"), None)
        self.assertEqual(validators.validate_bp("170/100"), None)

        with self.assertRaises(ValidationError):
            validators.validate_bp("90")
        with self.assertRaises(ValidationError):
            validators.validate_bp("/90")
        with self.assertRaises(ValidationError):
            validators.validate_bp("100/")
        with self.assertRaises(ValidationError):
            validators.validate_bp("90/200")
        with self.assertRaises(ValidationError):
            validators.validate_bp("-120/80")
        with self.assertRaises(ValidationError):
            validators.validate_bp("1200/80")
        with self.assertRaises(ValidationError):
            validators.validate_bp("200/20")


class TestWorkupModel(TestCase):

    fixtures = ['workup', 'pttrack']

    def setUp(self):
        self.provider = log_in_provider(
            self.client,
            build_provider())

        models.ClinicType.objects.create(name="Basic Care Clinic")
        models.ClinicDate.objects.create(
            clinic_type=models.ClinicType.objects.first(),
            clinic_date=now().date(),
            gcal_id="tmp")

        self.valid_wu_dict = wu_dict()

    def test_sign(self):

        wu = models.Workup.objects.create(**self.valid_wu_dict)

        # attempt sign as non-attending
        disallowed_ptype = ProviderType.objects.\
            filter(signs_charts=False).first()
        with self.assertRaises(ValueError):
            wu.sign(
                self.provider.associated_user,
                disallowed_ptype)
        wu.save()

        # attempt sign without missing ProviderType
        unassociated_ptype = ProviderType.objects.create(
            long_name="New", short_name="New", signs_charts=True)
        with self.assertRaises(ValueError):
            wu.sign(
                self.provider.associated_user,
                unassociated_ptype)

        # attempt sign as attending
        allowed_ptype = ProviderType.objects.\
            filter(signs_charts=True).first()
        wu.sign(
            self.provider.associated_user,
            allowed_ptype)
        wu.save()


class ViewsExistTest(TestCase):
    '''
    Verify that views involving the wokrup are functioning.
    '''
    fixtures = ['workup', 'pttrack']

    def setUp(self):

        models.ClinicDate.objects.create(
            clinic_type=models.ClinicType.objects.first(),
            clinic_date=now().date(),
            gcal_id="tmp")

        log_in_provider(self.client, build_provider())

        self.wu = models.Workup.objects.create(
            clinic_day=models.ClinicDate.objects.first(),
            chief_complaint="SOB",
            diagnosis="MI",
            HPI="A", PMH_PSH="B", meds="C", allergies="D", fam_hx="E",
            soc_hx="F", ros="", pe="", A_and_P="",
            author=models.Provider.objects.first(),
            author_type=ProviderType.objects.first(),
            patient=Patient.objects.first())

    def test_clindate_create_redirect(self):
        '''Verify that if no clindate exists, we're properly redirected to a
        clindate create page.'''

        # First delete clindate that's created in setUp.
        models.ClinicDate.objects.all().delete()

        pt = Patient.objects.first()

        pt_url = 'new-workup'
        response = self.client.get(reverse(pt_url, args=(pt.id,)))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('new-clindate', args=(pt.id,)))

    def test_new_workup_view(self):

        pt = Patient.objects.first()
        response = self.client.get(reverse('new-workup', args=(pt.id,)))
        self.assertEqual(response.status_code, 200)

    def test_workup_urls(self):
        wu_urls = ['workup',
                   'workup-update']

        # test the creation of many workups, just in case.
        for i in range(10):
            models.Workup.objects.bulk_create(
                [models.Workup(**wu_dict()) for i in range(77)])
            wu = models.Workup.objects.last()

            wu.diagnosis_categories.add(models.DiagnosisType.objects.first())

            for wu_url in wu_urls:
                response = self.client.get(reverse(wu_url, args=(wu.id,)))
                self.assertEqual(response.status_code, 200)

    def test_workup_initial(self):

        pt = Patient.objects.first()

        date_string = self.wu.written_datetime.strftime("%B %d, %Y")
        heading_text = "Migrated from previous workup on %s. Please delete this heading and modify the following:\n\n" % date_string

        response = self.client.get(reverse('new-workup', args=(pt.id,)))
        self.assertEqual(response.context['form'].initial['PMH_PSH'],
                         heading_text + "B")
        self.assertEqual(response.context['form'].initial['meds'],
                         heading_text + "C")
        self.assertEqual(response.context['form'].initial['allergies'],
                         heading_text + "D")
        self.assertEqual(response.context['form'].initial['fam_hx'],
                         heading_text + "E")
        self.assertEqual(response.context['form'].initial['soc_hx'],
                         heading_text + "F")

    def test_workup_update(self):
        '''
        Updating should be possible always for attendings, only without
        attestation for non-attendings.
        '''

        # if the wu is unsigned, all can access update.
        for role in ["Preclinical", "Clinical", "Coordinator", "Attending"]:
            log_in_provider(self.client, build_provider([role]))
            response = self.client.get(
                reverse('workup-update', args=(self.wu.id,)))
            self.assertEqual(response.status_code, 200)

        self.wu.sign(build_provider(["Attending"]).associated_user)
        self.wu.save()

        # nonattesting cannot access
        for role in ["Preclinical", "Clinical", "Coordinator"]:
            log_in_provider(self.client, build_provider([role]))
            response = self.client.get(
                reverse('workup-update', args=(self.wu.id,)))
            self.assertRedirects(response,
                                 reverse('workup', args=(self.wu.id,)))

        # attesting can
        log_in_provider(self.client, build_provider(["Attending"]))
        response = self.client.get(
            reverse('workup-update', args=(self.wu.id,)))
        self.assertEqual(response.status_code, 200)

    def test_workup_signing(self):
        '''
        Verify that singing is possible for attendings, and not for others.
        '''

        wu_url = "workup-sign"

        self.wu.diagnosis_categories.add(models.DiagnosisType.objects.first())
        self.wu.save()

        # Fresh workups should be unsigned
        self.assertFalse(self.wu.signed())

        # Providers with can_attend == False should not be able to sign
        for nonattesting_role in ["Preclinical", "Clinical", "Coordinator"]:
            log_in_provider(self.client, build_provider([nonattesting_role]))

            response = self.client.get(
                reverse(wu_url, args=(self.wu.id,)))
            self.assertRedirects(response,
                                 reverse('workup', args=(self.wu.id,)))
            self.assertFalse(models.Workup.objects.get(pk=self.wu.id).signed())

        # Providers able to attend should be able to sign.
        log_in_provider(self.client, build_provider(["Attending"]))

        response = self.client.get(reverse(wu_url, args=(self.wu.id,)))
        self.assertRedirects(response, reverse('workup', args=(self.wu.id,)),)
        # the self.wu has been updated, so we have to hit the db again.
        self.assertTrue(models.Workup.objects.get(pk=self.wu.id).signed())

    def test_workup_pdf(self):
        '''
        Verify that pdf download with the correct naming protocol is working
        '''

        wu_url = "workup-pdf"

        self.wu.diagnosis_categories.add(models.DiagnosisType.objects.first())
        self.wu.save()

        for nonstaff_role in ProviderType.objects.filter(staff_view=False):
            log_in_provider(self.client, build_provider([nonstaff_role]))

            response = self.client.get(reverse(wu_url, args=(self.wu.id,)))
            self.assertRedirects(response,
                                 reverse('workup', args=(self.wu.id,)))

        for staff_role in ProviderType.objects.filter(staff_view=True):
            log_in_provider(self.client, build_provider([staff_role.pk]))
            response = self.client.get(reverse(wu_url, args=(self.wu.id,)))
            self.assertEqual(response.status_code, 200)


class TestFormFieldValidators(TestCase):

    fixtures = ['workup', 'pttrack']

    def setUp(self):
        self.provider = log_in_provider(
            self.client,
            build_provider())

        models.ClinicType.objects.create(name="Basic Care Clinic")
        models.ClinicDate.objects.create(
            clinic_type=models.ClinicType.objects.first(),
            clinic_date=now().date(),
            gcal_id="tmp")

        self.valid_wu_dict = wu_dict()

    def test_missing_voucher_amount(self):

        form_data = self.valid_wu_dict

        form = forms.WorkupForm(data=form_data)

        # and expect an error to be on the empty altphone field
        self.assertNotEqual(form['voucher_amount'].errors, [])
        self.assertNotEqual(form['patient_pays'].errors, [])

        form_data['voucher_amount'] = '40'
        form_data['patient_pays'] = '40'

        form = forms.WorkupForm(data=form_data)
        self.assertEqual(form['voucher_amount'].errors, [])
        self.assertEqual(form['patient_pays'].errors, [])

        self.assertNotEqual(form['imaging_voucher_amount'].errors, [])
        self.assertNotEqual(form['patient_pays_imaging'].errors, [])

        form_data['imaging_voucher_amount'] = '40'
        form_data['patient_pays_imaging'] = '40'

        form = forms.WorkupForm(data=form_data)
        self.assertEqual(form['imaging_voucher_amount'].errors, [])
        self.assertEqual(form['patient_pays_imaging'].errors, [])


class LiveTesting(StaticLiveServerTestCase):

    fixtures = ['workup', 'pttrack']

    @classmethod
    def setUpClass(cls):
        super(LiveTesting, cls).setUpClass()
        cls.selenium = WebDriver()

    @classmethod
    def tearDownClass(cls):
        cls.selenium.quit()
        super(LiveTesting, cls).tearDownClass()

    def setUp(self):

        models.ClinicDate.objects.create(
            clinic_type=models.ClinicType.objects.first(),
            clinic_date=now().date())

        build_provider(username='jrporter', password='password')

        # any valid URL should redirect to login at this point.
        self.selenium.get('%s%s' % (self.live_server_url, '/'))
        live_submit_login(self.selenium, 'jrporter', 'password')

        PROVIDER_TYPE = 'Coordinator'
        self.selenium.find_element_by_xpath(
            '//input[@value="%s"]' % PROVIDER_TYPE).click()
        self.selenium.find_element_by_xpath(
            '//button[@type="submit"]').click()

    def select_tab(self, tab):

        self.selenium.execute_script("window.scrollTo(0, 0)")
        self.selenium.find_element_by_xpath(
            '//a[@href="#{t}"]'.format(t=tab)).click()

    def fill_out_workup(self, wu_data,
                        dx_cats=[models.DiagnosisType.objects.all()],
                        submit=True):

        self.select_tab('basics')
        for dx in dx_cats:
            self.selenium.find_element_by_xpath(
                '//input[@value="{dx}"]'.format(dx=dx)).click()

        for tab_name in ['basics', 'h-p', 'physical-exam', 'assessment-plan',
                         'referraldischarge']:

            self.select_tab(tab_name)

            for key in wu_data:
                # these form elements are excluded from the form, so we 
                # shouldn't try to fill them out.
                if key in forms.WorkupForm.Meta.exclude:
                    continue

                try:
                    self.selenium.find_element_by_name(key).send_keys(
                        wu_data[key])
                except ElementNotVisibleException:
                    pass

        # scroll to the bottom of the page so we can click submit.
        self.selenium.execute_script(
            "window.scrollTo(0, document.body.scrollHeight);")

        if submit:
            self.selenium.find_element_by_xpath(
                '//input[@type="submit"]').click()

    def test_ok_wu_submit(self):
        '''
        We should be able to successfully submit a well-formatted workup
        '''

        # navigate a new workup for the first patient in the database
        pt_url = reverse('new-workup', args=(Patient.objects.first().pk,))
        self.selenium.get('%s%s' % (self.live_server_url, pt_url))

        wu_data = wu_dict()
        dx_cats = [models.DiagnosisType.objects.first().pk]
        self.fill_out_workup(wu_data, dx_cats=dx_cats)

        ai_url = reverse('new-action-item', args=(Patient.objects.first().pk,))
        self.assertEquals(
            self.selenium.current_url,
            '%s%s' % (self.live_server_url, ai_url))

    def test_tab_switch_on_error(self):
        '''
        Verify that, when an error is on a tab that's on the last tab,
        we switch to that tab.
        '''

        # navigate a new workup for the first patient in the database
        pt_url = reverse('new-workup', args=(Patient.objects.first().pk,))
        self.selenium.get('%s%s' % (self.live_server_url, pt_url))

        wu_data = wu_dict()
        self.fill_out_workup(wu_data, dx_cats=[])

        tab_class = self.selenium.find_element_by_xpath(
            '/html/body/div[2]/form/ul/li[1]').get_attribute("class")
        self.assertIn("active", tab_class)

        dx_class = self.selenium.find_element_by_xpath(
            '//div[@id="div_id_diagnosis_categories"]').get_attribute("class")
        self.assertIn("has-error", dx_class)

    def test_noninteger_weight_wu(self):
        '''
        Test that when a noninteger weight is given, that we properly present
        the error.
        '''

        # navigate a new workup for the first patient in the database
        new_wu_url = reverse('new-workup', args=(Patient.objects.first().pk,))
        self.selenium.get('%s%s' % (self.live_server_url, new_wu_url))

        wu_data = wu_dict()
        dx_cats = [models.DiagnosisType.objects.first().pk]
        wu_data['height'] = '13.6'

        self.fill_out_workup(wu_data, dx_cats=dx_cats)

        # 'has-error' should be in the class description of the div, since it's
        # got an invalid value.
        dx_class = self.selenium.find_element_by_xpath(
            '//div[@id="div_id_height"]').get_attribute("class")
        self.assertIn("has-error", dx_class.split())

        # since we should have a successful submission, we should redirect away
        self.assertNotEquals(
            self.selenium.current_url,
            '%s%s' % (self.live_server_url, new_wu_url))
