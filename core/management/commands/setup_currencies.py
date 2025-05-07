from django.core.management.base import BaseCommand
from core.models import Currency

class Command(BaseCommand):
    help = 'Set up initial currency data'

    def handle(self, *args, **options):
        currencies = [
            {
                'code': 'USD',
                'name': 'US Dollar',
                'symbol': '$',
                'exchange_rate': 1.0,  # Base currency
            },
            {
                'code': 'EUR',
                'name': 'Euro',
                'symbol': '€',
                'exchange_rate': 0.92,  # Initial rate, will be updated
            },
            {
                'code': 'GBP',
                'name': 'British Pound',
                'symbol': '£',
                'exchange_rate': 0.79,  # Initial rate, will be updated
            },
            {
                'code': 'EGP',
                'name': 'Egyptian Pound',
                'symbol': 'E£',
                'exchange_rate': 30.90,  # Initial rate, will be updated
            },
        ]
        
        created_count = 0
        updated_count = 0
        
        for currency_data in currencies:
            currency, created = Currency.objects.update_or_create(
                code=currency_data['code'],
                defaults={
                    'name': currency_data['name'],
                    'symbol': currency_data['symbol'],
                    'exchange_rate': currency_data['exchange_rate'],
                    'is_active': True,
                }
            )
            
            if created:
                created_count += 1
            else:
                updated_count += 1
        
        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully set up currencies: {created_count} created, {updated_count} updated'
            )
        )