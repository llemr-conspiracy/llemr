from django.test import TestCase
from .  import models
from . import followup_models
from . import forms
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User
from django.utils.timezone import now
from django.core.files import File
import datetime

# pylint: disable=invalid-name
# Whatever, whatever. I name them what I want.

BASIC_FIXTURE = 'basic_fixture'

def note_check(test, note, client, pt_pk):
    test.assertEquals(note.author.pk,
                      int(client.session['_auth_user_id']))

    test.assertEquals(client.session['clintype_pk'],
                      note.author_type.pk)

    test.assertEquals(note.patient.pk, pt_pk)

    test.assertLessEqual((now() - note.written_datetime).total_seconds(),
                         10)
    test.assertLessEqual((now() - note.last_modified).total_seconds(), 10)


def build_provider_and_log_in(client, roles=[]):
    ''' Creates a provider and logs them in. Role defines their provider_type, default is all '''

    if roles == []:
        roles = ["Coordinator", "Attending", "Clinical", "Preclinical"]

    user = User.objects.create_user('tljones', 'tommyljones@gmail.com',
                                    'password')
    user.save()

    g = models.Gender.objects.all()[0]
    models.Provider.objects.create(
        first_name="Tommy", middle_name="Lee", last_name="Jones",
        phone="425-243-9115", gender=g, associated_user=user)

    for role in roles:
        for ptype in models.ProviderType.objects.all():
            if ptype.short_name == role:
                user.provider.clinical_roles.add(ptype)

    client.login(username=user.username, password='password')

    session = client.session
    session['clintype_pk'] = user.provider.clinical_roles.all()[0].pk
    session.save()


class ViewsExistTest(TestCase):
    fixtures = [BASIC_FIXTURE]

    def setUp(self):

        models.ClinicType.objects.create(name="Basic Care Clinic")

        models.ClinicDate.objects.create(
            clinic_type=models.ClinicType.objects.all()[0],
            clinic_date=now().date(),
            gcal_id="tmp")

        build_provider_and_log_in(self.client)

    def test_basic_urls(self):
        basic_urls = ["home",
                      "all-patients",
                      "intake"]

        for basic_url in basic_urls:
            response = self.client.get(reverse(basic_url))
            self.assertEqual(response.status_code, 200)

    def test_initial_config(self):
        session = self.client.session
        del session['clintype_pk']
        session.save()

        # verify: no clinic date -> create clinic date
        response = self.client.get(reverse('all-patients'))
        self.assertRedirects(response,
                             reverse('choose-clintype')+"?next="+reverse('all-patients'))

        # verify: no provider -> provider creation
        # (now done in ProviderCreateTest)

        # verify: not logged in -> log in
        self.client.logout()
        response = self.client.get(reverse('all-patients'))
        self.assertRedirects(response, reverse('login')+'?next='+reverse('all-patients'))

    def test_pt_urls(self):
        pt_urls = ['patient-detail',
                   "new-clindate",
                   'new-action-item',
                   'followup-choice',
                   'new-workup',
                   'patient-update']
        pt = models.Patient.objects.all()[0]

        for pt_url in pt_urls:
            response = self.client.get(reverse(pt_url, args=(pt.id,)))
            try:
                self.assertEqual(response.status_code, 200)
            except AssertionError as e:
                print pt_url
                print response
                raise e

    def test_provider_urls(self):
        response = self.client.get(reverse('new-provider'))
        self.assertEqual(response.status_code, 200)

    def test_clindate_create_redirect(self):
        '''Verify that if no clindate exists, we're properly redirected to a
        clindate create page.'''

        # First delete clindate that's created in setUp.
        models.ClinicDate.objects.all().delete()

        pt = models.Patient.objects.all()[0]

        pt_url = 'new-workup'
        response = self.client.get(reverse(pt_url, args=(pt.id,)))
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse('new-clindate', args=(pt.id,)), response.url)

    def test_workup_urls(self):
        wu_urls = ['workup',
                   'workup-update']

        # test the creation of many workups, just in case.
        for i in range(101):
            wu = models.Workup.objects.create(
                clinic_day=models.ClinicDate.objects.all()[0],
                chief_complaint="SOB",
                diagnosis="MI",
                HPI="", PMH_PSH="", meds="", allergies="", fam_hx="", soc_hx="",
                ros="", pe="", A_and_P="",
                author=models.Provider.objects.all()[0],
                author_type=models.ProviderType.objects.all()[0],
                patient=models.Patient.objects.all()[0])

            wu.diagnosis_categories.add(models.DiagnosisType.objects.all()[0])

            for wu_url in wu_urls:
                response = self.client.get(reverse(wu_url, args=(wu.id,)))
                self.assertEqual(response.status_code, 200)

    def test_workup_signing(self):

        wu_url = "workup-sign"

        wu = models.Workup.objects.create(
            clinic_day=models.ClinicDate.objects.all()[0],
            chief_complaint="SOB",
            diagnosis="MI",
            HPI="", PMH_PSH="", meds="", allergies="", fam_hx="", soc_hx="",
            ros="", pe="", A_and_P="",
            author=models.Provider.objects.all()[0],
            author_type=models.ProviderType.objects.all()[0],
            patient=models.Patient.objects.all()[0])

        wu.diagnosis_categories.add(models.DiagnosisType.objects.all()[0])
        wu.save()

        # Fresh workups should be unsigned
        self.assertFalse(wu.signed())

        # Providers with can_attend == False should not be able to sign
        models.Provider.objects.all()[0].can_attend = False

        response = self.client.get(reverse(wu_url, args=(wu.id,)))
        self.assertEqual(response.status_code, 302)
        self.assertFalse(wu.signed())

        # Providers able to attend should be able to sign.
        models.Provider.objects.all()[0].can_attend = True

        response = self.client.get(reverse(wu_url, args=(wu.id,)))
        self.assertEqual(response.status_code, 302)
        self.assertFalse(wu.signed())

    def test_document_urls(self):
        '''
        Test the views showing documents, as well as the integrity of path
        saving in document creation (probably superfluous).
        '''
        import os

        self.test_img = 'media/test.jpg'

        url = reverse('new-document', args=(1,))

        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        dtype = models.DocumentType.objects.create(name="Silly Picture")

        doc = models.Document.objects.create(
            title="who done it?",
            comments="Pictured: silliness",
            document_type=dtype,
            image=File(open(self.test_img)),
            patient=models.Patient.objects.get(id=1),
            author=models.Provider.objects.get(id=1),
            author_type=models.ProviderType.objects.all()[0])

        p = models.Document.objects.get(id=1).image.path
        random_name = p.split("/")[-1]
        random_name = random_name.split(".")[0]
        self.failUnless(open(p), 'file not found')
        self.assertEqual(doc.image.path, p)
        self.assertTrue(os.path.isfile(p))

        # Checking to make sure the path is 48 characters (the length of the random password

        self.assertEqual(len(random_name), 48)


        url = reverse('document-detail', args=(1,))
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

        # test the creation of many documents, just in case.
        for i in range(101):
            doc = models.Document.objects.create(
                title="who done it? "+str(i),
                comments="Pictured: silliness",
                document_type=dtype,
                image=File(open(self.test_img)),
                patient=models.Patient.objects.get(id=1),
                author=models.Provider.objects.get(id=1),
                author_type=models.ProviderType.objects.all()[0])

            p = models.Document.objects.get(id=doc.pk).image.path
            random_name = p.split("/")[-1]
            random_name = random_name.split(".")[0]
            self.failUnless(open(p), 'file not found')
            self.assertEqual(doc.image.path, p)
            self.assertTrue(os.path.isfile(p))

            # Checking to make sure the path is 48 characters (the length of the random password

            self.assertEqual(len(random_name), 48)

            url = reverse('document-detail', args=(doc.pk,))
            response = self.client.get(url)
            self.assertEqual(response.status_code, 200)

            url = reverse('document-detail', args=(doc.pk,))
            response = self.client.get(url)
            self.assertEqual(response.status_code, 200)

            os.remove(p)
            self.assertFalse(os.path.isfile(p))


class ProviderCreateTest(TestCase):
    fixtures = [BASIC_FIXTURE]

    def setUp(self):
        build_provider_and_log_in(self.client)

    def test_provider_creation(self):
        '''Verify that, in the absence of a provider, a provider is created,
        and that it is created correctly.'''

        final_url = reverse('all-patients')

        # verify: no provider -> create provider
        models.Provider.objects.all().delete()
        response = self.client.get(final_url)
        self.assertRedirects(response, reverse('new-provider')+'?next='+final_url)

        n_provider = len(models.Provider.objects.all())

        # The data submitted by a User when creating the Provider.
        form_data = {
            'first_name': "John",
            'last_name': "James",
            'phone': "8888888888",
            'languages': models.Language.objects.all()[0].pk,
            'gender': models.Gender.objects.all()[0].pk,
            'provider_email': "jj@wustl.edu",
            'clinical_roles': models.ProviderType.objects.all()[0].pk,
        }

        response = self.client.post(response.url, form_data)
        # redirects anywhere; don't care where (would be the 'next' parameter)
        self.assertEqual(response.status_code, 302)
        self.assertEquals(len(models.Provider.objects.all()), n_provider + 1)

        new_provider = list(models.Provider.objects.all())[-1]

        # verify the writethrough
        for name in ['first_name', 'last_name']:
            self.assertEquals(getattr(new_provider, name),
                              getattr(new_provider.associated_user, name))

        # now verify we're redirected
        response = self.client.get(final_url)
        self.assertEquals(response.status_code, 200)


class FollowupTest(TestCase):
    fixtures = [BASIC_FIXTURE]

    def setUp(self):
        build_provider_and_log_in(self.client)


    def test_followup_view_urls(self):

        pt = models.Patient.objects.all()[0]

        method = models.ContactMethod.objects.create(name="Carrier Pidgeon")
        res = followup_models.ContactResult(name="Fisticuffs")
        reftype = models.ReferralType.objects.create(name="Chiropracter")
        aptloc = models.ReferralLocation.objects.create(
            name="Franklin's Back Adjustment",
            address="1435 Sillypants Drive")
        reason = followup_models.NoAptReason.objects.create(
            name="better things to do")

        for i in range(101):
            # General Followup
            gf = followup_models.GeneralFollowup.objects.create(
                contact_method=method,
                contact_resolution=res,
                author=models.Provider.objects.all()[0],
                author_type=models.ProviderType.objects.all()[0],
                patient=pt)

            url = reverse('followup', kwargs={"pk": gf.id, "model": 'General'})
            response = self.client.get(url)
            self.assertEqual(response.status_code, 200)

            # Lab Followup
            lf = followup_models.LabFollowup.objects.create(
                contact_method=method,
                contact_resolution=res,
                author=models.Provider.objects.all()[0],
                author_type=models.ProviderType.objects.all()[0],
                patient=pt,
                communication_success=True)

            url = reverse('followup', kwargs={"pk": lf.id, "model": 'Lab'})
            response = self.client.get(url)
            self.assertEqual(response.status_code, 200)

            # Vaccine Followup
            vf = followup_models.VaccineFollowup.objects.create(
                contact_method=method,
                contact_resolution=res,
                author=models.Provider.objects.all()[0],
                author_type=models.ProviderType.objects.all()[0],
                patient=pt,
                subsq_dose=False)

            url = reverse('followup', kwargs={"pk": vf.id, "model": 'Vaccine'})
            response = self.client.get(url)
            self.assertEqual(response.status_code, 200)

            # Referral Followup
            rf = followup_models.ReferralFollowup.objects.create(
                contact_method=method,
                contact_resolution=res,
                author=models.Provider.objects.all()[0],
                author_type=models.ProviderType.objects.all()[0],
                patient=pt,
                referral_type=reftype,
                has_appointment=False,
                apt_location=aptloc,
                noapt_reason=reason)

            url = reverse('followup',
                          kwargs={"pk": rf.id, "model": 'Referral'})
            response = self.client.get(url)
            self.assertEqual(response.status_code, 200)

    def test_followup_create_urls(self):

        pt = models.Patient.objects.all()[0]

        for fu_type in ["labs", "referral", "general", "vaccine"]:
            url = reverse("new-followup",
                          kwargs={"pt_id": pt.id, 'ftype': fu_type.lower()})

            response = self.client.get(url)
            self.assertEquals(response.status_code, 200)

        url = reverse("followup", kwargs={"pk": pt.id, "model": "Lab"})

    def test_create_followups(self):

        attempt_again_cr = followup_models.ContactResult.objects.create(
            name="didn't reach the pt",
            attempt_again=True)
        no_attempt_again_cr = followup_models.ContactResult.objects.create(
            name="totally reached the pt",
            attempt_again=False)

        # Try creating a followup that requires re-contacts and one that does
        # not. Verification for correctness of the redirect is in verify_fu
        for contact_result in [attempt_again_cr, no_attempt_again_cr]:
            submitted_gen_fu = {
                "contact_method":
                    models.ContactMethod.objects.all()[0].pk,
                "contact_resolution": contact_result,
                "comments": ""
                }

            self.verify_fu(followup_models.GeneralFollowup, 'general',
                           submitted_gen_fu)

            submitted_vacc_fu = dict(submitted_gen_fu)
            submitted_vacc_fu['subsq_dose'] = True
            submitted_vacc_fu['dose_date'] = str(datetime.date.today())

            self.verify_fu(followup_models.VaccineFollowup, 'vaccine',
                           submitted_vacc_fu)

            submitted_lab_fu = dict(submitted_gen_fu)
            submitted_lab_fu["communication_success"] = True

            self.verify_fu(followup_models.LabFollowup, 'labs',
                           submitted_lab_fu)

            submitted_ref_fu = dict(submitted_gen_fu)
            submitted_ref_fu.update(
                {"referral_type" : models.ReferralType.objects.all()[0].pk,
                 "has_appointment": True,
                 'apt_location': models.ReferralLocation.objects.all()[0].pk,
                 'pt_showed': "Yes",
                 'noapt_reason': "",
                 'noshow_reason': "",
                })

            self.verify_fu(followup_models.ReferralFollowup, 'referral',
                           submitted_ref_fu)

    def test_follwup_error(self):
        pt = models.Patient.objects.all()[0]

        method = models.ContactMethod.objects.create(name="Carrier Pidgeon")
        res1 = followup_models.ContactResult.objects.create(name="DiggleJiggle", patient_reached = True)
        res2 = followup_models.ContactResult.objects.create(name="Jigglewiggle", patient_reached = False)
        reftype = models.ReferralType.objects.create(name="Chiropracter")
        aptloc = models.ReferralLocation.objects.create(
            name="Franklin's Back Adjustment",
            address="1435 Sillypants Drive")
        reason = followup_models.NoAptReason.objects.create(
            name="better things to do")

        rf1 = {
            'contact_method': method,
            'contact_resolution': res1,
            'author': models.Provider.objects.all()[0],
            'author_type': models.ProviderType.objects.all()[0],
            'patient': pt,
            'referral_type': reftype,
            'has_appointment': False,
            'apt_location': aptloc,
            'noapt_reason': reason}

        rf2 = {
            'contact_method': method,
            'contact_resolution': res1,
            'author': models.Provider.objects.all()[0],
            'author_type': models.ProviderType.objects.all()[0],
            'patient': pt,
            'referral_type': reftype,
            'has_appointment': False}

        rf3 = {
            'contact_method': method,
            'contact_resolution': res2,
            'author': models.Provider.objects.all()[0],
            'author_type': models.ProviderType.objects.all()[0],
            'patient': pt,
            'referral_type': reftype,
            'has_appointment': False}

        form1 = forms.ReferralFollowup(data=rf1)
        form2 = forms.ReferralFollowup(data=rf2)
        form3 = forms.ReferralFollowup(data=rf3)

        self.assertEqual(form1['noapt_reason'].errors, [])
        self.assertNotEqual(form2['noapt_reason'].errors, [])
        self.assertEqual(form3['noapt_reason'].errors, [])


    def verify_fu(self, fu_type, ftype, submitted_fu):

        pt = models.Patient.objects.all()[0]

        n_followup = len(fu_type.objects.all())

        url = reverse('new-followup', kwargs={"pt_id": pt.id,
                                              "ftype": ftype})
        response = self.client.post(url, submitted_fu)

        self.assertEqual(response.status_code, 302)

        if submitted_fu["contact_resolution"].attempt_again:
            self.assertRedirects(response,
                                 reverse("new-action-item", args=(pt.id,)))
        else:
            self.assertRedirects(response,
                                 reverse('patient-detail', args=(pt.id,)))

        self.assertEquals(len(fu_type.objects.all()), n_followup + 1)

        # this should get the most recently created followup, which should be
        # the one we just posted to create
        new_fu = sorted(fu_type.objects.all(), key=lambda(fu): fu.written_datetime)[-1]

        # make sure that all of the parameters in the submitted fu make it
        # into the object.
        for param in submitted_fu:
            if submitted_fu[param]:
                try:
                    self.assertEquals(str(submitted_fu[param]),
                                      str(getattr(new_fu, param)))
                except AssertionError:
                    self.assertEquals(submitted_fu[param],
                                      getattr(new_fu, param).pk)


class IntakeTest(TestCase):
    fixtures = [BASIC_FIXTURE]

    def setUp(self):
        build_provider_and_log_in(self.client)

        self.valid_pt_dict = {
            'first_name': "Juggie",
            'last_name': "Brodeltein",
            'middle_name': "Bayer",
            'phone': '+49 178 236 5288',
            'languages': [models.Language.objects.all()[0]],
            'gender': models.Gender.objects.all()[0].pk,
            'address': 'Schulstrasse 9',
            'city': 'Munich',
            'state': 'BA',
            'country': 'Germany',
            'zip_code': '63108',
            'pcp_preferred_zip': '63018',
            'date_of_birth': datetime.date(1990, 01, 01),
            'patient_comfortable_with_english': False,
            'ethnicities': [models.Ethnicity.objects.all()[0]],
            'preferred_contact_method':
                models.ContactMethod.objects.all()[0].pk,
        }

    def test_ssn_rewrite(self):
        '''SSNs given without hypens should be automatically hypenated.'''

        submitted_pt = self.valid_pt_dict
        submitted_pt['ssn'] = "123456789"

        response = self.client.post(reverse('intake'), submitted_pt)

        new_pt = list(models.Patient.objects.all())[-1]
        self.assertEquals(new_pt.ssn, "123-45-6789")

    def test_can_intake_pt(self):

        n_pt = len(models.Patient.objects.all())

        submitted_pt = self.valid_pt_dict

        url = reverse('intake')

        response = self.client.post(url, submitted_pt)

        self.assertEqual(response.status_code, 302)
        self.assertEquals(len(models.Patient.objects.all()), n_pt + 1)

        new_pt = models.Patient.objects.all()[n_pt]
        
        for param in submitted_pt:
            try:
                self.assertEquals(str(submitted_pt[param]),
                                  str(getattr(new_pt, param)))
            except AssertionError:
                self.assertEquals(str(submitted_pt[param]),
                                  str(getattr(new_pt, param).all()))

        # new patients should be marked as active by default
        self.assertTrue(new_pt.needs_workup)

    def test_missing_alt_phone(self):
        '''Missing the alternative phone w/o alt phone owner should fail.'''
        form_data = self.valid_pt_dict
        form_data['alternate_phone_1_owner'] = "Jamal"
        # omit 'alternate_phone', should get an error

        form = forms.PatientForm(data=form_data)
        self.assertEqual(form['first_name'].errors, [])
        self.assertNotEqual(form['alternate_phone_1_owner'].errors, [])

    def test_missing_alt_phone_owner(self):
        '''Missing the alt phone owner w/o alt phone should fail.'''
        form_data = self.valid_pt_dict
        # form_data['alternate_phone_1_owner'] = "Jamal"
        form_data['alternate_phone_1'] = "4258612322"
        # omit 'alternate_phone', should get an error

        form = forms.PatientForm(data=form_data)
        self.assertEqual(form['first_name'].errors, [])
        self.assertNotEqual(form['alternate_phone_1'].errors, [])


class ActionItemTest(TestCase):
    fixtures = [BASIC_FIXTURE]

    def setUp(self):
        build_provider_and_log_in(self.client, ["Coordinator"])


    def test_home_has_correct_patients(self):
        pt1 = models.Patient.objects.get(pk=1)

        # we need > 1 pt, because one will have an active AI and one won't
        pt2 = models.Patient.objects.create(
            first_name="Juggie",
            last_name="Brodeltein",
            middle_name="Bayer",
            phone='+49 178 236 5288',
            gender=models.Gender.objects.all()[1],
            address='Schulstrasse 9',
            city='Munich',
            state='BA',
            zip_code='63108',
            pcp_preferred_zip='63018',
            date_of_birth=datetime.date(1990, 01, 01),
            patient_comfortable_with_english=False,
            preferred_contact_method=models.ContactMethod.objects.all()[0],
        )

        pt3 = models.Patient.objects.create(
            first_name="asdf",
            last_name="lkjh",
            middle_name="Bayer",
            phone='+49 178 236 5288',
            gender=models.Gender.objects.all()[0],
            address='Schulstrasse 9',
            city='Munich',
            state='BA',
            zip_code='63108',
            pcp_preferred_zip='63018',
            date_of_birth=datetime.date(1990, 01, 01),
            patient_comfortable_with_english=False,
            preferred_contact_method=models.ContactMethod.objects.all()[0],
        )

        # make pt1 have and AI due tomorrow
        pt1_ai = models.ActionItem.objects.create(
            author=models.Provider.objects.all()[0],
            author_type=models.ProviderType.objects.all()[0],
            instruction=models.ActionInstruction.objects.all()[0],
            due_date=datetime.datetime.today()+datetime.timedelta(days=1),
            comments="",
            patient=pt1)

        # make pt2 have an AI due yesterday
        pt2_ai = models.ActionItem.objects.create(
            author=models.Provider.objects.all()[0],
            author_type=models.ProviderType.objects.all()[0],
            instruction=models.ActionInstruction.objects.all()[0],
            due_date=datetime.datetime.today()-datetime.timedelta(days=1),
            comments="",
            patient=pt2)

        # make pt3 have an AI that's done
        pt3_ai = models.ActionItem.objects.create(
            author=models.Provider.objects.all()[0],
            author_type=models.ProviderType.objects.all()[0],
            instruction=models.ActionInstruction.objects.all()[0],
            due_date=datetime.datetime.today()-datetime.timedelta(days=15),
            comments="",
            patient=pt3)

        url = reverse("home")

        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

        #pt2, pt3 should be present since pt 1 is not past due
        self.assertEqual(len(response.context['zipped_list'][1][1]), 2)
        self.assertIn(pt2, response.context['zipped_list'][1][1])
        self.assertIn(pt3, response.context['zipped_list'][1][1])

        pt3_ai.mark_done(models.Provider.objects.all()[0])
        pt3_ai.save()

        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

        # now only pt2 should be present, since only pt3's AI is now done
        self.assertEqual(len(response.context['zipped_list'][1][1]), 1)
        self.assertIn(pt2, response.context['zipped_list'][1][1])


    def test_action_item_urls(self):
        pt = models.Patient.objects.all()[0]

        ai_inst = models.ActionInstruction.objects.create(
            instruction="Follow up on labs")
        ai = models.ActionItem.objects.create(
            instruction=ai_inst,
            due_date=datetime.datetime.today(),
            comments="",
            author=models.Provider.objects.all()[0],
            author_type=models.ProviderType.objects.all()[0],
            patient=pt)

        # new action items should not be done
        self.assertFalse(ai.done())

        # submit a request to mark the new ai as done. should redirect to pt
        ai_url = 'done-action-item'
        response = self.client.get(reverse(ai_url, args=(ai.id,)))
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse('patient-detail', args=(pt.id,)),
                      response.url)
        self.assertTrue(models.ActionItem.objects.all()[0].done())
        self.assertEquals(models.ActionItem.objects.all()[0].author.pk,
                          int(self.client.session['_auth_user_id']))
        self.assertNotEqual(
            models.ActionItem.objects.all()[0].written_datetime,
            models.ActionItem.objects.all()[0].last_modified)

        # submit a request to reset the ai. should redirect to pt
        ai_url = 'reset-action-item'
        prev_mod_datetime = models.ActionItem.objects.all()[0].last_modified
        response = self.client.get(reverse(ai_url, args=(ai.id,)))
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse('patient-detail', args=(pt.id,)),
                      response.url)
        self.assertFalse(models.ActionItem.objects.all()[0].done())

        self.assertNotEqual(
            models.ActionItem.objects.all()[0].written_datetime,
            models.ActionItem.objects.all()[0].last_modified)
        self.assertNotEqual(prev_mod_datetime,
                            models.ActionItem.objects.all()[0].last_modified)

    def test_create_action_item(self):

        self.assertEquals(len(models.ActionItem.objects.all()), 0)

        submitted_ai = {
            "instruction": models.ActionInstruction.objects.all()[0].pk,
            "due_date": str(datetime.date.today() + datetime.timedelta(10)),
            "comments": "models.CharField(max_length=300)" # arbitrary string
            }

        url = reverse('new-action-item', kwargs={'pt_id': 1})
        response = self.client.post(url, submitted_ai)

        self.assertEquals(response.status_code, 302)
        self.assertIn(reverse('patient-detail', args=(1,)), response.url)

        self.assertEquals(len(models.ActionItem.objects.all()), 1)
        new_ai = models.ActionItem.objects.all()[0]

        submitted_ai['due_date'] = datetime.date(
            *([int(i) for i in submitted_ai['due_date'].split('-')]))

        for param in submitted_ai:
            self.assertEquals(str(submitted_ai[param]),
                              str(getattr(new_ai, param)))

        note_check(self, new_ai, self.client, 1)


class AttendingTests(TestCase):
    fixtures = [BASIC_FIXTURE]

    def setUp(self):
        build_provider_and_log_in(self.client, ["Attending"])

    def test_home_has_correct_patients_attending(self):

        models.ClinicDate.objects.create(clinic_type=models.ClinicType.objects.all()[0],
                                         clinic_date=datetime.datetime.now(),
                                         gcal_id="435345")
        # we need > 1 pt, because one will have an active AI and one won't
        pt1 = models.Patient.objects.create(
            first_name="Juggie",
            last_name="Brodeltein",
            middle_name="Bayer",
            phone='+49 178 236 5288',
            gender=models.Gender.objects.all()[1],
            address='Schulstrasse 9',
            city='Munich',
            state='BA',
            zip_code='63108',
            pcp_preferred_zip='63018',
            date_of_birth=datetime.date(1990, 01, 01),
            patient_comfortable_with_english=False,
            needs_workup=True,
            preferred_contact_method=models.ContactMethod.objects.all()[0],
        )

        pt2 = models.Patient.objects.create(
            first_name="Juggie",
            last_name="Brodeltein",
            middle_name="Bayer",
            phone='+49 178 236 5288',
            gender=models.Gender.objects.all()[1],
            address='Schulstrasse 9',
            city='Munich',
            state='BA',
            zip_code='63108',
            pcp_preferred_zip='63018',
            date_of_birth=datetime.date(1990, 01, 01),
            patient_comfortable_with_english=True,
            needs_workup=True,
            preferred_contact_method=models.ContactMethod.objects.all()[0],
        )

        pt3 = models.Patient.objects.create(
            first_name="asdf",
            last_name="lkjh",
            middle_name="Bayer",
            phone='+49 178 236 5288',
            gender=models.Gender.objects.all()[0],
            address='Schulstrasse 9',
            city='Munich',
            state='BA',
            zip_code='63108',
            pcp_preferred_zip='63018',
            date_of_birth=datetime.date(1990, 01, 01),
            patient_comfortable_with_english=False,
            needs_workup=True,
            preferred_contact_method=models.ContactMethod.objects.all()[0],
        )

        wu1 = models.Workup.objects.create(
            clinic_day=models.ClinicDate.objects.all()[0],
            chief_complaint="SOB",
            diagnosis="MI",
            HPI="", PMH_PSH="", meds="", allergies="", fam_hx="", soc_hx="",
            ros="", pe="", A_and_P="",
            author=models.Provider.objects.all()[0],
            author_type=models.ProviderType.objects.all()[0],
            patient=pt1)

        wu2 = models.Workup.objects.create(
            clinic_day=models.ClinicDate.objects.all()[0],
            chief_complaint="SOB",
            diagnosis="MI",
            HPI="", PMH_PSH="", meds="", allergies="", fam_hx="", soc_hx="",
            ros="", pe="", A_and_P="",
            author=models.Provider.objects.all()[0],
            author_type=models.ProviderType.objects.all()[0],
            patient=pt2,
            signer=models.Provider.objects.all().filter(
                clinical_roles=models.ProviderType.objects.all().filter(short_name="Attending")[0])[0])


        wu3 = models.Workup.objects.create(
            clinic_day=models.ClinicDate.objects.all()[0],
            chief_complaint="SOB",
            diagnosis="MI",
            HPI="", PMH_PSH="", meds="", allergies="", fam_hx="", soc_hx="",
            ros="", pe="", A_and_P="",
            author=models.Provider.objects.all()[0],
            author_type=models.ProviderType.objects.all()[0],
            patient=pt3)

        url = reverse("home")

        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

        # pt1, pt3 should be present since they are not signed
        self.assertEqual(len(response.context['zipped_list'][0][1]), 2)
        self.assertIn(pt1, response.context['zipped_list'][0][1])
        self.assertIn(pt3, response.context['zipped_list'][0][1])
