from modeltranslation.translator import register, TranslationOptions
from .models import SiteSetting, FAQ, Currency, ContactMessage, Notification


@register(SiteSetting)
class SiteSettingTranslationOptions(TranslationOptions):
    fields = ('site_name', 'address', 'about_us', 'privacy_policy', 'terms_conditions')


@register(FAQ)
class FAQTranslationOptions(TranslationOptions):
    fields = ('question', 'answer')


@register(Currency)
class CurrencyTranslationOptions(TranslationOptions):
    fields = ('name',)


# Note: Translating user-submitted content like ContactMessage might not always be desired
# depending on the application's requirements. Registering it here for completeness.
@register(ContactMessage)
class ContactMessageTranslationOptions(TranslationOptions):
    fields = ('subject', 'message')


@register(Notification)
class NotificationTranslationOptions(TranslationOptions):
    fields = ('title', 'message')
