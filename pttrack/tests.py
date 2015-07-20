from django.test import TestCase
from . import models
from . import forms
from django.core.exceptions import ValidationError
from django.core.urlresolvers import reverse
from django.test import Client
from django.contrib.auth.models import User
from django.utils.timezone import now
from django.core.files import File
import datetime


# pylint: disable=invalid-name
# Whatever, whatever. I name them what I want.

class CustomFuncTesting(TestCase):
    def test_validate_zip(self):
        self.assertEqual(models.validate_zip(12345), None)
        with self.assertRaises(ValidationError):
            models.validate_zip(123456)
        with self.assertRaises(ValidationError):
            models.validate_zip('ABCDE')


class ViewsExistTest(TestCase):
    def setUp(self):

        g = models.Gender.objects.create(long_name="Male", short_name="M")
        l = models.Language.objects.create(name="English")
        e = models.Ethnicity.objects.create(name="White")

        p = models.Patient.objects.create(
            first_name="Frankie", middle_name="Lane", last_name="McNath",
            address="6310 Scott Ave", city="St. Louis", state="MO",
            date_of_birth=datetime.date(year=1989, month=8, day=9),
            phone="501-233-1234",
            gender=g)

        p.languages.add(l)
        p.ethnicities.add(e)
        p.save()

        models.ClinicType.objects.create(name="Basic Care Clinic")

        models.ClinicDate.objects.create(
            clinic_type=models.ClinicType.objects.all()[0],
            clinic_date=now().date(),
            gcal_id="tmp")

        models.DiagnosisType.objects.create(name="Cardiovascular")

        for (lname, can_sign) in [("Attending Physician", True),
                                  ("Preclinical Medical Student", False),
                                  ("Clinical Medical Student", False),
                                  ("Coordinator", False)]:
            p = models.ProviderType(long_name=lname,
                                    short_name=lname.split()[0],
                                    signs_charts=can_sign)
            p.save()

        user = User.objects.create_user('tljones', 'tommyljones@gmail.com',
                                        'password')
        user.save()

        models.Provider.objects.create(
            first_name="Tommy", middle_name="Lee", last_name="Jones",
            phone="425-243-9115", gender=g, associated_user=user)

        for ptype in models.ProviderType.objects.all():
            user.provider.clinical_roles.add(ptype)

        self.client.login(username=user.username, password='password')

        session = self.client.session
        session['clintype_pk'] = user.provider.clinical_roles.all()[0].pk
        session.save()

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

        response = self.client.get(reverse('all-patients'))
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse('choose-clintype'), response.url)

        models.Provider.objects.all().delete()

        response = self.client.get(reverse('all-patients'))
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse('new-provider'), response.url)

        self.client.logout()

        response = self.client.get(reverse('all-patients'))
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse('login'), response.url)

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

        # submit a request to reset the ai. should redirect to pt
        ai_url = 'reset-action-item'
        response = self.client.get(reverse(ai_url, args=(ai.id,)))
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse('patient-detail', args=(pt.id,)),
                      response.url)
        self.assertFalse(models.ActionItem.objects.all()[0].done())

    def test_followup_create_urls(self):

        pt = models.Patient.objects.all()[0]

        for fu_type in ["labs", "referral", "general", "vaccine"]:
            url = reverse("new-followup",
                          kwargs={"pt_id": pt.id, 'ftype': fu_type.lower()})

            response = self.client.get(url)
            self.assertEquals(response.status_code, 200)

        url = reverse("followup", kwargs={"pk": pt.id, "model": "Lab"})

    def test_followup_view_urls(self):
        from . import followup_models

        pt = models.Patient.objects.all()[0]

        method = models.ContactMethod.objects.create(name="Carrier Pidgeon")
        res = followup_models.ContactResult(name="Fisticuffs")

        gf = followup_models.GeneralFollowup.objects.create(
            contact_method=method,
            contact_resolution=res,
            author=models.Provider.objects.all()[0],
            author_type=models.ProviderType.objects.all()[0],
            patient=pt)

        url = reverse('followup', kwargs={"pk": gf.id, "model": 'General'})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

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

        reftype = models.ReferralType.objects.create(name="Chiropracter")
        aptloc = models.ReferralLocation.objects.create(
            name="Franklin's Back Adjustment",
            address="1435 Sillypants Drive")
        reason = followup_models.NoAptReason.objects.create(
            name="better things to do")

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

        url = reverse('followup', kwargs={"pk": rf.id, "model": 'Vaccine'})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_document_urls(self):
        '''
        Test the views showing documents, as well as the integrity of path
        saving in document creation (probably superfluous).
        '''
        import os

        url = reverse('new-document', args=(1,))

        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

        dtype = models.DocumentType.objects.create(name="Silly Picture")
        doc = models.Document.objects.create(
            title="who done it?",
            comments="Pictured: silliness",
            document_type=dtype,
            image=File(open("media/test.jpg")),
            patient=models.Patient.objects.get(id=1),
            author=models.Provider.objects.get(id=1),
            author_type=models.ProviderType.objects.all()[0])

        p = models.Document.objects.get(id=1).image.path
        self.failUnless(open(p), 'file not found')
        self.assertEqual(doc.image.path, p)
        self.assertTrue(os.path.isfile(p))

        url = reverse('document-detail', args=(1,))
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

        url = reverse('document-detail', args=(1,))
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

        os.remove(p)
        self.assertFalse(os.path.isfile(p))


class ReferralFollowupTest(TestCase):
    fixtures = ['basic_fixture']

    def test_create_followup(self):
        #TODO tests here.
        pass
