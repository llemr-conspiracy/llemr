# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import datetime
from django.utils.timezone import now

from django.test import TestCase, override_settings
from django.core.urlresolvers import reverse
from django.conf import settings

from pttrack.test_views import log_in_provider, build_provider
from pttrack.models import (Gender, Patient, ContactMethod)

from workup.models import ClinicDate, ClinicType, Workup


def dewhitespace(s):
    return "".join(s.split())


class TestOtherDashboard(TestCase):

    fixtures = ['pttrack', 'workup']

    def setUp(self):

        self.clinical_student = build_provider(
            roles=["Clinical"], email='user2@gmail.com')
        log_in_provider(self.client, self.clinical_student)

    def test_root_redirect(self):

        response = self.client.get(reverse('root'), follow=True)
        self.assertTemplateUsed(response, 'pttrack/patient_list.html')


class TestAttendingDashboard(TestCase):

    fixtures = ['pttrack', 'workup']

    def setUp(self):

        # build an attending and a clinical student
        self.attending = build_provider(roles=["Attending"],
                                        email='user1@gmail.com')
        self.clinical_student = build_provider(
            roles=["Clinical"], email='user2@gmail.com')
        log_in_provider(self.client, self.attending)

        self.wu_info = dict(
            chief_complaint="SOB", diagnosis="MI", HPI="A", PMH_PSH="B",
            meds="C", allergies="D", fam_hx="E", soc_hx="F", ros="", pe="",
            A_and_P="")

        # prepare a patient with an unsigned wu today, in addition to
        # what comes in in the fixture
        self.clinic_today = ClinicDate.objects.create(
            clinic_type=ClinicType.objects.first(),
            clinic_date=now().date())

        self.pt2 = Patient.objects.create(
            first_name="Arthur", last_name="Miller", middle_name="",
            phone='+49 178 236 5288', gender=Gender.objects.first(),
            address='Schulstrasse 9', city='Munich', state='BA',
            zip_code='63108', pcp_preferred_zip='63018',
            date_of_birth=datetime.date(1994, 1, 22),
            patient_comfortable_with_english=False,
            preferred_contact_method=ContactMethod.objects.first(),
        )
        self.wu2 = Workup.objects.create(
            clinic_day=self.clinic_today,
            author=self.clinical_student,
            author_type=self.clinical_student.clinical_roles.first(),
            patient=self.pt2,
            **self.wu_info)

    def test_root_redirect(self):

        response = self.client.get(reverse('root'), follow=True)
        self.assertTemplateUsed(response, 'dashboard/dashboard-attending.html')

    def test_pt_without_note(self):
        response = self.client.get(reverse('dashboard-attending'))

        self.assertEqual(
            len(response.context['no_note_patients']),
            1)
        self.assertEqual(
            response.context['no_note_patients'][0],
            Patient.objects.first())

    def test_pt_without_note_and_pt_unsigned(self):

        # assign wu2 to our attending
        self.wu2.attending = self.attending
        self.wu2.save()

        # prepare a patient with an unsigned wu today, NOT assigned to
        # our attending
        pt3 = Patient.objects.create(
            first_name="John", last_name="Doe", middle_name="",
            phone='454545', gender=Gender.objects.first(),
            address='A', city='B', state='C',
            zip_code='12345', pcp_preferred_zip='12345',
            date_of_birth=datetime.date(1992, 4, 22),
            patient_comfortable_with_english=False,
            preferred_contact_method=ContactMethod.objects.first(),
        )
        wu3 = Workup.objects.create(
            clinic_day=self.clinic_today,
            author=self.clinical_student,
            author_type=self.clinical_student.clinical_roles.first(),
            patient=pt3,
            **self.wu_info)

        response = self.client.get(reverse('dashboard-attending'))

        # we should have one no note patient
        self.assertEqual(
            len(response.context['no_note_patients']),
            1)
        self.assertEqual(
            response.context['no_note_patients'][0],
            Patient.objects.first())

        # and one clinic day
        self.assertEqual(len(response.context['clinics']), 1)
        # with two patients
        self.assertContains(response, reverse('patient-detail',
                                              args=(self.pt2.pk,)))
        self.assertContains(response, reverse('patient-detail',
                                              args=(pt3.pk,)))
        # both of which are marked as unattested
        self.assertContains(response, '<tr  class="warning" >', count=2)

        wu3.sign(self.attending.associated_user)
        wu3.save()

        response = self.client.get(reverse('dashboard-attending'))

        # still one clinic day
        self.assertEqual(len(response.context['clinics']), 1)
        # with two patients
        self.assertContains(response, reverse('patient-detail',
                                              args=(self.pt2.pk,)))
        self.assertContains(response, reverse('patient-detail',
                                              args=(pt3.pk,)))
        # ONE of which are marked as unattested
        self.assertContains(response, '<tr  class="warning" >', count=1)

    @override_settings(OSLER_CLINIC_DAYS_PER_PAGE=3)
    def test_dashboard_pagination(self):
        response = self.client.get(reverse('dashboard-attending'))

        # since we're on the first page, the "back" pagination button
        # should be disabled
        self.assertIn(
            dewhitespace('''
                <li class="disabled"><a aria-label="Previous">
                    <span aria-hidden="true">&laquo;</span>
                </a></li>'''),
            dewhitespace(response.content.decode('ascii')))
        # since there's only one page, the "forward" pagination button
        # should be disabled
        self.assertIn(
            dewhitespace('''
                <li class="disabled"> <a aria-label="Next">
                    <span aria-hidden="true">&raquo;</span>
                </a> </li>'''),
            dewhitespace(response.content.decode('ascii')))

        # since there's only one page, only one page marker should be shown
        self.assertContains(
            response, '<a href="?page=', count=1)

        for i in range(5):
            cd = ClinicDate.objects.create(
                clinic_date=datetime.date(2001, i + 1, 1),
                clinic_type=ClinicType.objects.first())
            pt = Patient.objects.create(
                first_name="John", last_name="Doe", middle_name="",
                phone='454545', gender=Gender.objects.first(),
                address='A', city='B', state='C',
                zip_code='12345', pcp_preferred_zip='12345',
                date_of_birth=datetime.date(1992, i + 3, 22),
                patient_comfortable_with_english=False,
                preferred_contact_method=ContactMethod.objects.first(),
            )
            Workup.objects.create(
                attending=self.attending,
                clinic_day=cd,
                author=self.clinical_student,
                author_type=self.clinical_student.clinical_roles.first(),
                patient=pt,
                **self.wu_info)

        response = self.client.get(reverse('dashboard-attending'))

        # now we should have two pages
        self.assertContains(
            response, '<a href="?page=', count=2)
        # since we're on the first page, the "back" pagination button
        # should still be disabled
        self.assertIn(
            dewhitespace('''
                <li class="disabled"><a aria-label="Previous">
                    <span aria-hidden="true">&laquo;</span>
                </a></li>'''),
            dewhitespace(response.content.decode('ascii')))
        # since there's only one page, the "forward" pagination button
        # should be disabled
        self.assertIn(
            dewhitespace('''
              <li><a href="?page=2" aria-label="Next">
                <span aria-hidden="true">&raquo;</span>
              </a></li>'''),
            dewhitespace(response.content.decode('ascii')))

    @override_settings(OSLER_CLINIC_DAYS_PER_PAGE=3)
    def test_dashboard_page_out_of_range(self):

        for i in range(10):
            cd = ClinicDate.objects.create(
                clinic_date=datetime.date(2001, i + 1, 1),
                clinic_type=ClinicType.objects.first())
            pt = Patient.objects.create(
                first_name="John", last_name="Doe", middle_name="",
                phone='454545', gender=Gender.objects.first(),
                address='A', city='B', state='C',
                zip_code='12345', pcp_preferred_zip='12345',
                date_of_birth=datetime.date(1992, i + 3, 22),
                patient_comfortable_with_english=False,
                preferred_contact_method=ContactMethod.objects.first(),
            )
            Workup.objects.create(
                attending=self.attending,
                clinic_day=cd,
                author=self.clinical_student,
                author_type=self.clinical_student.clinical_roles.first(),
                patient=pt,
                **self.wu_info)

        response = self.client.get(reverse('dashboard-attending') +
                                   '?page=999')

        n_pages = (ClinicDate.objects.count() //
                   settings.OSLER_CLINIC_DAYS_PER_PAGE)

        # since we're on the last page, the "back" pagination button
        # should be enabled (i.e. no 'class="disabled"')
        self.assertIn(
            dewhitespace('''
                <a href="?page=%s" aria-label="Previous">
                    <span aria-hidden="true">&laquo;
                ''' % n_pages),
            dewhitespace(response.content.decode('ascii')))
        # since there's only one page, the "forward" pagination button
        # should be disabled
        self.assertIn(
            dewhitespace('''
                <li class="disabled"> <a aria-label="Next">
                    <span aria-hidden="true">&raquo;</span>
                </a> </li>'''),
            dewhitespace(response.content.decode('ascii')))
