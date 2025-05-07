import requests
from decimal import Decimal
from django.core.management.base import BaseCommand
from django.utils import timezone
from core.models import Currency
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Update currency exchange rates from external API'

    def handle(self, *args, **options):
        base_currency = 'USD'  # Base currency is USD
        
        # Fetch exchange rates from API
        try:
            response = requests.get(f'https://api.exchangerate.host/latest?base={base_currency}')
            data = response.json()
            
            if not data.get('success', False) and 'rates' not in data:
                self.stdout.write(self.style.ERROR('Failed to fetch exchange rates'))
                return
                
            rates = data.get('rates', {})
            
            # Update each currency in the database
            currencies = Currency.objects.all()
            updated_count = 0
            
            for currency in currencies:
                if currency.code in rates:
                    currency.exchange_rate = Decimal(str(rates[currency.code]))
                    currency.last_updated = timezone.now()
                    currency.save()
                    updated_count += 1
            
            self.stdout.write(
                self.style.SUCCESS(f'Successfully updated {updated_count} currency exchange rates')
            )
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error updating exchange rates: {str(e)}'))
            logger.error(f'Error updating exchange rates: {str(e)}')