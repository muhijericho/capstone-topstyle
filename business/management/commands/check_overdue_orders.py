from django.core.management.base import BaseCommand
from business.views import check_and_update_overdue_orders


class Command(BaseCommand):
    help = 'Check and update overdue rental orders'

    def handle(self, *args, **options):
        try:
            updated_count = check_and_update_overdue_orders()
            
            if updated_count > 0:
                self.stdout.write(
                    self.style.SUCCESS(
                        f'Successfully updated {updated_count} overdue order(s)'
                    )
                )
            else:
                self.stdout.write(
                    self.style.WARNING('No overdue orders found')
                )
                
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error checking overdue orders: {str(e)}')
            )


