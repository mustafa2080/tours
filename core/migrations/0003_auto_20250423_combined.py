from django.db import migrations, models
from django.db.utils import OperationalError


def field_exists(apps, schema_editor, table_name, column_name):
    with schema_editor.connection.cursor() as cursor:
        table_info = cursor.execute(f"PRAGMA table_info({table_name})")
        columns = [column[1] for column in table_info.fetchall()]
        return column_name in columns


def add_field_if_not_exists(apps, schema_editor):
    """Add fields only if they don't already exist"""
    fields_to_add = [
        ('core_contactmessage', 'message_de'),
        ('core_contactmessage', 'subject_de'),
        ('core_currency', 'name_de'),
        ('core_faq', 'answer_de'),
        ('core_faq', 'question_de'),
        ('core_notification', 'message_de'),
        ('core_notification', 'title_de'),
        ('core_sitesetting', 'about_us_de'),
        ('core_sitesetting', 'address_de'),
        ('core_sitesetting', 'privacy_policy_de'),
        ('core_sitesetting', 'site_name_de'),
        ('core_sitesetting', 'terms_conditions_de'),
    ]
    
    for table_name, column_name in fields_to_add:
        if not field_exists(apps, schema_editor, table_name, column_name):
            # Only execute the SQL if the column doesn't exist
            sql = f'ALTER TABLE {table_name} ADD COLUMN {column_name} text NULL'
            schema_editor.execute(sql)


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0002_rename_message_nl_contactmessage_message_de_and_more'),
    ]

    operations = [
        # Currency model changes - these are safe to apply
        migrations.AlterModelOptions(
            name='currency',
            options={'ordering': ['code'], 'verbose_name_plural': 'Currencies'},
        ),
        migrations.AddField(
            model_name='currency',
            name='is_active',
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name='currency',
            name='last_updated',
            field=models.DateTimeField(auto_now=True),
        ),
        migrations.AlterField(
            model_name='currency',
            name='code',
            field=models.CharField(max_length=3, unique=True),
        ),
        migrations.AlterField(
            model_name='currency',
            name='exchange_rate',
            field=models.DecimalField(decimal_places=6, default=1.0, max_digits=10),
        ),
        migrations.AlterField(
            model_name='currency',
            name='symbol',
            field=models.CharField(max_length=5),
        ),
        
        # Add German translation fields if they don't exist
        migrations.RunPython(add_field_if_not_exists),
    ]