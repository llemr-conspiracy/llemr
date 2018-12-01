from django.test import TestCase
from django.utils.timezone import now
from django.core.urlresolvers import reverse

from pttrack.models import Patient, ProviderType
from pttrack.test_views import build_provider, log_in_provider

from . import models
from .tests import wu_dict


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

    def test_progressnote_urls(self):
        url = reverse('new-progress-note', args=(1,))
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

        form_data = {
            'title': 'Depression',
            'text': 'so sad does testing work???',
            'patient': Patient.objects.get(id=1),
            'author': models.Provider.objects.get(id=1),
            'author_type': ProviderType.objects.first()
        }

        response = self.client.post(url, form_data)
        self.assertRedirects(response, reverse('patient-detail', args=(1,)))

        url = reverse('progress-note-update', args=(1,))
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

        form_data['text'] = 'actually not so bad'

        response = self.client.post(url, form_data)
        self.assertRedirects(
            response, reverse('progress-note-detail', args=(1,)))

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

        # TODO test use of settings.OSLER_WORKUP_COPY_FORWARD_FIELDS
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

    def test_workup_submit(self):
        """verify we can submit a valid workup as a signer and nonsigner"""

        for provider_type in ["Attending", "Clinical"]:
            provider = build_provider([provider_type])
            log_in_provider(self.client, provider)
            pt_id = Patient.objects.first().pk

            wu_count = models.Workup.objects.all().count()
            wu_data = wu_dict(units=True)
            wu_data['diagnosis_categories'] = [
                models.DiagnosisType.objects.first().pk]
            wu_data['clinic_day'] = wu_data['clinic_day'].pk

            r = self.client.post(
                reverse('new-workup', args=(pt_id,)),
                data=wu_data)

            self.assertRedirects(r, reverse("patient-detail", args=(pt_id,)))
            self.assertEqual(wu_count + 1, models.Workup.objects.all().count())
            self.assertEqual(
                models.Workup.objects.last().signed(),
                provider.clinical_roles.first().signs_charts)
