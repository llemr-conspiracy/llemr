from django.test import TestCase
from django.urls import reverse, resolve
from osler.inventory.models import DrugCategory, MeasuringUnit, Manufacturer, Drug
from osler.inventory import views
from .tests import drug_dict
from osler.core.tests.test_views import log_in_provider, build_provider

class TestDrugList(TestCase):

    fixtures = ['core', 'workup','inventory']

    def setUp(self):
        log_in_provider(self.client, build_provider())
        self.diff_drug = {
                            'name': 'Differentdrug',
                            'unit': MeasuringUnit.objects.last().pk,
                            'dose': 500.0,
                            'stock': 5,
                            'expiration_date': '2100-01-01',
                            'lot_number': 'HGFEDCBA',
                            'category': DrugCategory.objects.last().pk,
                            'manufacturer': Manufacturer.objects.last().pk
                        }

    def test_drug_list_view(self):
        drug = Drug.objects.create(**drug_dict())
        url = reverse('inventory:drug-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertIn(drug, response.context_data['object_list'])
        self.assertTemplateUsed(response, 'inventory/inventory-main.html')

    def test_drug_update(self):
        drug = Drug.objects.create(**drug_dict())
        n_drugs = len(Drug.objects.all())
        url = reverse('inventory:drug-update', kwargs={'pk':drug.pk})
        response = self.client.post(url, self.diff_drug, follow=True)
        drug_get = Drug.objects.get(pk=drug.pk)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(n_drugs, Drug.objects.count())
        for param in self.diff_drug:
            self.assertEqual(str(self.diff_drug[param]),
                             str(getattr(drug_get, param)))

    def test_drug_dispense(self):
        drug = Drug.objects.create(**drug_dict())
        drug_initial = Drug.objects.get(pk=drug.pk)
        url = reverse('inventory:drug-dispense')
        response = self.client.post(url, {'pk':drug.pk,'num':'5'}, follow=True)
        drug_final = Drug.objects.get(pk=drug.pk)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(str(getattr(drug_initial,'stock')-5),
                         str(getattr(drug_final,'stock')))

class TestDrugAdd(TestCase):

    fixtures = ['core', 'workup', 'inventory']

    def setUp(self):
        log_in_provider(self.client, build_provider())

        self.drug_dict = {
                            'name': 'Somedrug',
                            'unit': MeasuringUnit.objects.first(),
                            'dose': 1000.0,
                            'stock': 10,
                            'expiration_date': '2040-01-01',
                            'lot_number': 'ABCDEFGH',
                            'category': DrugCategory.objects.first(),
                            'manufacturer': Manufacturer.objects.first()
                        }

    def test_pre_drug_add_new_with_collision(self):
        drug = Drug.objects.create(**self.drug_dict)
        url = reverse('inventory:pre-drug-add-new')
        self.drug_dict['manufacturer'] = Manufacturer.objects.first().pk
        response = self.client.post(url,
            {k: self.drug_dict[k] for k in ['name', 'lot_number', 'manufacturer']},
            follow=True)

        self.assertTemplateUsed(response, 'inventory/predrug-select.html')
        self.assertIn(drug, response.context_data['object_list'])


    def test_pre_drug_add_new_no_collision(self):
        url = reverse('inventory:pre-drug-add-new')
        self.drug_dict['manufacturer'] = Manufacturer.objects.first().pk
        response = self.client.post(url,
            {k: self.drug_dict[k] for k in ['name', 'lot_number', 'manufacturer']},
            follow=True)

        self.assertTemplateUsed(response, 'inventory/add_new_drug.html')
        self.assertEqual(
            response.context_data['form']['name'].value(),
            self.drug_dict['name'])
        self.assertEqual(
            response.context_data['form']['lot_number'].value(),
            self.drug_dict['lot_number'])
        self.assertEqual(
            response.context_data['form']['manufacturer'].value(),
            self.drug_dict['manufacturer'])

    def test_drug_add_new(self):
        n_drugs = len(Drug.objects.all())

        url = reverse('inventory:drug-add-new')

        response = self.client.post(url, self.drug_dict)

        self.assertEqual(response.status_code, 302)
        self.assertEqual(Drug.objects.count(), n_drugs + 1)

        new_drug = Drug.objects.last()

        for param in self.drug_dict:
            self.assertEqual(str(self.drug_dict[param]),
                             str(getattr(new_drug, param)))


