from django.test import TestCase
from django.urls import reverse, resolve
from osler.inventory.models import DrugCategory, MeasuringUnit, Manufacturer, Drug, DispenseHistory
from osler.inventory import views, forms
from osler.inventory.tests import factories
from osler.core.tests.test_views import build_user
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

    return {
        'name': 'Somedrug',
        'unit': MeasuringUnit.objects.create(name='someunit'),
        'dose': 1000.0,
        'stock': 10,
        'expiration_date': '2040-01-01',
        'lot_number': 'ABCDEFGH',
        'category': DrugCategory.objects.create(name='somecategory'),
        'manufacturer': Manufacturer.objects.create(name='somemanufacturer')
    }

class TestModels(TestCase):

    def test_drugcategory_creation(self):
        assert DrugCategory.objects.count() == 0
        category = factories.DrugCategoryFactory()
        assert isinstance(category, DrugCategory)
        assert DrugCategory.objects.count() == 1

    def test_measuringunit_creation(self):
        assert MeasuringUnit.objects.count() == 0
        measuringunit = factories.MeasuringUnitFactory()
        assert isinstance(measuringunit, MeasuringUnit)
        assert MeasuringUnit.objects.count() == 1

    def test_manufacturer_creation(self):
        assert Manufacturer.objects.count() == 0
        manufacturer = factories.ManufacturerFactory()
        assert isinstance(manufacturer, Manufacturer)
        assert Manufacturer.objects.count() == 1

    def test_drug_creation(self):
        assert Drug.objects.count() == 0
        drug = factories.DrugFactory()
        assert isinstance(drug, Drug)
        assert Drug.objects.count() == 1

    def test_dispense_history_creation(self):
        assert DispenseHistory.objects.count() == 0
        user = build_user()
        dispense_history = factories.DispenseHistoryFactory(author=user, author_type=user.groups.first())
        assert isinstance(dispense_history, DispenseHistory)
        assert DispenseHistory.objects.count() == 1

    def test_can_dispense(self):
        drug = factories.DrugFactory()
        num = drug.stock
        self.assertEqual(drug.can_dispense(num), True)

    def test_cannot_dispense(self):
        drug = factories.DrugFactory()
        num = drug.stock + 1
        self.assertEqual(drug.can_dispense(num), False)

    def test_dispense(self):
        drug = factories.DrugFactory()
        num = drug.stock
        dispense = 5
        remain = num - dispense
        drug.dispense(dispense)
        self.assertEqual(drug.stock, remain)

class TestForms(TestCase):

    def test_drug_form_valid(self):
        drug = factories.DrugFactory()
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
        drug = factories.DrugFactory()
        data = {
                    'name': drug.name,
                    'lot_number': drug.lot_number,
                    'manufacturer': drug.manufacturer.pk
                }
        form = forms.DuplicateDrugForm(data=data)
        self.assertTrue(form.is_valid())
