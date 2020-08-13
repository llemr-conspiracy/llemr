import datetime
import json
import os

from django.test import TestCase
from django.urls import reverse
from django.utils.timezone import now
from django.core import mail
from django.core.management import call_command
from django.contrib.auth import get_user_model
from django.conf import settings

from osler.core import models
from osler.followup.models import ContactResult
from osler.referral.models import Referral, FollowupRequest, PatientContact
from osler.referral.forms import PatientContactForm

from osler.core.tests import factories
from osler.users.tests import factories as user_factories


def build_user(group_factories=None):

    if group_factories is None:
        group_factories = [user_factories.VolunteerGroupFactory]

    return user_factories.UserFactory(
        groups=[f() for f in group_factories]
    )

def log_in_user(client, user, group=None):
    """Logs a user in and sets their active role as the provided group, if
    supplied, otherwise their first group."""

    client.force_login(user)

    user.active_role = user.groups.first()

    session = client.session
    if not group:
        group = user.groups.first()
    assert user.groups.filter(pk=group.pk).exists()
    session['active_role_pk'] = group.pk
    session['active_role_name'] = group.name
    session.save()

    user.save()

    return user


def get_url_pt_list_identifiers(self, url):
    response = self.client.get(url)
    assert response.status_code == 200

    list_identifiers = []
    pt_lists = json.loads(response.context['lists'])
    for pt_list in pt_lists:
        list_identifiers.append(pt_list['identifier'])
    return list_identifiers


def is_uuid4(uuid):
    # TODO: this should be a regular expression probably.
    return (len(uuid.split('-')) == 5) and (len(uuid) == 36)


class SendEmailTest(TestCase):
    """Test custom django management command sendemail
    """
    def setUp(self):
        self.users = user_factories.UserFactory.create_batch(
            4,
            groups=[user_factories.CaseManagerGroupFactory()],
            provider=factories.ProviderFactory())

        pt = factories.PatientFactory(
            case_managers=[self.users[0], self.users[2]]
        )

        tomorrow = now().date() + datetime.timedelta(days=1)
        yesterday = now().date() - datetime.timedelta(days=1)

        # action item due today
        factories.ActionItemFactory(
            due_date=now().today(),
            author=self.users[0],
            author_type=self.users[0].groups.first(),
            patient=pt
        )

        # action item due yesterday
        factories.ActionItemFactory(
            due_date=yesterday,
            author=self.users[0],
            author_type=self.users[0].groups.first(),
            patient=pt
        )

        # action item due tomorrow
        factories.ActionItemFactory(
            due_date=tomorrow,
            author=self.users[1],
            author_type=self.users[1].groups.first(),
            patient=pt
        )

        # complete action item from yesterday
        factories.ActionItemFactory(
            due_date=yesterday,
            author=self.users[1],
            author_type=self.users[1].groups.first(),
            patient=pt,
            completion_date=now(),
            completion_author=self.users[1],
        )


    def test_sendemail(self):
        """Verifies that email is correctly being sent for incomplete,
        overdue action items
        """

        call_command('action_item_spam')

        # test that 1 message has been sent for the AI due yesterday and
        # today but only 1 email bc same pt/case manager
        assert len(mail.outbox) == 1

        # verify that subject is correct
        assert mail.outbox[0].subject == 'SNHC: Action Item Due'

        # verify that the 1 message is to user[0] and user[2] (second
        # case manager) and NOT user[1] and user[3]
        assert set(mail.outbox[0].to) == set([self.users[0].email,
                                              self.users[2].email])


class ViewsExistTest(TestCase):

    def setUp(self):
        self.user = build_user()
        log_in_user(self.client, self.user)

        self.patient = factories.PatientFactory()

    def test_initial_config(self):
        session = self.client.session
        del session['active_role_pk']
        del session['active_role_name']
        session.save()

        # verify: no clinic date -> create clinic date
        response = self.client.get(reverse('core:all-patients'))

        # verify: no provider -> provider creation
        # (now done in ProviderCreateTest)
        assert response.status_code == 302
        assert response.url == ''.join([reverse('core:choose-role'),
                                        "?next=",
                                        reverse('core:all-patients')])

        # verify: not logged in -> log in
        self.client.logout()
        response = self.client.get(reverse('core:all-patients'))
        self.assertRedirects(response,
                             ''.join([reverse('account_login'),
                                      '?next=',
                                      reverse('core:all-patients')]))

    def test_pt_urls(self):
        pt_urls = ['core:patient-detail',
                   'core:new-action-item',
                   'core:patient-update',
                   'followup-choice',
                   'new-clindate',
        ]

        pt = models.Patient.objects.first()

        for pt_url in pt_urls:
            response = self.client.get(reverse(pt_url, args=(pt.id,)))
            assert response.status_code == 200

    def test_provider_urls(self):
        response = self.client.get(reverse('core:user-init'))
        assert response.status_code == 200

    def test_document_urls(self):
        """Test the views showing documents

        Check the integrity of path saving in document creation (probably
        superfluous) and the UUID file naming.
        """

        url = reverse('core:new-document', args=(self.patient.pk,))

        response = self.client.get(url)
        assert response.status_code == 200

        doc = factories.DocumentFactory(
            author=self.user,
            author_type=self.user.groups.first())

        p = models.Document.objects.first().image.path
        assert open(p)
        assert doc.image.path == p
        assert os.path.isfile(p)
        assert is_uuid4(p.split("/")[-1].split(".")[0])

        url = reverse('core:document-detail', args=(doc.pk,))
        response = self.client.get(url)
        assert response.status_code == 200

    def test_inject_choose_clintype_malicious_next(self):

        # First, check that we successfully redirect to all patients.
        url = ''.join([
            reverse('core:choose-role'),
            "?next=",
            reverse('core:all-patients')
        ])

        form_data = {'radio-roles': self.user.groups.first().pk}
        response = self.client.post(url, form_data)

        self.assertRedirects(response, reverse('core:all-patients'))

        # Then, verfy that we will NOT redirect to google.com
        url = reverse('core:choose-role') + "?next=http://www.google.com/"

        form_data = {'radio-roles': self.user.groups.first().pk}
        response = self.client.post(url, form_data)

        assert response.status_code == 302
        assert response.url == reverse('home')


class IntakeTest(TestCase):

    def setUp(self):
        user = build_user()
        log_in_user(self.client, user)

        self.valid_pt_dict = {
            'first_name': "Juggie",
            'last_name': "Brodeltein",
            'middle_name': "Bayer",
            'phone': '+49 178 236 5288',
            'languages': [factories.LanguageFactory()],
            'gender': factories.GenderFactory(),
            'address': 'Schulstrasse 9',
            'city': 'Munich',
            'state': 'BA',
            'country': 'Germany',
            'zip_code': '63108',
            'pcp_preferred_zip': '63018',
            'date_of_birth': datetime.date(1990, 1, 1),
            'patient_comfortable_with_english': False,
            'ethnicities': [factories.EthnicityFactory()],
            'preferred_contact_method':
                factories.ContactMethodFactory()
        }

    def preintake_patient_with_collision(self):

        self.valid_pt_dict['gender'] = models.Gender.objects.first()
        del self.valid_pt_dict['preferred_contact_method']
        del self.valid_pt_dict['languages']
        del self.valid_pt_dict['ethnicities']

        pt = models.Patient.objects.create(**self.valid_pt_dict)

        url = reverse('core:preintake')
        response = self.client.post(
            url,
            {k: self.valid_pt_dict[k] for k
             in ['first_name', 'last_name']},
            follow=True)

        self.assertTemplateUsed(response, 'core/preintake-select.html')

        self.assertIn(pt, response.context_data['object_list'])

    def preintake_patient_no_collision(self):

        url = reverse('core:preintake')
        response = self.client.post(
            url,
            {k: self.valid_pt_dict[k] for k
             in ['first_name', 'last_name']},
            follow=True)

        self.assertTemplateUsed(response, 'core/intake.html')

        self.assertEqual(
            response.context_data['form']['first_name'].value(),
            self.valid_pt_dict['first_name'])

        self.assertEqual(
            response.context_data['form']['last_name'].value(),
            self.valid_pt_dict['last_name'])

    def test_can_intake_pt(self):

        n_pt = len(models.Patient.objects.all())

        submitted_pt = self.valid_pt_dict

        url = reverse('core:intake')

        response = self.client.post(url, submitted_pt)

        assert models.Patient.objects.count() == n_pt + 1

        new_pt = models.Patient.objects.last()
        for param in submitted_pt:
            try:
                self.assertEqual(str(submitted_pt[param]),
                                 str(getattr(new_pt, param)))
            except AssertionError:
                for x, y in zip(submitted_pt[param],
                                getattr(new_pt, param).all()):
                    self.assertEqual(x, y)

        # new patients should be marked as active by default
        assert new_pt.needs_workup


class ActionItemTest(TestCase):

    def setUp(self):
        self.coordinator = build_user([user_factories.CaseManagerGroupFactory])
        log_in_user(self.client, self.coordinator)

    def test_action_item_completeable_functions(self):

        ai = models.ActionItem.objects.create(
            author=self.coordinator,
            author_type=self.coordinator.groups.first(),
            due_date=(now() + datetime.timedelta(days=3)).date(),
            instruction=factories.ActionInstructionFactory(),
            patient=factories.PatientFactory()
        )

        self.assertEqual(
            ai.attribution(),
            "Added by %s on %s" %
            (self.coordinator.name, now().date())
        )

        coordinator2 = build_user([user_factories.CaseManagerGroupFactory])
        ai.mark_done(coordinator2)
        ai.save()

        assert ai.attribution() == (
            "Marked done by %s on %s" %
            (coordinator2.name, now().date()))

    def test_action_item_urls(self):
        ai = models.ActionItem.objects.create(
            instruction=factories.ActionInstructionFactory(),
            due_date=now().today(),
            author=self.coordinator,
            author_type=self.coordinator.groups.first(),
            patient=factories.PatientFactory()
        )

        response = self.client.get(
            reverse('core:patient-detail', args=(ai.patient.id,)))
        self.assertTemplateUsed(response, 'core/patient_detail.html')
        self.assertContains(
            response, reverse('core:done-action-item', args=(ai.id,)))

        # new action items should not be done
        assert not ai.done()

        # submit a request to mark the new ai as done. should redirect to
        # choose a followup type.
        response = self.client.get(
            reverse('core:done-action-item', args=(ai.id,)))
        assert response.status_code == 302
        assert reverse("new-actionitem-followup",
            kwargs={'pt_id':ai.patient.pk,'ai_id':ai.pk}) in response.url
        assert models.ActionItem.objects.first().done()
        assert \
            models.ActionItem.objects.first().written_datetime != \
            models.ActionItem.objects.first().last_modified

        # submit a request to reset the ai. should redirect to pt
        prev_mod_datetime = models.ActionItem.objects.first().last_modified
        response = self.client.get(
            reverse('core:reset-action-item', args=(ai.id,)))
        assert response.status_code == 302
        assert reverse('core:patient-detail',
                       args=(ai.patient.id,)) in response.url
        assert not models.ActionItem.objects.first().done()

        assert (
            models.ActionItem.objects.first().written_datetime !=
            models.ActionItem.objects.first().last_modified)
        assert prev_mod_datetime != \
            models.ActionItem.objects.first().last_modified

        # make sure updating the action items url works
        response = self.client.get(
            reverse('core:update-action-item', args=(ai.pk,)))
        assert response.status_code == 200

    def test_create_action_item(self):

        assert models.ActionItem.objects.count() == 0

        submitted_ai = {
            "instruction": factories.ActionInstructionFactory(),
            "due_date": str(datetime.date.today() + datetime.timedelta(10)),
            "comments": "an arbitrary string comment"
        }

        pt = factories.PatientFactory()
        url = reverse('core:new-action-item',
                      kwargs={'pt_id': pt.id})
        response = self.client.post(url, submitted_ai)

        assert response.status_code == 302
        assert reverse('core:patient-detail', args=(pt.id,)) in response.url
        assert models.ActionItem.objects.count() == 1

        new_ai = models.ActionItem.objects.first()

        submitted_ai['due_date'] = datetime.date(
            *([int(i) for i in submitted_ai['due_date'].split('-')]))

        for param in submitted_ai:
            assert str(submitted_ai[param]) == str(getattr(new_ai, param))

        assert new_ai.author.id == self.coordinator.id
        assert new_ai.author_type.id == self.coordinator.groups.first().id
        assert new_ai.patient.id == pt.id

        assert (now() - new_ai.written_datetime).total_seconds() <= 10
        assert (now() - new_ai.last_modified).total_seconds() <= 10


class ToggleStatusTest(TestCase):

    def setUp(self):
        self.coordinator = build_user([user_factories.CaseManagerGroupFactory])
        log_in_user(self.client, self.coordinator)

    def test_activate_urls(self):
        pt = factories.PatientFactory()

        response = self.client.get(reverse('core:patient-activate-detail', args=(pt.id,)))
        assert response.status_code == 302

        response = self.client.get(reverse('core:patient-activate-home', args=(pt.id,)))
        assert response.status_code == 302

    def test_activate_perms(self):
        pt = factories.PatientFactory()
        assert pt.needs_workup

        pt.toggle_active_status(self.coordinator, self.coordinator.groups.first())
        assert not pt.needs_workup

        attending = build_user([user_factories.AttendingGroupFactory])
        with self.assertRaises(ValueError):
            pt.toggle_active_status(attending, attending.groups.first())
        assert not pt.needs_workup

        volunteer = build_user([user_factories.VolunteerGroupFactory])
        with self.assertRaises(ValueError):
            pt.toggle_active_status(volunteer, volunteer.groups.first())
        assert not pt.needs_workup
        

