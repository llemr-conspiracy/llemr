from __future__ import unicode_literals

from django.test import TestCase
from django.utils.timezone import now
from django.urls import reverse
from django.conf import settings

from osler.core.models import Patient
from osler.core.tests.test_views import build_user, log_in_user

import osler.users.tests.factories as user_factories

from osler.workup import models
from osler.workup.tests.tests import wu_dict, pn_dict


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

        self.wu = models.Workup.objects.create(**wu_dict(user=self.user))

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
        """Test that user can successfully access new workup page."""

        pt = Patient.objects.first()
        response = self.client.get(reverse('new-workup', args=(pt.id,)))
        assert response.status_code == 200

    def test_workup_urls(self):
        """Test creation of many workups."""

        wu_urls = ['workup',
                   'workup-update']

        for i in range(5):
            models.Workup.objects.bulk_create(
                [models.Workup(**wu_dict()) for i in range(5)])
            wu = models.Workup.objects.last()

            wu.diagnosis_categories.add(models.DiagnosisType.objects.first())

            for wu_url in wu_urls:
                response = self.client.get(reverse(wu_url, args=(wu.id,)))
                assert response.status_code == 200

    def test_workup_initial(self):

        pt = Patient.objects.first()

        date_string = self.wu.written_datetime.strftime("%B %d, %Y")
        heading_text = settings.OSLER_WORKUP_COPY_FORWARD_MESSAGE.format(date=date_string, contents="")

        response = self.client.get(reverse('new-workup', args=(pt.id,)))

        for field in settings.OSLER_WORKUP_COPY_FORWARD_FIELDS:
            assert response.context['form'].initial[field] == heading_text + getattr(self.wu, field)

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
        """Verify that signing is possible for attendings, and not for others.
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

    def test_workup_pdf(self):
        """Verify that pdf download with the correct name
        """

        wu_url = "workup-pdf"

        no_perm_group = user_factories.NoPermGroupFactory()
        pdf_perm_group = user_factories.PermGroupFactory(permissions=['workup.export_pdf_Workup'])

        for group in [no_perm_group, pdf_perm_group]:
            log_in_user(self.client, user_factories.UserFactory(groups=[group]))
            response = self.client.get(reverse(wu_url, args=(self.wu.id,)))
            assert response.status_code == 200 if group == pdf_perm_group else 403

    def test_workup_submit(self):
        """verify we can submit a valid workup as a signer and nonsigner"""

        for role in user_factories.all_roles:
            user = build_user([role])
            log_in_user(self.client, user)
            pt_id = Patient.objects.first().pk

            wu_count = models.Workup.objects.all().count()
            wu_data = wu_dict(units=True, clinic_day_pk=True, dx_category=True)

            response = self.client.post(
                reverse('new-workup', args=(pt_id,)),
                data=wu_data)
            self.assertRedirects(response, reverse("core:patient-detail", args=(pt_id,)))

            can_attest = role in user_factories.attesting_roles
            assert models.Workup.objects.all().count() == wu_count + 1
            assert models.Workup.objects.last().signed() == can_attest

    def test_invalid_workup_submit_preserves_units(self):

        # first, craft a workup that has units, but fail to set the
        # diagnosis categories, so that it will fail to be accepted.
        wu_data = wu_dict(units=True)
        pt_id = Patient.objects.first().pk

        response = self.client.post(
            reverse('new-workup', args=(pt_id,)),
            data=wu_data)

        # verify we're bounced back to workup-create
        assert response.status_code == 200
        self.assertTemplateUsed(response, 'workup/workup-create.html')
        self.assertFormError(response, 'form', 'diagnosis_categories',
                             'This field is required.')

        for unit in ['height_units', 'weight_units', 'temperature_units']:
            self.assertContains(response, '<input name="%s"' % (unit))

            assert response.context['form'][unit].value() == wu_data[unit]


class TestProgressNoteViews(TestCase):
    '''
    Verify that views involving the workup are functioning.
    '''
    fixtures = ['workup', 'core']

    def setUp(self):

        self.user = build_user()
        log_in_user(self.client, self.user)

        self.pn_data = pn_dict(user=self.user)

        models.ClinicDate.objects.create(
            clinic_type=models.ClinicType.objects.first(),
            clinic_date=now().date())

    def test_progressnote_urls(self):
        pt = Patient.objects.first()

        n_notes = models.ProgressNote.objects.count()

        pn_url = reverse('new-progress-note', args=(pt.id,))
        response = self.client.get(pn_url)
        assert response.status_code == 200

        response = self.client.post(pn_url, self.pn_data)
        self.assertRedirects(response,
                             reverse('core:patient-detail', args=(pt.id,)))
        assert models.ProgressNote.objects.count() == n_notes + 1

        response = self.client.get(
            reverse('progress-note-update',
                    args=(models.ProgressNote.objects.last().pk,)))
        assert response.status_code == 200

        self.pn_data['text'] = 'actually not so bad'

        response = self.client.post(pn_url, self.pn_data)
        self.assertRedirects(response,
                             reverse('core:patient-detail', args=(pt.id,)))

    def test_progressnote_signing(self):
        """Verify that singing is possible for attendings and not for others.
        """

        pn_url = "progress-note-sign"

        pn = models.ProgressNote.objects.create(**self.pn_data)

        # Fresh notes should be unsigned
        assert not pn.signed()

        # Providers with can_attend == False should not be able to sign
        for role in user_factories.all_roles:
            log_in_user(self.client, build_user([role]))
            response = self.client.get(reverse(pn_url, args=(pn.id,)))
            self.assertRedirects(response,
                                 reverse('progress-note-detail',
                                         args=(pn.id,)))
            can_attest = role in user_factories.attesting_roles
            assert models.ProgressNote.objects.get(pk=pn.id).signed() == can_attest
            pn.signer = None
            pn.save()
