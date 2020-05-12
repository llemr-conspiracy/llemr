from __future__ import unicode_literals
from builtins import str
from django.test import TestCase, override_settings, Client
from django.urls import reverse
from django.contrib.auth import get_user_model

from osler.core.models import ProviderType
from osler.core.tests.test_views import build_provider, log_in_provider

from .models import PageviewRecord


class TestAudit(TestCase):

    fixtures = ['core.json']

    def setUp(self):
        self.client = Client()

    def test_audit_unicode(self):
        """Check that unicode works for TestAudit
        """
        p = PageviewRecord.objects.create(
            user=get_user_model().objects.first(),
            user_ip='128.0.0.1',
            role=ProviderType.objects.first(),
            method=PageviewRecord.HTTP_METHODS[0],
            url=reverse('home'),
            referrer='',
            status_code=200,
        )

        self.assertEqual(
            str(p),
            "GET by None to %s at %s" % (reverse('home'), p.timestamp))

    def test_create_on_view(self):

        provider = log_in_provider(self.client, build_provider(["Attending"]))
        expected_user = provider.associated_user

        # format is: {X-Forwarded-For: client, proxy1, proxy2}
        USER_IP = '0.0.0.0'
        self.client.get(
            reverse('home'),
            HTTP_X_FORWARDED_FOR=USER_IP + ',,')

        n_records = PageviewRecord.objects.count()
        self.assertEqual(n_records, 1)

        record = PageviewRecord.objects.first()
        self.assertEqual(record.user, expected_user)
        self.assertEqual(record.user_ip, USER_IP)
        self.assertEqual(record.role.short_name, 'Attending')
        self.assertEqual(record.method, 'GET')

    def test_audit_admin(self):
        p = log_in_provider(self.client, build_provider(["Coordinator"]))
        p.associated_user.is_staff = True
        p.associated_user.is_superuser = True
        p.associated_user.save()

        r = self.client.get(reverse('admin:audit_pageviewrecord_changelist'))
        self.assertEqual(r.status_code, 200)

    @override_settings(OSLER_AUDIT_BLACK_LIST=['0.0.0.1'])
    def test_create_on_view_if_USER_IP_is_not_in_BLACKLIST(self):

        provider = log_in_provider(self.client, build_provider(["Attending"]))
        expected_user = provider.associated_user

        # format is: {X-Forwarded-For: client, proxy1, proxy2}
        USER_IP = '0.0.0.0'
        self.client.get(
            reverse('home'),
            HTTP_X_FORWARDED_FOR=USER_IP + ',,')

        n_records = PageviewRecord.objects.count()
        self.assertEqual(n_records, 1)

        record = PageviewRecord.objects.first()
        self.assertEqual(record.user, expected_user)
        self.assertEqual(record.user_ip, USER_IP)
        self.assertEqual(record.role.short_name, 'Attending')
        self.assertEqual(record.method, 'GET')

    @override_settings(OSLER_AUDIT_BLACK_LIST=['0.0.0.1'])
    def test_no_create_on_view_if_USER_IP_is_in_BLACKLIST(self):

        provider = log_in_provider(self.client, build_provider(["Attending"]))
        expected_user = provider.associated_user

        # format is: {X-Forwarded-For: client, proxy1, proxy2}
        USER_IP = '0.0.0.1'
        self.client.get(
            reverse('home'),
            HTTP_X_FORWARDED_FOR=USER_IP + ',,')

        n_records = PageviewRecord.objects.count()
        self.assertEqual(n_records, 0)
