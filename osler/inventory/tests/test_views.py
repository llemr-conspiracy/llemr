from django.test import TestCase
from django.urls import reverse, resolve
from osler.inventory.models import DrugCategory, MeasuringUnit, Manufacturer, Drug, DispenseHistory
from osler.inventory import views
from osler.core.tests.test_views import log_in_user, build_user
from osler.core.tests import factories as core_factories
from osler.inventory.tests import factories
from osler.users.tests import factories as user_factories
from django.utils import timezone

class TestDrugList(TestCase):

    fixtures = ['core']

    def setUp(self):

        self.user = build_user()

        log_in_user(self.client, self.user)

        self.unit = factories.MeasuringUnitFactory(name='different_unit')
        self.category = factories.DrugCategoryFactory(name='different_category')
        self.manufacturer = factories.ManufacturerFactory(name='different_manufacturer')

        self.diff_drug = {
                            'name': 'Differentdrug',
                            'unit': self.unit.pk,
                            'dose': 500.0,
                            'stock': 5,
                            'expiration_date': '2100-01-01',
                            'lot_number': 'HGFEDCBA',
                            'category': self.category.pk,
                            'manufacturer': self.manufacturer.pk
                        }
        self.drug = factories.DrugFactory()

        self.pt = core_factories.PatientFactory()

    def test_drug_list_view(self):
        url = reverse('inventory:drug-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertIn(self.drug, response.context_data['object_list'])
        self.assertTemplateUsed(response, 'inventory/inventory-main.html')

    def test_drug_update(self):
        n_drugs = Drug.objects.count()
        url = reverse('inventory:drug-update', kwargs={'pk':self.drug.pk})
        response = self.client.post(url, self.diff_drug, follow=True)
        drug_new = Drug.objects.get(pk=self.drug.pk)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(n_drugs, Drug.objects.count())
        for param in self.diff_drug:
            self.assertEqual(str(self.diff_drug[param]),
                             str(getattr(drug_new, param)))

    def test_drug_dispense_can_dispense_and_dispense_history_creation(self):
        assert DispenseHistory.objects.count() == 0

        drug_initial = Drug.objects.get(pk=self.drug.pk)
        dispense = drug_initial.stock
        remain = drug_initial.stock - dispense
        url = reverse('inventory:drug-dispense')
        response = self.client.post(url, {'pk':self.drug.pk, 'num':str(dispense), 'patient_pk':self.pt.pk}, follow=True)
        drug_final = Drug.objects.get(pk=self.drug.pk)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(remain, drug_final.stock)

        assert DispenseHistory.objects.count() == 1
        url = reverse('core:patient-detail', args=(self.pt.id,))
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.drug.name)
        self.assertContains(response, self.drug.lot_number)
        self.assertContains(response, str(dispense))

    def test_drug_dispense_cannot_dispense(self):
        assert DispenseHistory.objects.count() == 0

        drug_initial = Drug.objects.get(pk=self.drug.pk)
        dispense = drug_initial.stock + 1
        url = reverse('inventory:drug-dispense')
        response = self.client.post(url, {'pk':self.drug.pk, 'num':str(dispense), 'patient_pk':self.pt.pk}, follow=True)
        drug_final = Drug.objects.get(pk=self.drug.pk)

        self.assertEqual(drug_initial.stock, drug_final.stock)
        self.assertEqual(response.status_code, 404)
        assert DispenseHistory.objects.count() == 0

class TestDrugAdd(TestCase):

    fixtures = ['core']

    def setUp(self):
        log_in_user(self.client, build_user())

        self.drug = factories.DrugFactory()

        self.drug_field = {
                        'name': self.drug.name,
                        'unit': self.drug.unit.pk,
                        'dose': self.drug.dose,
                        'stock': self.drug.stock,
                        'expiration_date': self.drug.expiration_date,
                        'lot_number': self.drug.lot_number,
                        'category': self.drug.category.pk,
                        'manufacturer': self.drug.manufacturer.pk
        }

    def test_pre_drug_add_new_with_collision(self):
        url = reverse('inventory:pre-drug-add-new')
        response = self.client.post(url,
            {k: self.drug_field[k] for k in ['name', 'lot_number', 'manufacturer']},
            follow=True)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'inventory/predrug-select.html')
        self.assertIn(self.drug, response.context_data['object_list'])


    def test_pre_drug_add_new_no_collision(self):
        self.drug.delete()
        url = reverse('inventory:pre-drug-add-new')
        response = self.client.post(url,
            {k: self.drug_field[k] for k in ['name', 'lot_number', 'manufacturer']},
            follow=True)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'inventory/add_new_drug.html')
        self.assertEqual(
            response.context_data['form']['name'].value(),
            self.drug_field['name'])
        self.assertEqual(
            response.context_data['form']['lot_number'].value(),
            self.drug_field['lot_number'])
        self.assertEqual(
            response.context_data['form']['manufacturer'].value(),
            self.drug_field['manufacturer'])

    def test_drug_add_new(self):
        n_drugs = Drug.objects.count()

        url = reverse('inventory:drug-add-new')

        response = self.client.post(url, self.drug_field)

        self.assertEqual(response.status_code, 302)
        self.assertEqual(Drug.objects.count(), n_drugs + 1)

        new_drug = Drug.objects.last()

        for param in self.drug_field:
            self.assertEqual(str(self.drug_field[param]),
                             str(getattr(new_drug, param)))


class TestDrugExport(TestCase):
    """
    Tests csv exports with correct name and user permissions work
    """
    def setUp(self):
        log_in_user(self.client, build_user())

    def test_export_csv(self):
        export_csv_url = reverse('inventory:export-csv')
        no_perm_group = user_factories.NoPermGroupFactory()
        csv_perm_group = user_factories.PermGroupFactory(permissions=['inventory.export_csv'])

        for group in [no_perm_group, csv_perm_group]:
            log_in_user(self.client, user_factories.UserFactory(groups=[group]))
            response = self.client.post(export_csv_url)

            if group == csv_perm_group:
                assert response.status_code == 200
                self.assertEqual(response["Content-Disposition"],
                                 f"attachment; filename=drug-inventory-{str(timezone.now().date())}.csv")
            else:
                 assert response.status_code == 403

    def test_export_dispensing_histories(self):
        export_dispensing_histories_url = reverse('inventory:export-dispensing-history')
        no_perm_group = user_factories.NoPermGroupFactory()
        csv_perm_group = user_factories.PermGroupFactory(permissions=['inventory.export_csv'])

        for group in [no_perm_group, csv_perm_group]:
            log_in_user(self.client, user_factories.UserFactory(groups=[group]))
            response = self.client.post(export_dispensing_histories_url, {'start_date': '2020-09-22','end_date': '2020-09-28'})

            if group == csv_perm_group:
                assert response.status_code == 200
                self.assertEqual(response["Content-Disposition"],
                                 f"attachment; filename=drug-dispensing-history-through-2020-09-28.csv")
            else:
                 assert response.status_code == 403
