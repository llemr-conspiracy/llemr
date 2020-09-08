from django.test import TestCase
from django.urls import reverse, resolve
from osler.inventory.models import DrugCategory, MeasuringUnit, Manufacturer, Drug, DispenseHistory
from osler.inventory import views
from osler.core.tests.test_views import log_in_user, build_user
from osler.core.tests import factories as core_factories
from osler.inventory.tests import factories

class TestDrugList(TestCase):

    fixtures = ['core']

    def setUp(self):

        self.user = build_user()

        log_in_user(self.client, self.user)

        global drug
        global unit
        global category
        global manufacturer
        global pt

        unit = factories.MeasuringUnitFactory(name='different_unit')
        category = factories.DrugCategoryFactory(name='different_category')
        manufacturer = factories.ManufacturerFactory(name='different_manufacturer')

        self.diff_drug = {
                            'name': 'Differentdrug',
                            'unit': unit.pk,
                            'dose': 500.0,
                            'stock': 5,
                            'expiration_date': '2100-01-01',
                            'lot_number': 'HGFEDCBA',
                            'category': category.pk,
                            'manufacturer': manufacturer.pk
                        }
        drug = factories.DrugFactory()

        pt = core_factories.PatientFactory()

    def test_drug_list_view(self):
        url = reverse('inventory:drug-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertIn(drug, response.context_data['object_list'])
        self.assertTemplateUsed(response, 'inventory/inventory-main.html')

    def test_drug_update(self):
        n_drugs = Drug.objects.count()
        url = reverse('inventory:drug-update', kwargs={'pk':drug.pk})
        response = self.client.post(url, self.diff_drug, follow=True)
        drug_new = Drug.objects.get(pk=drug.pk)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(n_drugs, Drug.objects.count())
        for param in self.diff_drug:
            self.assertEqual(str(self.diff_drug[param]),
                             str(getattr(drug_new, param)))

    def test_drug_dispense_can_dispense_and_dispense_history_creation(self):
        assert DispenseHistory.objects.count() == 0

        drug_initial = Drug.objects.get(pk=drug.pk)
        dispense = drug_initial.stock
        remain = drug_initial.stock - dispense
        url = reverse('inventory:drug-dispense')
        response = self.client.post(url, {'pk':drug.pk, 'num':str(dispense), 'patient_pk':pt.pk}, follow=True)
        drug_final = Drug.objects.get(pk=drug.pk)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(drug_initial.stock - dispense, drug_final.stock)

        assert DispenseHistory.objects.count() == 1
        url = reverse('core:patient-detail', args=(pt.id,))
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, drug.name)
        self.assertContains(response, drug.lot_number)
        self.assertContains(response, str(dispense))

    def test_drug_dispense_cannot_dispense(self):
        assert DispenseHistory.objects.count() == 0

        drug_initial = Drug.objects.get(pk=drug.pk)
        dispense = drug_initial.stock + 1
        url = reverse('inventory:drug-dispense')
        response = self.client.post(url, {'pk':drug.pk, 'num':str(dispense), 'patient_pk':pt.pk}, follow=True)
        drug_final = Drug.objects.get(pk=drug.pk)

        self.assertEqual(drug_initial.stock, drug_final.stock)
        self.assertEqual(response.status_code, 404)
        assert DispenseHistory.objects.count() == 0

class TestDrugAdd(TestCase):

    fixtures = ['core']

    def setUp(self):
        log_in_user(self.client, build_user())

        global drug

        drug = factories.DrugFactory()

        self.drug_field = {
                        'name': drug.name,
                        'unit': drug.unit.pk,
                        'dose': drug.dose,
                        'stock': drug.stock,
                        'expiration_date': drug.expiration_date,
                        'lot_number': drug.lot_number,
                        'category': drug.category.pk,
                        'manufacturer': drug.manufacturer.pk
        }

    def test_pre_drug_add_new_with_collision(self):
        url = reverse('inventory:pre-drug-add-new')
        response = self.client.post(url,
            {k: self.drug_field[k] for k in ['name', 'lot_number', 'manufacturer']},
            follow=True)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'inventory/predrug-select.html')
        self.assertIn(drug, response.context_data['object_list'])


    def test_pre_drug_add_new_no_collision(self):
        drug.delete()
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


