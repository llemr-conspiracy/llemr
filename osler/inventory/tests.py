from django.test import TestCase
from django.urls import reverse, resolve
from osler.inventory.models import DrugCategory, MeasuringUnit, Manufacturer, Drug
from osler.inventory import views, forms
# Create your tests here.

class TestUrls(TestCase):

    def test_drug_list_url(self):
        path = reverse('inventory:drug-list')
        self.assertEqual(resolve(path).view_name, 'inventory:drug-list')

    def test_drug_add_new_url(self):
        path = reverse('inventory:drug-add-new')
        self.assertEqual(resolve(path).view_name, 'inventory:drug-add-new')

    def test_pre_add_new_drug_url(self):
        path = reverse('inventory:pre-drug-add-new')
        self.assertEqual(resolve(path).view_name, 'inventory:pre-drug-add-new')

    def test_predrug_select_url(self):
        path = reverse('inventory:predrug-select')
        self.assertEqual(resolve(path).view_name, 'inventory:predrug-select')

    def test_drug_dispense_url(self):
        path = reverse('inventory:drug-dispense')
        self.assertEqual(resolve(path).view_name, 'inventory:drug-dispense')

    def test_drugupdate_url(self):
        path = reverse('inventory:drug-update', kwargs={'pk':1})
        self.assertEqual(resolve(path).view_name, 'inventory:drug-update')

    def test_export_csv_url(self):
        path = reverse('inventory:export-csv')
        self.assertEqual(resolve(path).view_name, 'inventory:export-csv')

def drug_dict():

    drug_dict = {
        'name': 'Somedrug',
        'unit': MeasuringUnit.objects.create(name='someunit'),
        'dose': 1000.0,
        'stock': 10,
        'expiration_date': '2040-01-01',
        'lot_number': 'ABCDEFGH',
        'category': DrugCategory.objects.create(name='somecategory'),
        'manufacturer': Manufacturer.objects.create(name='somemanufacturer')
    }

    return drug_dict

class TestModels(TestCase):

    def test_drugcategory_creation(self):
        category = DrugCategory.objects.create(name='somecategory')
        assert isinstance(category, DrugCategory)
        self.assertEqual(category.__str__(), category.name)

    def test_measuringunit_creation(self):
        measuringunit = MeasuringUnit.objects.create(name='someunit')
        assert isinstance(measuringunit, MeasuringUnit)
        self.assertEqual(measuringunit.__str__(), measuringunit.name)

    def test_manufacturer_creation(self):
        manufacturer = Manufacturer.objects.create(name='somemanufacturer')
        assert isinstance(manufacturer, Manufacturer)
        self.assertEqual(manufacturer.__str__(), manufacturer.name)

    def test_drug_creation(self):
        drug = Drug.objects.create(**drug_dict())
        assert isinstance(drug, Drug)
        self.assertEqual(drug.__str__(), '{}, {}, stock: {}'.format(drug.name, drug.lot_number, drug.stock))

    def test_can_dispense(self):
        drug = Drug.objects.create(**drug_dict())
        self.assertEqual(drug.can_dispense(9), True)

    def test_cannot_dispense(self):
        drug = Drug.objects.create(**drug_dict())
        self.assertEqual(drug.can_dispense(11), False)

    def test_dispense(self):
        drug = Drug.objects.create(**drug_dict())
        drug.dispense(5)
        self.assertEqual(Drug.objects.first().stock, 5)

class TestForms(TestCase):

    def test_drug_form_valid(self):
        drug = Drug.objects.create(**drug_dict())
        drug_get = Drug.objects.get(pk=drug.pk)
        data = {
                    'name': drug.name,
                    'unit': drug.unit.pk,
                    'dose': drug.dose,
                    'stock': drug.stock,
                    'expiration_date': drug.expiration_date,
                    'lot_number': drug.lot_number,
                    'category': drug.category.pk,
                    'manufacturer': drug.manufacturer.pk
                }
        form = forms.DrugForm(data=data)
        self.assertTrue(form.is_valid())

    def test_duplicate_drug_form_valid(self):
        drug = Drug.objects.create(**drug_dict())
        drug_get = Drug.objects.get(pk=drug.pk)
        data = {
                    'name': drug.name,
                    'lot_number': drug.lot_number,
                    'manufacturer': drug.manufacturer.pk
                }
        form = forms.DuplicateDrugForm(data=data)
        self.assertTrue(form.is_valid())
