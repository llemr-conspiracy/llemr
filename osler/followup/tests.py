'''Module for testing the followups Osler module.'''
from __future__ import unicode_literals
import datetime

from django.test import TestCase
from django.urls import reverse

from osler.followup import forms, models
from osler.core.models import Gender, Patient, Provider, ActionItem, ActionInstruction

from osler.core.tests.test_views import log_in_user, build_user
from osler.users.tests import factories as user_factories

FU_TYPES = ["labs"]

     
class FollowupTest(TestCase):
    fixtures = ['followup', 'core']

    def setUp(self):
        log_in_user(self.client, build_user())

        self.user = user_factories.UserFactory()

        self.ai = ActionItem.objects.create(
            due_date=datetime.date(2020, 1, 1),
            author=self.user,
            instruction=ActionInstruction.objects.create(
                instruction="Follow up on labs"),
            comments="I hate tests",
            author_type=self.user.groups.first(),
            patient=Patient.objects.all()[0])

    def tearDown(self):
        models.LabFollowup.objects.all().delete()
        models.ActionItemFollowup.objects.all().delete()

    def test_followup_view_urls(self):

        pt = Patient.objects.all()[0]
        ai = ActionItem.objects.all()[0]
        method = models.ContactMethod.objects.create(name="Carrier Pidgeon")
        res = models.ContactResult(name="Fisticuffs")
        reftype = models.ReferralType.objects.create(name="Chiropracter")
        aptloc = models.ReferralLocation.objects.create(
            name="Franklin's Back Adjustment",
            address="1435 Sillypants Drive")
        reason = models.NoAptReason.objects.create(
            name="better things to do")

        for i in range(101):
            # Lab Followup
            lf = models.LabFollowup.objects.create(
                contact_method=method,
                contact_resolution=res,
                author=self.user,
                author_type=self.user.groups.first(),
                patient=pt,
                communication_success=True)

            url = reverse('followup', kwargs={"pk": lf.id, "model": 'Lab'})
            response = self.client.get(url)
            self.assertEqual(response.status_code, 200)

            aif = models.ActionItemFollowup.objects.create(
                contact_method=method,
                contact_resolution=res,
                author=self.user,
                author_type=self.user.groups.first(),
                patient=pt,
                action_item=ai)

            url = reverse('followup',kwargs={"pk": aif.id, "model": 'Action Item'})
            response = self.client.get(url)
            self.assertEqual(response.status_code, 200)

    def test_followup_create_urls(self):
        '''
        Verify that all the followup creation URLs are accessible.
        '''
        pt = Patient.objects.all()[0]
        ai = ActionItem.objects.all()[0]

        for fu_type in FU_TYPES:
            url = reverse("new-followup",
                          kwargs={"pt_id": pt.id, 'ftype': fu_type.lower()})

            response = self.client.get(url)
            self.assertEqual(response.status_code, 200)

        response = self.client.get(reverse("new-actionitem-followup",
            kwargs={'pt_id': pt.id, 'ai_id': ai.id}))
        self.assertEqual(response.status_code, 200)

    def test_create_followups(self):

        contactRes = models.ContactResult.objects.create(
                    name="didn't reach the pt", attempt_again=True)

        for button_clicked in ['followup_create', 'followup_close']:
            submitted_gen_fu = {
                "contact_method":
                    models.ContactMethod.objects.all()[0].pk,
                "contact_resolution": contactRes,
                "comments": "",
                button_clicked: True
                }

            submitted_lab_fu = dict(submitted_gen_fu)
            submitted_lab_fu["communication_success"] = True

            self.verify_fu(models.LabFollowup, 'labs',
                           submitted_lab_fu)

            ai = ActionItem.objects.all()[0]
            submitted_ai_fu = dict(submitted_gen_fu)
            submitted_ai_fu.update(
                {"action_item": ActionItem.objects.all()[0].pk,})
            
            self.verify_fu(models.ActionItemFollowup,'actionitem', submitted_ai_fu)

    def verify_fu(self, fu_type, ftype, submitted_fu):

        pt = Patient.objects.all()[0]

        n_followup = len(fu_type.objects.all())

        if ftype=='actionitem':
            url = reverse('new-actionitem-followup', kwargs={"pt_id": pt.id,
                "ai_id": ActionItem.objects.all()[0].id})
        else:
            url = reverse('new-followup', kwargs={"pt_id": pt.id,
                                              "ftype": ftype})
        
        response = self.client.post(url, submitted_fu)

        self.assertEqual(response.status_code, 302)

        if 'followup_create' in submitted_fu:
            self.assertRedirects(response,
                                 reverse("core:new-action-item", args=(pt.id,)))
        elif 'followup_close' in submitted_fu:
            self.assertRedirects(response,
                                 reverse('core:patient-detail', args=(pt.id,)))


        self.assertEqual(len(fu_type.objects.all()), n_followup + 1)

        # this should get the most recently created followup, which should be
        # the one we just posted to create
        new_fu = sorted(fu_type.objects.all(), key=lambda fu: fu.written_datetime)[-1]

        # make sure that all of the parameters in the submitted fu make it
        # into the object.

        for param in submitted_fu:
            if submitted_fu[param]:
                #ignore followup_create/close because they're not attributes of
                #followup object, they're post information from the buttons
                if param=='followup_create' or param=='followup_close':
                    pass
                else:
                    try:
                        self.assertEqual(str(submitted_fu[param]),
                                          str(getattr(new_fu, param)))
                    except AssertionError:
                        self.assertEqual(submitted_fu[param],
                                          getattr(new_fu, param).pk)

