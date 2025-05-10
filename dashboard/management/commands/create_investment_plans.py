from django.core.management.base import BaseCommand
from dashboard.models import InvestmentPlan

class Command(BaseCommand):
    help = 'Creates initial investment plans'

    def handle(self, *args, **kwargs):
        # Check if plans already exist
        if InvestmentPlan.objects.exists():
            self.stdout.write(self.style.WARNING('Investment plans already exist. Skipping creation.'))
            return

        # Create plans
        plans = [
            {
                'name': 'Starter Plan',
                'description': 'Perfect for beginners. Low risk with steady returns.',
                'minimum_amount': 100,
                'maximum_amount': 1000,
                'return_percentage': 5,
                'duration_days': 7,
            },
            {
                'name': 'Growth Plan',
                'description': 'Balanced risk and reward for intermediate investors.',
                'minimum_amount': 1000,
                'maximum_amount': 5000,
                'return_percentage': 10,
                'duration_days': 14,
            },
            {
                'name': 'Premium Plan',
                'description': 'Higher returns for experienced investors.',
                'minimum_amount': 5000,
                'maximum_amount': 20000,
                'return_percentage': 15,
                'duration_days': 30,
            },
            {
                'name': 'Elite Plan',
                'description': 'Maximum returns for serious investors.',
                'minimum_amount': 20000,
                'maximum_amount': 100000,
                'return_percentage': 25,
                'duration_days': 60,
            },
        ]

        for plan_data in plans:
            InvestmentPlan.objects.create(**plan_data)
            self.stdout.write(self.style.SUCCESS(f'Created investment plan: {plan_data["name"]}'))

        self.stdout.write(self.style.SUCCESS('Successfully created all investment plans'))