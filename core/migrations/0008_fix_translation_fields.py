from django.db import migrations

def copy_nl_to_de(apps, schema_editor):
    """Copy Dutch translation data to German fields if they exist"""
    ContactMessage = apps.get_model('core', 'ContactMessage')
    FAQ = apps.get_model('core', 'FAQ')
    Notification = apps.get_model('core', 'Notification')
    SiteSetting = apps.get_model('core', 'SiteSetting')
    Currency = apps.get_model('core', 'Currency')

    # Helper function to safely get nl field value
    def get_nl_value(obj, field):
        try:
            return getattr(obj, f'{field}_nl')
        except AttributeError:
            return None

    # Copy ContactMessage translations
    for obj in ContactMessage.objects.all():
        obj.message_de = get_nl_value(obj, 'message') or obj.message_de
        obj.subject_de = get_nl_value(obj, 'subject') or obj.subject_de
        obj.save()

    # Copy FAQ translations
    for obj in FAQ.objects.all():
        obj.question_de = get_nl_value(obj, 'question') or obj.question_de
        obj.answer_de = get_nl_value(obj, 'answer') or obj.answer_de
        obj.save()

    # Copy Notification translations
    for obj in Notification.objects.all():
        obj.title_de = get_nl_value(obj, 'title') or obj.title_de
        obj.message_de = get_nl_value(obj, 'message') or obj.message_de
        obj.save()

    # Copy SiteSetting translations
    for obj in SiteSetting.objects.all():
        obj.site_name_de = get_nl_value(obj, 'site_name') or obj.site_name_de
        obj.address_de = get_nl_value(obj, 'address') or obj.address_de
        obj.about_us_de = get_nl_value(obj, 'about_us') or obj.about_us_de
        obj.privacy_policy_de = get_nl_value(obj, 'privacy_policy') or obj.privacy_policy_de
        obj.terms_conditions_de = get_nl_value(obj, 'terms_conditions') or obj.terms_conditions_de
        obj.save()

    # Copy Currency translations
    for obj in Currency.objects.all():
        obj.name_de = get_nl_value(obj, 'name') or obj.name_de
        obj.save()

class Migration(migrations.Migration):

    dependencies = [
        ('core', '0007_rename_message_nl_contactmessage_message_de_and_more'),
    ]

    operations = [
        migrations.RunPython(copy_nl_to_de, reverse_code=migrations.RunPython.noop),
    ]