from django.test import TestCase
from django.utils.timezone import now

from pttrack.models import Provider, ProviderType, Patient, Gender
from pttrack.test_views import log_in_provider, build_provider

from . import models


class TestAttestations(TestCase):

    fixtures = ['workup', 'pttrack']

    def setUp(self):

        models.ClinicDate.objects.create(
            clinic_type=models.ClinicType.objects.first(),
            clinic_date=now().date())

        # roles=["AP", "C", "PV", "CV"])
        self.all_roles_provider = build_provider()

        self.wu = models.Workup.objects.create(
            clinic_day=models.ClinicDate.objects.first(),
            chief_complaint="SOB",
            diagnosis="MI",
            HPI="A", PMH_PSH="B", meds="C", allergies="D",
            fam_hx="E",
            author=Provider.objects.first(),
            soc_hx="F", ros="", pe="", A_and_P="",
            author_type=ProviderType.objects.filter(
                signs_charts=False).first(),
            patient=Patient.objects.first())

        self.pn = models.ProgressNote.objects.create(
            title='Good',
            text='very good',
            author=Provider.objects.first(),
            author_type=ProviderType.objects.filter(
                signs_charts=False).first(),
            patient=Patient.objects.first())

    # Workup Attestation Testing
    def test_all_roles_provider_wu_signing(self):
        # roles=["AP", "C", "PV", "CV"], username=None,
        # password='password', email=None)
        all_roles_provider = build_provider()

        # test that if a provider tries to sign a chart with a provider
        # type they do not have, an error is thrown
        with self.assertRaises(ValueError):
            self.wu.sign(
                all_roles_provider.associated_user,
                active_role=ProviderType(
                    long_name="Test Provider", short_name="TP",
                    signs_charts=False, staff_view=False))

        self.assertFalse(self.wu.signed())

        with self.assertRaises(ValueError):  # test that with active_role=None, an error is thrown
            self.wu.sign(
                all_roles_provider.associated_user)

        self.assertFalse(self.wu.signed())

        # test that provider given all roles can sign a chart if their active role allows for it
        self.wu.sign(
            all_roles_provider.associated_user,
            active_role=ProviderType.objects.filter(signs_charts=True).first())

        self.assertTrue(self.wu.signed())

    def test_non_signing_provider_wu_signing(self):  # test that provider with no roles that allow for signing the chart cannot sign chart

        all_roles_provider = build_provider()

        # self.assertEqual(len(ProviderType.objects.filter(signs_charts=False)), 3)

        with self.assertRaises(ValueError):
            self.wu.sign(
                all_roles_provider.associated_user,
                active_role=ProviderType.objects.filter(signs_charts=False).first())

        self.assertFalse(self.wu.signed())

    def test_one_role_provider_wu_signing(self):  # test that provider given one role will use that roll, and can only sign chart if ProviderType allows for it

        for role in ["Preclinical", "Clinical", "Coordinator", "Attending"]:  # ProviderType is not Iterable, even though the QuerySet should be iterable?
            one_role_provider = build_provider(roles=[role])
            if one_role_provider.clinical_roles.first().signs_charts:
                self.wu.sign(
                    one_role_provider.associated_user)

                self.assertTrue(self.wu.signed())

            else:  # one_role_provider.signs_charts = False
                with self.assertRaises(ValueError):
                    self.wu.sign(
                        one_role_provider.associated_user)

                self.assertFalse(self.wu.signed())

                with self.assertRaises(ValueError):  # test that a non-Attending provider cannot use the Attending role to sign a chart
                    self.wu.sign(
                        one_role_provider.associated_user,
                        active_role=ProviderType.objects.filter(signs_charts=True).first())

                self.assertFalse(self.wu.signed())

            self.wu.signer = None  # reset chart's signed status
