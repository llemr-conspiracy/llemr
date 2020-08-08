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


def note_check(note, author, clintype, pt_pk):
    """Helper method that verifies that a note is correctly written to the
    database. This should probably be broken out into its own unit test that
    directly interfaces with the form object.
    """

    assert note.author == author
    assert clintype == note.author_type
    assert note.patient.pk == pt_pk

    assert (now() - note.written_datetime).total_seconds() <= 10
    assert (now() - note.last_modified).total_seconds() <= 10


def build_provider(group_factories=None):

    if group_factories is None:
        group_factories = [user_factories.VolunteerGroupFactory]

    return user_factories.UserFactory(
        groups=[f() for f in group_factories]
    )

def log_in_provider(client, user):
    """Creates a provider and logs them in. Role defines their provider_type,
    default is all"""

    client.force_login(user)

    user.active_role = user.groups.first()
    client.session['active_role_set'] = True

    client.session.save()
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
    # fixtures = [BASIC_FIXTURE]
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
            patient=pt,
            due_date=now().today(),
            author=self.users[0]
        )

        # action item due yesterday
        factories.ActionItemFactory(
            patient=pt,
            due_date=yesterday,
            author=self.users[0]
        )

        # action item due tomorrow
        factories.ActionItemFactory(
            patient=pt,
            due_date=tomorrow,
            author=self.users[1]
        )

        # complete action item from yesterday
        factories.ActionItemFactory(
            patient=pt,
            due_date=yesterday,
            author=self.users[1],
            completion_date=now(),
            completion_author=self.users[1],
        )

    def test_sendemail(self):
        """Verifies that email is correctly being sent for incomplete,
        overdue action items
        """

        print([(i, u.email) for i, u in enumerate(self.users)])

        call_command('action_item_spam')

        # test that 1 message has been sent for the AI due yesterday and
        # today but only 1 email bc same pt/case manager
        assert len(mail.outbox) == 1

        # verify that subject is correct
        assert mail.outbox[0].subject == 'SNHC: Action Item Due'

        # verify that the 1 message is to user[0] and user[2] (second
        # case manager) and NOT user[1] and user[3]
        print(mail.outbox[0].to)
        assert set(mail.outbox[0].to) == set([self.users[0].email,
                                              self.users[2].email])


class ViewsExistTest(TestCase):
    # fixtures = [BASIC_FIXTURE]

    def setUp(self):
        self.user = user_factories.UserFactory(
            groups=[user_factories.VolunteerGroupFactory()]
        )
        self.user.save()

        self.client.force_login(self.user)
        s = self.client.session
        s['clintype_pk'] = self.user.groups.first().pk
        s.save()

        self.patient = factories.PatientFactory()

    def test_initial_config(self):
        session = self.client.session
        del session['clintype_pk']
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

        pt_urls_redirect = ['core:patient-activate-detail',
                            'core:patient-activate-home']

        pt = models.Patient.objects.first()

        for pt_url in pt_urls:
            response = self.client.get(reverse(pt_url, args=(pt.id,)))
            try:
                self.assertEqual(response.status_code, 200)
            except AssertionError as e:
                raise e

        for pt_url in pt_urls_redirect:
            response = self.client.get(reverse(pt_url, args=(pt.id,)))
            try:
                self.assertEqual(response.status_code, 302)
            except AssertionError as e:
                raise e

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


class ProviderCreateTest(TestCase):

    def setUp(self):
        log_in_provider(self.client, build_provider())

    def test_provider_creation(self):
        """Verify that, in the absence of a provider, a provider is created,
        and that it is created correctly."""

        final_url = reverse('core:all-patients')

        # verify: no provider -> create provider
        models.Provider.objects.all().delete()
        response = self.client.get(final_url)
        final_response_url = response.url
        self.assertRedirects(
            response, reverse('core:user-init') + '?next=' + final_url)

        n_provider = len(models.Provider.objects.all())

        # The data submitted by a User when creating the Provider.
        form_data = {
            'first_name': "John",
            'last_name': "James",
            'phone': "8888888888",
            'languages': models.Language.objects.first().pk,
            'gender': models.Gender.objects.first().pk,
            'clinical_roles': models.ProviderType.objects.first().pk,
        }
        response = self.client.post(response.url, form_data)
        # redirects anywhere; don't care where (would be the 'next' parameter)
        assert response.status_code == 302
        assert len(models.Provider.objects.all()) == n_provider + 1

        new_provider = list(models.Provider.objects.all())[-1]

        # verify the writethrough
        self.assertEqual(new_provider.name(), new_provider.associated_user.name)

        # now verify we're redirected
        response = self.client.get(final_url)
        assert response.status_code == 200

        # Test for proper resubmission behavior.
        n_provider = len(models.Provider.objects.all())
        # WebDriver().back()

        # POST a form with new names
        form_data['first_name'] = 'Janet'
        form_data['last_name'] = 'Jane'
        response = self.client.post(final_response_url, form_data)

        # Verify redirect anywhere; don't care where (would be 'next=')
        self.assertEqual(response.status_code, 302)

        # Verify that number of providers has not changed, and user's
        # names is still the original new_provider's names
        self.assertEqual(len(models.Provider.objects.all()), n_provider)
        self.assertEqual(new_provider.name(), new_provider.associated_user.name)

        # now verify we're redirected
        response = self.client.get(final_url)
        self.assertEqual(response.status_code, 200)


class IntakeTest(TestCase):
    # fixtures = [BASIC_FIXTURE]

    def setUp(self):
        log_in_provider(self.client, build_provider())

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

        print(response)

        assert response.status_code == 200
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
    # fixtures = [BASIC_FIXTURE]

    def setUp(self):
        self.coordinator = build_provider([user_factories.CaseManagerGroupFactory])
        self.provider = log_in_provider(self.client, self.coordinator)

    def test_action_item_completeable_functions(self):

        ai_inst = models.ActionInstruction.objects.create(
            instruction="Follow up on labs")
        ai = models.ActionItem.objects.create(
            instruction=ai_inst,
            due_date=now().today(),
            comments="",
            author=models.Provider.objects.first(),
            author_type=models.ProviderType.objects.first(),
            patient=models.Patient.objects.first())

        self.assertEqual(
            ai.attribution(),
            "Added by Jones, Tommy L. on %s" % now().date())

        ai.mark_done(self.coordinator)
        ai.save()

        assert ai.attribution() == (
            "Marked done by Jones, Tommy L. on %s" % now().date())

    def test_action_item_urls(self):
        pt = models.Patient.objects.first()

        ai_inst = models.ActionInstruction.objects.create(
            instruction="Follow up on labs")
        ai = models.ActionItem.objects.create(
            instruction=ai_inst,
            due_date=now().today(),
            comments="",
            author=models.Provider.objects.first(),
            author_type=models.ProviderType.objects.first(),
            patient=pt)

        response = self.client.get(
            reverse('core:patient-detail', args=(pt.id,)))
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
        assert reverse('core:patient-detail', args=(pt.id,)) in response.url
        assert not models.ActionItem.objects.first().done()

        assert \
            models.ActionItem.objects.first().written_datetime != \
            models.ActionItem.objects.first().last_modified
        assert prev_mod_datetime != \
            models.ActionItem.objects.first().last_modified

        # make sure updating the action items url works
        response = self.client.get(
            reverse('core:update-action-item', args=(ai.pk,)))
        assert response.status_code == 200

    def test_create_action_item(self):

        patient = models.Patient.objects.first()
        assert models.ActionItem.objects.count() == 0

        submitted_ai = {
            "instruction": models.ActionInstruction.objects.first().pk,
            "due_date": str(datetime.date.today() + datetime.timedelta(10)),
            "comments": "an arbitrary string comment"
        }

        url = reverse('core:new-action-item', kwargs={'pt_id': patient.id})
        response = self.client.post(url, submitted_ai)

        assert response.status_code == 302
        assert reverse('core:patient-detail', args=(1,)) in response.url
        assert models.ActionItem.objects.count() == 1

        new_ai = models.ActionItem.objects.first()

        submitted_ai['due_date'] = datetime.date(
            *([int(i) for i in submitted_ai['due_date'].split('-')]))

        for param in submitted_ai:
            assert str(submitted_ai[param]) == str(getattr(new_ai, param))

        note_check(new_ai,
                   self.provider,
                   models.ProviderType.objects.get(long_name='Coordinator'),
                   patient.id)


class ProviderUpdateTest(TestCase):
    # fixtures = [BASIC_FIXTURE]

    def setUp(self):
        self.provider = build_provider([user_factories.VolunteerGroupFactory])

    def test_require_providers_update(self):
        """Test that the require_providers_update() method sets all
        needs_update to True
        """

        # this line is repeated for every test instead of in a setUp
        # def so that we can store the provider variable

        log_in_provider(self.client, self.provider)
        for provider in models.Provider.objects.all():
            self.assertEqual(provider.needs_updating, False)

        models.require_providers_update()

        for provider in models.Provider.objects.all():
            self.assertEqual(provider.needs_updating, True)

    def test_redirect_and_form_submit(self):
        """Test correct redirect and form submit behavior
        """
        final_url = reverse('home')

        log_in_provider(self.client, self.provider)
        self.provider.languages.add(models.Language.objects.first())
        self.provider.save()

        initial_num_providers = models.Provider.objects.count()

        # Verify needs_update -> will redirect
        models.require_providers_update()
        assert \
            models.Provider.objects.get(pk=self.provider.pk).needs_updating is True

        response = self.client.get(reverse('home'), follow=True)
        self.assertRedirects(
            response, ''.join([reverse('core:provider-update'),
                               "?next=/dashboard/dispatch/"]))

        form_data = {
            'first_name': "John",
            'last_name': "James",
            'phone': "8888888888",
            'languages': [models.Language.objects.first().pk],
            'gender': models.Gender.objects.first().pk,
            'clinical_roles': [models.ProviderType.objects.get(
                short_name='Clinical').pk],
        }

        response = self.client.post(
            reverse('core:provider-update'),
            form_data,
            follow=True)

        # Redirects anywhere; don't care where (would be the 'next' parameter)
        # assert response.status_code == 302

        # Verify number of providers is still the same
        assert models.Provider.objects.count() == initial_num_providers

        # Verify write-through and no longer needs update
        provider = models.Provider.objects.get(pk=provider_pk)
        roles = [role.short_name for role
                 in getattr(provider, 'clinical_roles').all()]

        assert roles == ['Clinical']
        assert getattr(provider, 'phone') == '8888888888'
        assert getattr(provider, 'needs_updating') is False

        # Verify that accessing final url no longer redirects
        response = self.client.get(final_url, follow=True)

        with open('tmp.html', 'wb') as w:
            w.write(response.content)

        self.assertRedirects(
            response, reverse(settings.OSLER_DEFAULT_DASHBOARD))


class TestReferralPatientDetailIntegration(TestCase):
    """Tests integration of Action Items and Referral Followups in
    core:patient-detail."""

    # fixtures = [BASIC_FIXTURE]

    def setUp(self):
        log_in_provider(self.client, build_provider())

        self.contact_method = models.ContactMethod.objects.create(
            name="Carrier Pidgeon")

        self.pt = models.Patient.objects.create(
            first_name="Juggie",
            last_name="Brodeltein",
            middle_name="Bayer",
            phone='+49 178 236 5288',
            gender=models.Gender.objects.first(),
            address='Schulstrasse 9',
            city='Munich',
            state='BA',
            zip_code='63108',
            pcp_preferred_zip='63018',
            date_of_birth=datetime.date(1990, 1, 1),
            patient_comfortable_with_english=False,
            preferred_contact_method=self.contact_method,
        )

        self.pt.case_managers.add(models.Provider.objects.first())

        ai_inst = models.ActionInstruction.objects.create(
            instruction="Follow up on labs")

        self.tomorrow = now().date() + datetime.timedelta(days=1)
        self.yesterday = now().date() - datetime.timedelta(days=1)

        ai_prototype = {
            'instruction': ai_inst,
            'comments': "",
            'author_type': models.ProviderType.objects.first(),
            'patient': self.pt
        }

        # Action item due today
        ai_today = models.ActionItem.objects.create(
            due_date=now().date(),
            author=models.Provider.objects.first(),
            **ai_prototype
        )

        # Action item due yesterday
        ai_yesterday = models.ActionItem.objects.create(
            due_date=self.yesterday,
            author=models.Provider.objects.first(),
            **ai_prototype
        )

        # Action item due tomorrow
        ai_tomorrow = models.ActionItem.objects.create(
            due_date=self.tomorrow,
            author=models.Provider.objects.first(),
            **ai_prototype
        )

        # Complete action item from yesterday
        ai_complete = models.ActionItem.objects.create(
            due_date=self.yesterday,
            author=models.Provider.objects.first(),
            completion_date=now(),
            completion_author=models.Provider.objects.first(),
            **ai_prototype
        )

        self.reftype = models.ReferralType.objects.create(
            name="Specialty", is_fqhc=False)
        self.refloc = models.ReferralLocation.objects.create(
            name='COH', address='Euclid Ave.')
        self.refloc.care_availiable.add(self.reftype)

    def test_patient_detail(self):
        """ Creates several action items and referral followups to check if view
            is properly supplying Status, FQHC Referral Status, Referrals,
            Action Item totals, and Followup totals."""

        # Create follow up request due yesterday
        referral1 = Referral.objects.create(
            comments="Needs his back checked",
            status=Referral.STATUS_PENDING,
            kind=self.reftype,
            author=models.Provider.objects.first(),
            author_type=models.ProviderType.objects.first(),
            patient=self.pt
        )
        referral1.location.add(self.refloc)

        followup_request1 = FollowupRequest.objects.create(
            referral=referral1,
            contact_instructions="Call him",
            due_date=self.yesterday,
            author=models.Provider.objects.first(),
            author_type=models.ProviderType.objects.first(),
            patient=self.pt
        )

        # Create a second referral followup request due today
        fqhc_reftype = models.ReferralType.objects.create(
            name="FQHC", is_fqhc=True)
        fhc = models.ReferralLocation.objects.create(
            name="Family Health Center", address="Manchester Ave.")
        fhc.care_availiable.add(fqhc_reftype)

        referral2 = Referral.objects.create(
            comments="Connecting patient to FQHC",
            status=Referral.STATUS_PENDING,
            kind=fqhc_reftype,
            author=models.Provider.objects.first(),
            author_type=models.ProviderType.objects.first(),
            patient=self.pt
        )
        referral2.location.add(fhc)

        followup_request2 = FollowupRequest.objects.create(
            referral=referral2,
            contact_instructions="Call him",
            due_date=now().date(),
            author=models.Provider.objects.first(),
            author_type=models.ProviderType.objects.first(),
            patient=self.pt
        )

        # Check that patient detail properly renders
        url = reverse('core:patient-detail', args=(self.pt.id,))
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

        # Check patient status -- there is one action item and followup
        # request 1 day past due and one action item and followup
        # request due today
        expected_status = "Action items 1, 0, 0, 1 days past due"
        self.assertContains(response, expected_status)

        expected_fqhc_status = Referral.STATUS_PENDING
        self.assertContains(response, expected_fqhc_status)

        # Check that referral list contains description of both referrals
        self.assertContains(response, referral1)
        self.assertContains(response, referral2)

        # Verify that the correct amount of action items are present
        total_action_items = "Action Items (6 Total)"
        self.assertContains(response, total_action_items)
        # Sanity check
        incorrect_total_action_items = "Action Items (5 Total)"
        self.assertNotContains(response, incorrect_total_action_items)

        # Now complete followup request and see if page is properly updated
        successful_res = ContactResult.objects.create(
            name="Communicated health data with patient", patient_reached=True)

        # Complete followup request for first referral
        form_data = {
            'contact_method': self.contact_method,
            'contact_status': successful_res,
            'has_appointment': PatientContact.PTSHOW_YES,
            'appointment_location': [self.refloc.pk],
            'pt_showed': PatientContact.PTSHOW_YES,
            PatientContactForm.SUCCESSFUL_REFERRAL: True
        }

        # Check that form is valid
        form = PatientContactForm(data=form_data)
        self.assertEqual(form.is_valid(), True)

        # Verify that PatientContactForm has been submitted
        url = reverse('new-patient-contact', args=(self.pt.id,
                                                   referral1.id,
                                                   followup_request1.id))
        response = self.client.post(url, form_data)
        self.assertEqual(response.status_code, 302)

        # Finally check if the new patient detail page is updated
        url = reverse('core:patient-detail', args=(self.pt.id,))
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

        expected_status = "Action items 1, 0, 0 days past due"
        self.assertContains(response, expected_status)

        # Verify that the correct amount of action items are present
        total_action_items = "Action Items (6 Total)"
        self.assertContains(response, total_action_items)

        # Verify that the followup total has been updated
        expected_followups = "Followups (1)"
        self.assertContains(response, expected_followups)

        # There should now be 2 completed action items
        finished_action_items = "Completed Action Items (2)"
        self.assertContains(response, finished_action_items)

        # Verify that the template contains expected PatientContact description
        self.assertContains(response,
                            PatientContact.objects.first().short_text())
