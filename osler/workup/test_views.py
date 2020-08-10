from __future__ import unicode_literals

from builtins import range
from django.test import TestCase
from django.utils.timezone import now
from django.urls import reverse

from osler.core.models import Patient
from osler.core.tests.test_views import build_user, log_in_user

import osler.users.tests.factories as user_factories

from osler.workup import models
from osler.workup.tests import wu_dict

import pytest


class ViewsExistTest(TestCase):
    """
    Verify that views involving the workup are functioning.
    """
    fixtures = ['workup', 'core']



    def setUp(self):

        models.ClinicDate.objects.create(
            clinic_type=models.ClinicType.objects.first(),
            clinic_date=now().date())

        self.user = build_user()
        log_in_user(self.client, self.user)

        self.wu = models.Workup.objects.create(
            clinic_day=models.ClinicDate.objects.first(),
            chief_complaint="SOB",
            diagnosis="MI",
            HPI="A", PMH_PSH="B", meds="C", allergies="D", fam_hx="E",
            soc_hx="F", ros="", pe="", A_and_P="",
            author=self.user,
            author_type=self.user.groups.first(),
            patient=Patient.objects.first())

    def test_clindate_create_redirect(self):
        '''Verify that if no clindate exists, we're properly redirected to a
        clindate create page.'''

        # First delete clindate that's created in setUp.
        models.Workup.objects.all().delete()
        models.ClinicDate.objects.all().delete()

        pt = Patient.objects.first()

        pt_url = 'new-workup'
        response = self.client.get(reverse(pt_url, args=(pt.id,)))
        assert response.status_code == 302
        self.assertRedirects(response, reverse('new-clindate', args=(pt.id,)))

    def test_new_workup_view(self):

        pt = Patient.objects.first()
        response = self.client.get(reverse('new-workup', args=(pt.id,)))
        assert response.status_code == 200

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
                assert response.status_code == 200

    def test_workup_initial(self):

        pt = Patient.objects.first()

        date_string = self.wu.written_datetime.strftime("%B %d, %Y")
        heading_text = "Migrated from previous workup on %s. Please delete this heading and modify the following:\n\n" % date_string

        # TODO test use of settings.OSLER_WORKUP_COPY_FORWARD_FIELDS
        response = self.client.get(reverse('new-workup', args=(pt.id,)))
        assert response.context['form'].initial['PMH_PSH'] == heading_text + "B"
        assert response.context['form'].initial['meds'] == heading_text + "C"
        assert response.context['form'].initial['allergies'] == heading_text + "D"
        assert response.context['form'].initial['fam_hx'] == heading_text + "E"
        assert response.context['form'].initial['soc_hx'] == heading_text + "F"

    def test_workup_update(self):
        '''
        Updating should be possible always for attendings, only without
        attestation for non-attendings.
        '''
        
        # if the wu is unsigned, all can access update.
        for role in user_factories.all_roles:
            log_in_user(self.client, build_user([role]))
            response = self.client.get(
                reverse('workup-update', args=(self.wu.id,)))
            assert response.status_code == 200

        signer = build_user([user_factories.AttendingGroupFactory])
        self.wu.sign(signer, signer.groups.first())
        self.wu.save()

        # nonattesting cannot access while attesting can
        for role in user_factories.all_roles:
            log_in_user(self.client, build_user([role]))
            response = self.client.get(
                reverse('workup-update', args=(self.wu.id,)))
            if role in user_factories.attesting_roles:
                assert response.status_code == 200
            else:
                self.assertRedirects(response,
                    reverse('workup', args=(self.wu.id,)))


    def test_workup_signing(self):
        """Verify that singing is possible for attendings, and not for others.
        """

        wu_url = "workup-sign"

        # only attesting roles should be able to sign
        for role in user_factories.attesting_roles:
            assert not self.wu.signed()
            log_in_user(self.client, build_user([role]))
            response = self.client.get(reverse(wu_url, args=(self.wu.id,)))
            self.assertRedirects(response, reverse('workup', args=(self.wu.id,)),)
            is_attesting = role in user_factories.attesting_roles
            assert models.Workup.objects.get(pk=self.wu.id).signed() == is_attesting
            self.wu.signer = None
            self.wu.save()

    def donttest_workup_pdf(self):
        """Verify that pdf download with the correct name
        """

        wu_url = "workup-pdf"

        # nonattesting cannot export pdf while attesting can
        for role in user_factories.all_roles:
            log_in_user(self.client, build_user([role]))
            response = self.client.get(reverse(wu_url, args=(self.wu.id,)))
            if role in user_factories.attesting_roles:
                assert response.status_code == 200
            else:
                self.assertRedirects(response,
                    reverse('workup', args=(self.wu.id,)))

    def test_workup_submit(self):
        """verify we can submit a valid workup as a signer and nonsigner"""

        for role in user_factories.all_roles:
            user = build_user([role])
            log_in_user(self.client, user)
            pt_id = Patient.objects.first().pk

            wu_count = models.Workup.objects.all().count()
            wu_data = wu_dict(units=True)
            # wu_data['diagnosis_categories'] = [
            #     models.DiagnosisType.objects.first().pk]
            wu_data['clinic_day'] = wu_data['clinic_day'].pk

            r = self.client.post(
                reverse('new-workup', args=(pt_id,)),
                data=wu_data)
            self.assertRedirects(r, reverse("core:patient-detail", args=(pt_id,)))

            self.assertEqual(wu_count + 1, models.Workup.objects.all().count())
            self.assertEqual(
                models.Workup.objects.last().signed(),
                user.clinical_roles.first().signs_charts)

    def test_invalid_workup_submit_preserves_units(self):

        # first, craft a workup that has units, but fail to set the
        # diagnosis categories, so that it will fail to be accepted.
        wu_data = wu_dict(units=True)
        pt_id = Patient.objects.first().pk

        r = self.client.post(
            reverse('new-workup', args=(pt_id,)),
            data=wu_data)

        # verify we're bounced back to workup-create
        self.assertEqual(r.status_code, 200)
        self.assertTemplateUsed(r, 'workup/workup-create.html')
        self.assertFormError(r, 'form', 'diagnosis_categories',
                             'This field is required.')

        for unit in ['height_units', 'weight_units', 'temperature_units']:
            self.assertContains(r, '<input name="%s"' % (unit))

            self.assertEqual(
                r.context['form'][unit].value(),
                wu_data[unit])


class TestProgressNoteViews(TestCase):
    '''
    Verify that views involving the workup are functioning.
    '''
    fixtures = ['workup', 'core']

    def setUp(self):

        provider = build_user()
        log_in_user(self.client, provider)

        self.formdata = {
            'title': 'Depression',
            'text': 'so sad does testing work???',
            'patient': Patient.objects.first(),
            'author': provider,
            'author_type': ProviderType.objects.first()
        }

        models.ClinicDate.objects.create(
            clinic_type=models.ClinicType.objects.first(),
            clinic_date=now().date())

    def test_progressnote_urls(self):
        pt = Patient.objects.first()

        n_notes = models.ProgressNote.objects.count()

        url = reverse('new-progress-note', args=(pt.id,))
        response = self.client.get(url)
        assert response.status_code == 200

        response = self.client.post(url, self.formdata)
        self.assertRedirects(response,
                             reverse('core:patient-detail', args=(pt.id,)))
        assert models.ProgressNote.objects.count() == n_notes + 1

        response = self.client.get(
            reverse('progress-note-update',
                    args=(models.ProgressNote.objects.last().pk,)))
        assert response.status_code == 200

        self.formdata['text'] = 'actually not so bad'

        response = self.client.post(url, self.formdata)
        self.assertRedirects(response,
                             reverse('core:patient-detail', args=(pt.id,)))

    def test_progressnote_signing(self):
        """Verify that singing is possible for attendings and not for others.
        """

        sign_url = "progress-note-sign"

        pn = models.ProgressNote.objects.create(
            title='Depression',
            text='so sad does testing work???',
            patient=Patient.objects.first(),
            author=models.Provider.objects.first(),
            author_type=ProviderType.objects.first()
        )

        # Fresh notes should be unsigned
        self.assertFalse(pn.signed())

        # Providers with can_attend == False should not be able to sign
        for nonattesting_role in ["Preclinical", "Clinical", "Coordinator"]:
            log_in_user(self.client, build_user([nonattesting_role]))

            response = self.client.get(
                reverse(sign_url, args=(pn.id,)))
            self.assertRedirects(response,
                                 reverse('progress-note-detail',
                                         args=(pn.id,)))
            self.assertFalse(models.ProgressNote.objects
                             .get(pk=pn.id)
                             .signed())

        # Providers able to attend should be able to sign.
        log_in_user(self.client, build_user(["Attending"]))

        response = self.client.get(reverse(sign_url, args=(pn.id,)))
        self.assertRedirects(response, reverse('progress-note-detail',
                                               args=(pn.id,)),)
        # the pn has been updated, so we have to hit the db again.
        self.assertTrue(models.ProgressNote.objects.get(pk=pn.id).signed())
