# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import pttrack.validators
import pttrack.models
import django.db.models.deletion
from django.conf import settings


class Migration(migrations.Migration):

    replaces = [('pttrack', '0001_initial'),
                ('pttrack', '0002_providertype_is_staff'),
                ('pttrack', '0003_auto_20160119_1459'),
                ('pttrack', '0004_auto_20160328_1425'),
                ('pttrack', '0005_auto_20160628_1852'),
                ('pttrack', '0006_rm_ssn'),
                ('pttrack', '0007_needs_workup_default_true'),
                ('pttrack', '0008_add_case_manager'),
                ('pttrack', '0009_auto_20170502_1103'),
                ('pttrack', '0010_auto_20170623_1300')]

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='ActionInstruction',
            fields=[
                ('instruction', models.CharField(max_length=50, serialize=False, primary_key=True)),
            ],
        ),
        migrations.CreateModel(
            name='ActionItem',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('written_datetime', models.DateTimeField(auto_now_add=True)),
                ('last_modified', models.DateTimeField(auto_now=True)),
                ('due_date', models.DateField(help_text=b'MM/DD/YYYY or YYYY-MM-DD')),
                ('comments', models.CharField(max_length=300)),
                ('completion_date', models.DateTimeField(null=True, blank=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='ContactMethod',
            fields=[
                ('name', models.CharField(max_length=50, serialize=False, primary_key=True)),
            ],
        ),
        migrations.CreateModel(
            name='Document',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('written_datetime', models.DateTimeField(auto_now_add=True)),
                ('last_modified', models.DateTimeField(auto_now=True)),
                ('title', models.CharField(max_length=200)),
                ('image', models.FileField(help_text=b'Please deidentify all file names before upload! Delete all files after upload!', upload_to=pttrack.models.make_filepath, verbose_name=b'PDF File or Image Upload')),
                ('comments', models.TextField()),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='DocumentType',
            fields=[
                ('name', models.CharField(max_length=50, serialize=False, primary_key=True)),
            ],
        ),
        migrations.CreateModel(
            name='Ethnicity',
            fields=[
                ('name', models.CharField(max_length=50, serialize=False, primary_key=True)),
            ],
        ),
        migrations.CreateModel(
            name='Gender',
            fields=[
                ('long_name', models.CharField(max_length=30, serialize=False, primary_key=True)),
                ('short_name', models.CharField(max_length=1)),
            ],
        ),
        migrations.CreateModel(
            name='HistoricalActionItem',
            fields=[
                ('id', models.IntegerField(verbose_name='ID', db_index=True, auto_created=True, blank=True)),
                ('written_datetime', models.DateTimeField(editable=False, blank=True)),
                ('last_modified', models.DateTimeField(editable=False, blank=True)),
                ('due_date', models.DateField(help_text=b'MM/DD/YYYY or YYYY-MM-DD')),
                ('comments', models.CharField(max_length=300)),
                ('completion_date', models.DateTimeField(null=True, blank=True)),
                ('history_id', models.AutoField(serialize=False, primary_key=True)),
                ('history_date', models.DateTimeField()),
                ('history_type', models.CharField(max_length=1, choices=[('+', 'Created'), ('~', 'Changed'), ('-', 'Deleted')])),
            ],
            options={
                'ordering': ('-history_date', '-history_id'),
                'get_latest_by': 'history_date',
                'verbose_name': 'historical action item',
            },
        ),
        migrations.CreateModel(
            name='HistoricalDocument',
            fields=[
                ('id', models.IntegerField(verbose_name='ID', db_index=True, auto_created=True, blank=True)),
                ('written_datetime', models.DateTimeField(editable=False, blank=True)),
                ('last_modified', models.DateTimeField(editable=False, blank=True)),
                ('title', models.CharField(max_length=200)),
                ('image', models.TextField(help_text=b'Please deidentify all file names before upload! Delete all files after upload!', max_length=100, verbose_name=b'PDF File or Image Upload')),
                ('comments', models.TextField()),
                ('history_id', models.AutoField(serialize=False, primary_key=True)),
                ('history_date', models.DateTimeField()),
                ('history_type', models.CharField(max_length=1, choices=[('+', 'Created'), ('~', 'Changed'), ('-', 'Deleted')])),
            ],
            options={
                'ordering': ('-history_date', '-history_id'),
                'get_latest_by': 'history_date',
                'verbose_name': 'historical document',
            },
        ),
        migrations.CreateModel(
            name='HistoricalPatient',
            fields=[
                ('id', models.IntegerField(verbose_name='ID', db_index=True, auto_created=True, blank=True)),
                ('first_name', models.CharField(max_length=100, validators=[pttrack.validators.validate_name])),
                ('last_name', models.CharField(max_length=100, validators=[pttrack.validators.validate_name])),
                ('middle_name', models.CharField(blank=True, max_length=100, validators=[pttrack.validators.validate_name])),
                ('phone', models.CharField(max_length=40, null=True, blank=True)),
                ('address', models.CharField(max_length=200)),
                ('city', models.CharField(default=b'St. Louis', max_length=50)),
                ('state', models.CharField(default=b'MO', max_length=2)),
                ('zip_code', models.CharField(max_length=5, validators=[pttrack.validators.validate_zip])),
                ('country', models.CharField(default=b'USA', max_length=100)),
                ('pcp_preferred_zip', models.CharField(blank=True, max_length=5, null=True, validators=[pttrack.validators.validate_zip])),
                ('date_of_birth', models.DateField(validators=[pttrack.validators.validate_birth_date])),
                ('patient_comfortable_with_english', models.BooleanField(default=True)),
                ('alternate_phone_1_owner', models.CharField(max_length=40, null=True, blank=True)),
                ('alternate_phone_1', models.CharField(max_length=40, null=True, blank=True)),
                ('alternate_phone_2_owner', models.CharField(max_length=40, null=True, blank=True)),
                ('alternate_phone_2', models.CharField(max_length=40, null=True, blank=True)),
                ('alternate_phone_3_owner', models.CharField(max_length=40, null=True, blank=True)),
                ('alternate_phone_3', models.CharField(max_length=40, null=True, blank=True)),
                ('alternate_phone_4_owner', models.CharField(max_length=40, null=True, blank=True)),
                ('alternate_phone_4', models.CharField(max_length=40, null=True, blank=True)),
                ('needs_workup', models.BooleanField(default=True)),
                ('history_id', models.AutoField(serialize=False, primary_key=True)),
                ('history_date', models.DateTimeField()),
                ('history_type', models.CharField(max_length=1, choices=[('+', 'Created'), ('~', 'Changed'), ('-', 'Deleted')])),
                ('gender', models.ForeignKey(related_name='+', on_delete=django.db.models.deletion.DO_NOTHING, db_constraint=False, blank=True, to='pttrack.Gender', null=True)),
                ('history_user', models.ForeignKey(related_name='+', on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL, null=True)),
                ('preferred_contact_method', models.ForeignKey(related_name='+', on_delete=django.db.models.deletion.DO_NOTHING, db_constraint=False, blank=True, to='pttrack.ContactMethod', null=True)),
                ('email', models.EmailField(max_length=254, null=True, blank=True)),
            ],
            options={
                'ordering': ('-history_date', '-history_id'),
                'get_latest_by': 'history_date',
                'verbose_name': 'historical patient',
            },
        ),
        migrations.CreateModel(
            name='HistoricalProvider',
            fields=[
                ('id', models.IntegerField(verbose_name='ID', db_index=True, auto_created=True, blank=True)),
                ('first_name', models.CharField(max_length=100, validators=[pttrack.validators.validate_name])),
                ('last_name', models.CharField(max_length=100, validators=[pttrack.validators.validate_name])),
                ('middle_name', models.CharField(blank=True, max_length=100, validators=[pttrack.validators.validate_name])),
                ('phone', models.CharField(max_length=40, null=True, blank=True)),
                ('history_id', models.AutoField(serialize=False, primary_key=True)),
                ('history_date', models.DateTimeField()),
                ('history_type', models.CharField(max_length=1, choices=[('+', 'Created'), ('~', 'Changed'), ('-', 'Deleted')])),
                ('associated_user', models.ForeignKey(related_name='+', on_delete=django.db.models.deletion.DO_NOTHING, db_constraint=False, blank=True, to=settings.AUTH_USER_MODEL, null=True)),
                ('gender', models.ForeignKey(related_name='+', on_delete=django.db.models.deletion.DO_NOTHING, db_constraint=False, blank=True, to='pttrack.Gender', null=True)),
                ('history_user', models.ForeignKey(related_name='+', on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL, null=True)),
                ('needs_updating', models.BooleanField(default=False)),
            ],
            options={
                'ordering': ('-history_date', '-history_id'),
                'get_latest_by': 'history_date',
                'verbose_name': 'historical provider',
            },
        ),
        migrations.CreateModel(
            name='Language',
            fields=[
                ('name', models.CharField(max_length=50, serialize=False, primary_key=True)),
            ],
        ),
        migrations.CreateModel(
            name='Patient',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('first_name', models.CharField(max_length=100, validators=[pttrack.validators.validate_name])),
                ('last_name', models.CharField(max_length=100, validators=[pttrack.validators.validate_name])),
                ('middle_name', models.CharField(blank=True, max_length=100, validators=[pttrack.validators.validate_name])),
                ('phone', models.CharField(max_length=40, null=True, blank=True)),
                ('address', models.CharField(max_length=200)),
                ('city', models.CharField(default=b'St. Louis', max_length=50)),
                ('state', models.CharField(default=b'MO', max_length=2)),
                ('zip_code', models.CharField(max_length=5, validators=[pttrack.validators.validate_zip])),
                ('country', models.CharField(default=b'USA', max_length=100)),
                ('pcp_preferred_zip', models.CharField(blank=True, max_length=5, null=True, validators=[pttrack.validators.validate_zip])),
                ('date_of_birth', models.DateField(validators=[pttrack.validators.validate_birth_date])),
                ('patient_comfortable_with_english', models.BooleanField(default=True)),
                ('alternate_phone_1_owner', models.CharField(max_length=40, null=True, blank=True)),
                ('alternate_phone_1', models.CharField(max_length=40, null=True, blank=True)),
                ('alternate_phone_2_owner', models.CharField(max_length=40, null=True, blank=True)),
                ('alternate_phone_2', models.CharField(max_length=40, null=True, blank=True)),
                ('alternate_phone_3_owner', models.CharField(max_length=40, null=True, blank=True)),
                ('alternate_phone_3', models.CharField(max_length=40, null=True, blank=True)),
                ('alternate_phone_4_owner', models.CharField(max_length=40, null=True, blank=True)),
                ('alternate_phone_4', models.CharField(max_length=40, null=True, blank=True)),
                ('needs_workup', models.BooleanField(default=True)),
                ('ethnicities', models.ManyToManyField(to='pttrack.Ethnicity')),
                ('gender', models.ForeignKey(to='pttrack.Gender')),
                ('languages', models.ManyToManyField(help_text=b'Specify here languages that are spoken at a level sufficient to be used for medical communication.', to='pttrack.Language')),
                ('preferred_contact_method', models.ForeignKey(blank=True, to='pttrack.ContactMethod', null=True)),
                ('email', models.EmailField(max_length=254, null=True, blank=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Provider',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('first_name', models.CharField(max_length=100)),
                ('last_name', models.CharField(max_length=100)),
                ('middle_name', models.CharField(max_length=100, blank=True)),
                ('phone', models.CharField(max_length=40)),
                ('associated_user', models.OneToOneField(null=True, blank=True, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='ProviderType',
            fields=[
                ('long_name', models.CharField(max_length=100)),
                ('short_name', models.CharField(max_length=30, serialize=False, primary_key=True)),
                ('signs_charts', models.BooleanField(default=False)),
                ('staff_view', models.BooleanField(default=False)),
            ],
        ),
        migrations.CreateModel(
            name='ReferralLocation',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=300)),
                ('address', models.TextField()),
            ],
        ),
        migrations.CreateModel(
            name='ReferralType',
            fields=[
                ('name', models.CharField(max_length=100, serialize=False, primary_key=True)),
            ],
        ),
        migrations.AddField(
            model_name='provider',
            name='clinical_roles',
            field=models.ManyToManyField(to='pttrack.ProviderType'),
        ),
        migrations.AddField(
            model_name='provider',
            name='gender',
            field=models.ForeignKey(to='pttrack.Gender'),
        ),
        migrations.AddField(
            model_name='provider',
            name='languages',
            field=models.ManyToManyField(help_text=b'Specify here languages that are spoken at a level sufficient to be used for medical communication.', to='pttrack.Language'),
        ),
        migrations.AddField(
            model_name='historicaldocument',
            name='author',
            field=models.ForeignKey(related_name='+', on_delete=django.db.models.deletion.DO_NOTHING, db_constraint=False, blank=True, to='pttrack.Provider', null=True),
        ),
        migrations.AddField(
            model_name='historicaldocument',
            name='author_type',
            field=models.ForeignKey(related_name='+', on_delete=django.db.models.deletion.DO_NOTHING, db_constraint=False, blank=True, to='pttrack.ProviderType', null=True),
        ),
        migrations.AddField(
            model_name='historicaldocument',
            name='document_type',
            field=models.ForeignKey(related_name='+', on_delete=django.db.models.deletion.DO_NOTHING, db_constraint=False, blank=True, to='pttrack.DocumentType', null=True),
        ),
        migrations.AddField(
            model_name='historicaldocument',
            name='history_user',
            field=models.ForeignKey(related_name='+', on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL, null=True),
        ),
        migrations.AddField(
            model_name='historicaldocument',
            name='patient',
            field=models.ForeignKey(related_name='+', on_delete=django.db.models.deletion.DO_NOTHING, db_constraint=False, blank=True, to='pttrack.Patient', null=True),
        ),
        migrations.AddField(
            model_name='historicalactionitem',
            name='author',
            field=models.ForeignKey(related_name='+', on_delete=django.db.models.deletion.DO_NOTHING, db_constraint=False, blank=True, to='pttrack.Provider', null=True),
        ),
        migrations.AddField(
            model_name='historicalactionitem',
            name='author_type',
            field=models.ForeignKey(related_name='+', on_delete=django.db.models.deletion.DO_NOTHING, db_constraint=False, blank=True, to='pttrack.ProviderType', null=True),
        ),
        migrations.AddField(
            model_name='historicalactionitem',
            name='completion_author',
            field=models.ForeignKey(related_name='+', on_delete=django.db.models.deletion.DO_NOTHING, db_constraint=False, blank=True, to='pttrack.Provider', null=True),
        ),
        migrations.AddField(
            model_name='historicalactionitem',
            name='history_user',
            field=models.ForeignKey(related_name='+', on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL, null=True),
        ),
        migrations.AddField(
            model_name='historicalactionitem',
            name='instruction',
            field=models.ForeignKey(related_name='+', on_delete=django.db.models.deletion.DO_NOTHING, db_constraint=False, blank=True, to='pttrack.ActionInstruction', null=True),
        ),
        migrations.AddField(
            model_name='historicalactionitem',
            name='patient',
            field=models.ForeignKey(related_name='+', on_delete=django.db.models.deletion.DO_NOTHING, db_constraint=False, blank=True, to='pttrack.Patient', null=True),
        ),
        migrations.AddField(
            model_name='document',
            name='author',
            field=models.ForeignKey(to='pttrack.Provider'),
        ),
        migrations.AddField(
            model_name='document',
            name='author_type',
            field=models.ForeignKey(to='pttrack.ProviderType'),
        ),
        migrations.AddField(
            model_name='document',
            name='document_type',
            field=models.ForeignKey(to='pttrack.DocumentType'),
        ),
        migrations.AddField(
            model_name='document',
            name='patient',
            field=models.ForeignKey(to='pttrack.Patient'),
        ),
        migrations.AddField(
            model_name='actionitem',
            name='author',
            field=models.ForeignKey(to='pttrack.Provider'),
        ),
        migrations.AddField(
            model_name='actionitem',
            name='author_type',
            field=models.ForeignKey(to='pttrack.ProviderType'),
        ),
        migrations.AddField(
            model_name='actionitem',
            name='completion_author',
            field=models.ForeignKey(related_name='action_items_completed', blank=True, to='pttrack.Provider', null=True),
        ),
        migrations.AddField(
            model_name='actionitem',
            name='instruction',
            field=models.ForeignKey(to='pttrack.ActionInstruction'),
        ),
        migrations.AddField(
            model_name='actionitem',
            name='patient',
            field=models.ForeignKey(to='pttrack.Patient'),
        ),
        migrations.AlterField(
            model_name='actionitem',
            name='comments',
            field=models.TextField(max_length=300),
        ),
        migrations.AlterField(
            model_name='historicalactionitem',
            name='comments',
            field=models.TextField(max_length=300),
        ),
        migrations.AlterField(
            model_name='actionitem',
            name='comments',
            field=models.TextField(),
        ),
        migrations.AlterField(
            model_name='historicalactionitem',
            name='comments',
            field=models.TextField(),
        ),
        migrations.AlterField(
            model_name='provider',
            name='phone',
            field=models.CharField(max_length=40, null=True, blank=True),
        ),
        migrations.AddField(
            model_name='provider',
            name='needs_updating',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='provider',
            name='first_name',
            field=models.CharField(max_length=100, validators=[pttrack.validators.validate_name]),
        ),
        migrations.AlterField(
            model_name='provider',
            name='last_name',
            field=models.CharField(max_length=100, validators=[pttrack.validators.validate_name]),
        ),
        migrations.AlterField(
            model_name='provider',
            name='middle_name',
            field=models.CharField(blank=True, max_length=100, validators=[pttrack.validators.validate_name]),
        ),
        migrations.AddField(
            model_name='historicalpatient',
            name='case_manager',
            field=models.ForeignKey(related_name='+', on_delete=django.db.models.deletion.DO_NOTHING, db_constraint=False, blank=True, to='pttrack.Provider', null=True),
        ),
        migrations.AddField(
            model_name='patient',
            name='case_manager',
            field=models.ForeignKey(blank=True, to='pttrack.Provider', null=True),
        ),
        migrations.AlterField(
            model_name='historicalpatient',
            name='date_of_birth',
            field=models.DateField(help_text=b'MM/DD/YYYY', validators=[pttrack.validators.validate_birth_date]),
        ),
        migrations.AlterField(
            model_name='patient',
            name='date_of_birth',
            field=models.DateField(help_text=b'MM/DD/YYYY', validators=[pttrack.validators.validate_birth_date]),
        ),
        migrations.CreateModel(
            name='Outcome',
            fields=[
                ('name', models.CharField(max_length=50, serialize=False, primary_key=True)),
            ],
        ),
        migrations.AddField(
            model_name='historicalpatient',
            name='outcome',
            field=models.ForeignKey(related_name='+', on_delete=django.db.models.deletion.DO_NOTHING, db_constraint=False, blank=True, to='pttrack.Outcome', null=True),
        ),
        migrations.AddField(
            model_name='patient',
            name='outcome',
            field=models.ForeignKey(default='NA', blank=True, to='pttrack.Outcome', null=True),
            preserve_default=False,
        ),
    ]
