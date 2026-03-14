from django.apps import AppConfig
import os
import sys


class ProductsConfig(AppConfig):
    name = 'products'

    def ready(self):
        if os.environ.get('AUTO_SEED_DEMO_DATA', '1') != '1':
            return

        skipped_commands = {
            'migrate',
            'makemigrations',
            'collectstatic',
            'shell',
            'test',
            'check',
            'createsuperuser',
            'seed_demo_data',
            'dbshell',
        }

        if len(sys.argv) > 1 and sys.argv[1] in skipped_commands:
            return

        if len(sys.argv) > 1 and sys.argv[1] == 'runserver' and os.environ.get('RUN_MAIN') != 'true':
            return

        try:
            from django.core.management import call_command
            from django.db import connection
            from django.db.utils import OperationalError, ProgrammingError
            from products.models import Product

            try:
                existing_tables = set(connection.introspection.table_names())
            except (OperationalError, ProgrammingError):
                return

            if 'products_product' not in existing_tables:
                return

            if Product.objects.exists():
                return

            call_command('seed_demo_data', verbosity=0)
        except Exception:
            # App should never fail startup because of optional demo seeding.
            return
