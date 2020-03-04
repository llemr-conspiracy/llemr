from django.contrib import admin
from django.core.urlresolvers import reverse
from simple_history.admin import SimpleHistoryAdmin
from django.db.models import Count, Min, Max
from django.db.models.functions import Trunc
from django.db.models import DateField
from collections import Counter

from pttrack.admin import NoteAdmin
from . import models
from pttrack.models import Provider


def get_next_in_date_hierarchy(request, date_hierarchy):
    if date_hierarchy + '__day' in request.GET:
        return 'day'
    if date_hierarchy + '__month' in request.GET:
        return 'day'
    if date_hierarchy + '__year' in request.GET:
        return 'month'
    return 'month'

@admin.register(models.WorkupSummary)
class WorkupSummaryAdmin(admin.ModelAdmin):
    change_list_template = 'admin/workup_summary_change_list.html'
    date_hierarchy = 'written_datetime'

    def get_drug_list(self):
        # Lower case to facilitate matching
        LIST_OF_VALID_MEDS = [
            'lisinopril',
            'atorvastatin',
            'levothyroxine',
            'metformin hydrochloride',
            'amlodipine',
            'metoprolol',
            'omeprazole',
            'simvastatin',
            'losartan potassium',
            'albuterol',
            'gabapentin',
            'hydrochlorothiazide',
            'acetaminophen',
            'hydrocodone bitartrate',
            'sertraline hydrochloride',
            'fluticasone',
            'montelukast',
            'furosemide',
            'amoxicillin',
            'pantoprazole sodium',
            'escitalopram oxalate',
            'alprazolam',
            'prednisone',
            'bupropion',
            'pravastatin sodium',
            'acetaminophen',
            'citalopram',
            'dextroamphetamine',
            'dextroamphetamine saccharate',
            'amphetamine',
            'amphetamine aspartate',
            'ibuprofen',
            'carvedilol',
            'trazodone hydrochloride',
            'fluoxetine hydrochloride',
            'tramadol hydrochloride',
            'insulin glargine',
            'glargine',
            'clonazepam',
            'tamsulosin hydrochloride',
            'atenolol',
            'potassium',
            'meloxicam',
            'rosuvastatin',
            'clopidogrel bisulfate',
            'propranolol hydrochloride',
            'aspirin',
            'cyclobenzaprine',
            'hydrochlorothiazide',
            'lisinopril',
            'glipizide',
            'duloxetine',
            'methylphenidate',
            'ranitidine',
            'venlafaxine',
            'zolpidem tartrate',
            'warfarin',
            'oxycodone',
            'norethindrone',
            'allopurinol',
            'ergocalciferol',
            'insulin aspart',
            'aspart',
            'azithromycin',
            'metronidazole',
            'loratadine',
            'lorazepam',
            'estradiol',
            'ethinyl estradiol',
            'norgestimate',
            'lamotrigine',
            'glimepiride',
            'fluticasone propionate',
            'salmeterol xinafoate',
            'cetirizine',
            'hydrochlorothiazide',
            'losartan potassium',
            'paroxetine',
            'spironolactone',
            'fenofibrate',
            'naproxen',
            'pregabalin',
            'insulin human',
            'budesonide',
            'formoterol',
            'diltiazem hydrochloride',
            'quetiapine fumarate',
            'topiramate',
            'bacitracin',
            'neomycin',
            'polymyxin b',
            'clonidine',
            'buspirone hydrochloride',
            'latanoprost',
            'tiotropium',
            'ondansetron',
            'lovastatin',
            'valsartan',
            'finasteride',
            'amitriptyline',
            'esomeprazole',
            'tizanidine',
            'alendronate sodium',
            'lisdexamfetamine dimesylate',
            'ferrous sulfate',
            'apixaban',
            'diclofenac',
            'sitagliptin phosphate',
            'folic acid',
            'sumatriptan',
            'drospirenone',
            'ethinyl estradiol',
            'hydroxyzine',
            'oxybutynin',
            'hydrochlorothiazide',
            'triamterene',
            'cephalexin',
            'triamcinolone',
            'benazepril hydrochloride',
            'hydralazine hydrochloride',
            'celecoxib',
            'ciprofloxacin',
            'ropinirole hydrochloride',
            'rivaroxaban',
            'levetiracetam',
            'isosorbide mononitrate',
            'aripiprazole',
            'doxycycline',
            'insulin detemir',
            'detemir',
            'famotidine',
            'amoxicillin',
            'clavulanate potassium',
            'methotrexate',
            'hydrocodone bitartrate',
            'mirtazapine',
            'nifedipine',
            'sulfamethoxazole',
            'trimethoprim',
            'enalapril maleate',
            'docusate',
            'insulin lispro',
            'lispro',
            'pioglitazone',
            'divalproex sodium',
            'donepezil hydrochloride',
            'hydroxychloroquine sulfate',
            'prednisolone',
            'thyroid',
            'guanfacine',
            'testosterone',
            'hydrochlorothiazide',
            'valsartan',
            'ramipril',
            'diazepam',
            'ethinyl estradiol',
            'levonorgestrel',
            'clindamycin',
            'gemfibrozil',
            'metformin hydrochloride',
            'sitagliptin phosphate',
            'baclofen',
            'norethindrone',
            'temazepam',
            'nitroglycerin',
            'nebivolol hydrochloride',
            'verapamil hydrochloride',
            'timolol',
            'promethazine hydrochloride',
            'benzonatate',
            'memantine hydrochloride',
            'doxazosin mesylate',
            'ezetimibe',
            'valacyclovir',
            'beclomethasone',
            'hydrocortisone',
            'morphine',
            'risperidone',
            'methylprednisolone',
            'oseltamivir phosphate',
            'amlodipine besylate',
            'benazepril hydrochloride',
            'meclizine hydrochloride',
            'polyethylene glycol 3350',
            'liraglutide',
            'desogestrel',
            'ethinyl estradiol',
            'levofloxacin',
            'acyclovir',
            'brimonidine tartrate',
            'digoxin',
            'adalimumab',
            'cyanocobalamin',
            'magnesium',
            'albuterol sulfate',
            'ipratropium bromide',
            'chlorthalidone',
            'glyburide',
            'levocetirizine dihydrochloride',
            'carbamazepine',
            'ethinyl estradiol',
            'etonogestrel',
            'methocarbamol',
            'pramipexole dihydrochloride',
            'lithium',
            'dicyclomine hydrochloride',
            'fluconazole',
            'nortriptyline hydrochloride',
            'carbidopa',
            'levodopa',
            'nitrofurantoin',
            'mupirocin',
            'acetaminophen',
            'butalbital',
            'lansoprazole',
            'dexmethylphenidate hydrochloride',
            'budesonide',
            'mirabegron',
            'canagliflozin',
            'menthol',
            'terazosin',
            'progesterone',
            'amiodarone hydrochloride',
            'mometasone',
            'cefdinir',
            'atomoxetine hydrochloride',
            'linagliptin',
            'colchicine',
            'dexlansoprazole',
            'naphazoline hydrochloride',
            'pheniramine maleate',
            'rizatriptan benzoate',
            'hydromorphone hydrochloride',
            'oxcarbazepine',
            'lidocaine',
            'clobetasol propionate',
            'phentermine',
            'labetalol',
            'travoprost',
            'guaifenesin',
            'codeine phosphate',
            'pseudoephedrine hydrochloride',
            'eszopiclone',
            'erythromycin',
            'ipratropium',
            'sildenafil',
            'sucralfate',
            'ketoconazole',
            'irbesartan',
            'phenytoin',
            'medroxyprogesterone acetate',
            'olmesartan medoxomil',
            'emtricitabine',
            'sodium',
            'benztropine mesylate',
            'prazosin hydrochloride',
            'empagliflozin',
            'tolterodine tartrate',
            'nystatin',
            'bimatoprost',
            'dulaglutide',
            'dorzolamide hydrochloride',
            'timolol maleate',
            'guaifenesin',
            'desvenlafaxine',
            'calcium',
            'cholecalciferol',
            'minocycline hydrochloride',
            'primidone',
            'olanzapine',
            'doxepin hydrochloride',
            'diphenhydramine hydrochloride',
            'penicillin v',
            'formoterol fumarate',
            'mometasone furoate',
            'methimazole',
            'fexofenadine hydrochloride',
            'mesalamine',
            'sodium fluoride',
            'cyclosporine',
            'telmisartan',
            'fentanyl',
            'tamoxifen citrate',
            'liothyronine sodium',
            'metoclopramide hydrochloride',
            'mycophenolate mofetil',
            'carisoprodol',
            'calcitriol',
            'linaclotide',
            'anastrozole',
            'dapagliflozin',
            'exenatide',
            'ziprasidone',
            'calcium',
            'epinephrine',
            'torsemide',
            'insulin degludec',
            'degludec',
            'alfuzosin hydrochloride',
            'sotalol hydrochloride',
            'bisoprolol fumarate',
            'quinapril',
            'olopatadine',
            'ketorolac tromethamine',
            'ranolazine',
            'lurasidone hydrochloride',
            'pancrelipase lipase',
            'pancrelipase protease',
            'pancrelipase amylase',
            'dutasteride',
            'bumetanide',
            'ofloxacin',
            'rabeprazole sodium',
            'triazolam',
            'dorzolamide hydrochloride',
            'tadalafil',
            'solifenacin succinate',
            'ethinyl estradiol',
            'norgestrel',
            'vilazodone hydrochloride',
            'chlorhexidine',
            'sennosides',
            'buprenorphine',
            'naloxone',
            'flecainide acetate',
            'niacin',
            'indomethacin',
            'hydrochlorothiazide',
            'olmesartan medoxomil',
            'tretinoin',
            'conjugated estrogens',
            'medroxyprogesterone',
            'atenolol',
            'chlorthalidone',
            'haloperidol',
            'azelastine hydrochloride',
            'ezetimibe',
            'simvastatin',
            'enoxaparin sodium',
            'betamethasone dipropionate',
            'clotrimazole'
        ]

        output_list = []
        for med in LIST_OF_VALID_MEDS:
            # if med has two words, second is almost always chemical name
            # add shortened name to list of meds as well
            if len(med.split()) > 1:
                output_list.append(med)
                output_list.append(med.split()[0])
            else:
                output_list.append(med)
        return output_list

    def changelist_view(self, request, extra_context=None):
        response = super(WorkupSummaryAdmin, self).changelist_view(
            request, extra_context)

        try:
            qs = response.context_data['cl'].queryset
        except (AttributeError, KeyError):
            return response

        # Add table for number of total workups per year
        all_dates = [q['clinic_day__clinic_date'].year
                     for q in models.Workup.objects.values('clinic_day__clinic_date')]
        year2count = Counter(all_dates)

        year2clinic_date_count = Counter(
            [q['clinic_date'].year
             for q in models.ClinicDate.objects.filter(workup__isnull=False).distinct().values('clinic_date')]
        )

        # year2count = {}
        # for date in all_dates:
        #     if date.year in year2count.keys():
        #         year2count[date.year] += 1
        #     else:
        #         year2count[date.year] = 1

        response.context_data['workups_by_year'] = [
            {'year': year,
             'count': year2count[year],
             'workups_per_clinic_day': (float(year2count[year]) /
                                        float(year2clinic_date_count[year]))}
            for year in year2count.keys()
        ]

        response.context_data['diagnosis_categories'] = list(
            models.DiagnosisType.objects
            .annotate(count=Count('workup'))
            .order_by('-count')
        )


        rx_split = [q['rx'].lower().replace('-', ' ').split()
                    for q in qs.values('rx')]

        med_count = {}

        med_list = self.get_drug_list()
        for rx in rx_split:
            for keyword in rx:
                if keyword in med_list:
                    if keyword in med_count.keys():
                        med_count[keyword] += 1
                    else:
                        med_count[keyword] = 1

        from heapq import nlargest
        number_of_meds_to_show = 10
        response.context_data['med_list'] = [{
            'name': key.capitalize(),
            'count': v}
            for (key, v) in nlargest(number_of_meds_to_show, med_count.items(), key=lambda i: i[1])]


        # Select time period for display
        period = get_next_in_date_hierarchy(
            request,
            self.date_hierarchy,
        )

        # Note that week does not currently work
        workups_over_time = (qs.annotate(
            period=Trunc('clinic_day__clinic_date',
                         period, output_field=DateField()))
            .values('period')
            .annotate(total=Count('id'))
            .order_by('period'))

        workups_range = workups_over_time.aggregate(
            low=Min('total'),
            high=Max('total')
        )
        high = workups_range.get('high', 0)
        low = workups_range.get('low', 0)

        response.context_data['workups_over_time'] = [
            {'period': x['period'],
             'total': x['total'],
             'pct': (float(x['total']) / float(high) * 100
                     if high > low else 0)
             }
            for x in workups_over_time
        ]

        # Add attendings sorted by number of workups

        # Note - annotation does not seem to work because of
        # multiple ForeignKey relationships between Workup
        # and Provider

        # attendings = (
        #     Provider.objects.all()
        #     .filter(clinical_roles__signs_charts=True)
        #     .annotate(attending_count=Count('workup__attending'))
        #     .order_by('-attending_count')
        # )

        attendings = Counter([q['signer'] for q in qs.filter(signer__isnull=False).values('signer')])
        number_attendings_to_show = 20
        response.context_data['attendings'] = [
            {'name': Provider.objects.get(pk=k).name(),
             'count': v}
            for (k, v) in nlargest(number_attendings_to_show,
                                   attendings.items(),
                                   key=lambda i: i[1])
        ]

        authors = Counter([q['author'] for q in qs.values('author')])
        number_authors_to_show = 20
        response.context_data['authors'] = [
            {'name': Provider.objects.get(pk=k).name(),
             'count': v}
            for (k, v) in nlargest(number_authors_to_show,
                                   authors.items(),
                                   key=lambda i: i[1])
        ]

        # Count the number of workups per patient
        pt_id2workup_count = Counter([q['patient'] for q in qs.values('patient')])
        workups_per_patient = Counter([i for i in pt_id2workup_count.values()])
        response.context_data['workups_per_patient'] = [
            {'workups_per_pt': k,
             'count': v,
             'pct': (float(v) / float(max(workups_per_patient.values()))
                     * 100)}
            for (k, v) in workups_per_patient.items()
        ]

        return response

@admin.register(models.ClinicDate)
class ClinicDateAdmin(admin.ModelAdmin):
    date_hierarchy = 'clinic_date'
    list_display = ('__str__', 'clinic_date', 'clinic_type', 'number_of_notes')


@admin.register(models.Workup)
class WorkupAdmin(NoteAdmin):
    date_hierarchy = 'written_datetime'

    list_display = ('chief_complaint', 'written_datetime', 'patient',
                    'author', 'clinic_day', 'attending', 'signed')

    readonly_fields = NoteAdmin.readonly_fields + ('author', 'signed_date',
                                                   'signer')
    list_filter = ('clinic_day', 'diagnosis_categories')
    search_fields = ('patient__first_name', 'patient__last_name',
                     'attending__first_name', 'attending__last_name',
                     'author__first_name', 'author__last_name',
                     'clinic_day__clinic_type__name',
                     'chief_complaint')

    def view_on_site(self, obj):
        url = reverse('workup', kwargs={'pk': obj.pk})
        return url


@admin.register(models.ProgressNote)
class ProgressNoteAdmin(NoteAdmin):

    def view_on_site(self, obj):
        url = reverse('progress-note-detail', kwargs={'pk': obj.pk})
        return url


for model in [models.ClinicType, models.DiagnosisType]:
    if hasattr(model, "history"):
        admin.site.register(model, SimpleHistoryAdmin)
    else:
        admin.site.register(model)
