from decimal import Decimal
from datetime import timedelta
from random import Random
from typing import Iterable

from django.contrib.auth.models import Group, User
from django.core.management.base import BaseCommand
from django.utils import timezone

from products.models import Category, Product
from purchases.models import Purchase
from sales.models import Sale


class Command(BaseCommand):
    help = 'Seed demo data for Aashish Tech Suppliers Inventory System'

    def _seed_purchases(
        self,
        products: Iterable[Product],
        created_by: User,
        rng: Random,
    ) -> int:
        if Purchase.objects.exists():
            return 0

        purchase_total = 0
        methods = ['cash', 'bank', 'online']
        suppliers = [
            'Aashish Electronics Wholesale',
            'Metro IT Distribution',
            'SmartTech Sourcing Hub',
            'Kathmandu Device Supply',
            'Prime Network Traders',
            'Future Tech Imports',
            'Vertex Components Nepal',
            'Digital Frontier Supply',
        ]

        for idx, product in enumerate(products):
            quantity = rng.randint(4, 14)
            buy_price = (product.price * Decimal('0.72')).quantize(Decimal('0.01'))
            total_price = (buy_price * quantity).quantize(Decimal('0.01'))
            paid_ratio = Decimal(str(rng.choice([0.5, 0.7, 0.85, 1.0])))
            amount_paid = (total_price * paid_ratio).quantize(Decimal('0.01'))
            purchase_date = timezone.now() - timedelta(days=rng.randint(20, 170), hours=rng.randint(0, 23))

            Purchase.objects.create(
                supplier_name=product.supplier_name or suppliers[idx % len(suppliers)],
                product=product,
                quantity=quantity,
                purchase_price=buy_price,
                payment_method=methods[idx % len(methods)],
                amount_paid=amount_paid,
                purchase_date=purchase_date,
                created_by=created_by,
            )
            purchase_total += 1

        return purchase_total

    def _seed_sales(self, products: Iterable[Product], sold_by: User, rng: Random) -> int:
        if Sale.objects.exists():
            return 0

        sale_total = 0
        methods = ['cash', 'bank', 'online']
        buyers = [
            'Nabin Technologies',
            'Sita Enterprises',
            'Everest Education Center',
            'Himal Office Solutions',
            'Walk-in Customer',
            'Kiran Trading Co.',
        ]

        for month_offset in range(6):
            for idx, product in enumerate(products):
                if product.quantity <= max(product.reorder_level, 2):
                    continue

                quantity = rng.randint(1, min(5, max(2, product.quantity // 3)))
                total = (product.price * quantity).quantize(Decimal('0.01'))
                paid_ratio = Decimal(str(rng.choice([0.6, 0.8, 1.0])))
                amount_paid = (total * paid_ratio).quantize(Decimal('0.01'))

                sale = Sale.objects.create(
                    product=product,
                    buyer_name=buyers[(idx + month_offset) % len(buyers)],
                    quantity=quantity,
                    payment_method=methods[(idx + month_offset) % len(methods)],
                    amount_paid=amount_paid,
                    sold_by=sold_by,
                )

                sale_date = timezone.now() - timedelta(
                    days=(month_offset * 30) + rng.randint(0, 20),
                    hours=rng.randint(0, 23),
                )
                Sale.objects.filter(pk=sale.pk).update(date=sale_date)
                sale_total += 1

        return sale_total

    def handle(self, *args: object, **options: object):
        categories = [
            ('Laptops', 'fa-solid fa-laptop', 'Business and creator-grade laptops for daily operations.'),
            ('Desktop Computers', 'fa-solid fa-desktop', 'Performance desktop towers and all-in-one computers.'),
            ('Smartphones', 'fa-solid fa-mobile-screen-button', 'Flagship and productivity smartphones for teams.'),
            ('Monitors', 'fa-solid fa-display', 'Professional and ultra-wide monitors for office setups.'),
            ('Computer Accessories', 'fa-solid fa-keyboard', 'Keyboards, mice, webcams, and productivity accessories.'),
            ('Storage Devices', 'fa-solid fa-hard-drive', 'Fast SSDs and reliable external backup drives.'),
            ('Networking Devices', 'fa-solid fa-wifi', 'Routers and networking hardware for connected offices.'),
            ('Gaming Equipment', 'fa-solid fa-gamepad', 'Consoles and gaming peripherals for entertainment zones.'),
            ('Printers', 'fa-solid fa-print', 'Laser and inkjet printers for office documentation.'),
            ('Office Electronics', 'fa-solid fa-building', 'Essential electronics supporting office workflows.'),
        ]
        category_map = {}
        for name, icon, desc in categories:
            category_map[name], _ = Category.objects.get_or_create(
                name=name,
                defaults={'icon': icon, 'description': desc},
            )

        products = [
            ('Dell XPS 13', 'Dell', 'Laptops', 'Aashish Electronics Wholesale', Decimal('1299.00'), 8, 4),
            ('MacBook Air M2', 'Apple', 'Laptops', 'Metro IT Distribution', Decimal('1199.00'), 12, 5),
            ('Lenovo ThinkPad X1', 'Lenovo', 'Laptops', 'SmartTech Sourcing Hub', Decimal('1399.00'), 5, 3),
            ('HP Spectre x360', 'HP', 'Laptops', 'Future Tech Imports', Decimal('1249.00'), 7, 3),
            ('Apple iMac', 'Apple', 'Desktop Computers', 'Metro IT Distribution', Decimal('1799.00'), 4, 2),
            ('Dell OptiPlex', 'Dell', 'Desktop Computers', 'Aashish Electronics Wholesale', Decimal('849.00'), 10, 4),
            ('HP Pavilion Desktop', 'HP', 'Desktop Computers', 'Future Tech Imports', Decimal('899.00'), 9, 4),
            ('iPhone 15', 'Apple', 'Smartphones', 'Digital Frontier Supply', Decimal('999.00'), 15, 5),
            ('Samsung Galaxy S24', 'Samsung', 'Smartphones', 'Vertex Components Nepal', Decimal('899.00'), 13, 5),
            ('Google Pixel 8', 'Google', 'Smartphones', 'Prime Network Traders', Decimal('799.00'), 9, 4),
            ('OnePlus 12', 'OnePlus', 'Smartphones', 'Kathmandu Device Supply', Decimal('749.00'), 10, 4),
            ('Dell UltraSharp Monitor', 'Dell', 'Monitors', 'Aashish Electronics Wholesale', Decimal('459.00'), 6, 3),
            ('Logitech MX Master 3 Mouse', 'Logitech', 'Computer Accessories', 'Vertex Components Nepal', Decimal('109.00'), 30, 10),
            ('Keychron K8 Mechanical Keyboard', 'Keychron', 'Computer Accessories', 'SmartTech Sourcing Hub', Decimal('99.00'), 22, 8),
            ('Anker USB-C Hub', 'Anker', 'Computer Accessories', 'Digital Frontier Supply', Decimal('49.00'), 25, 8),
            ('Logitech C920 Webcam', 'Logitech', 'Computer Accessories', 'Metro IT Distribution', Decimal('79.00'), 18, 6),
            ('TP-Link Archer AX55 Router', 'TP-Link', 'Networking Devices', 'Prime Network Traders', Decimal('149.00'), 14, 5),
            ('Netgear Nighthawk AX5400', 'Netgear', 'Networking Devices', 'Prime Network Traders', Decimal('229.00'), 9, 4),
            ('Ubiquiti UniFi Access Point', 'Ubiquiti', 'Networking Devices', 'Future Tech Imports', Decimal('179.00'), 5, 3),
            ('Samsung 990 Pro SSD', 'Samsung', 'Storage Devices', 'Vertex Components Nepal', Decimal('189.00'), 16, 6),
            ('WD Black NVMe SSD', 'Western Digital', 'Storage Devices', 'Digital Frontier Supply', Decimal('159.00'), 12, 5),
            ('Seagate 2TB External HDD', 'Seagate', 'Storage Devices', 'SmartTech Sourcing Hub', Decimal('89.00'), 20, 7),
            ('SanDisk Extreme Portable SSD', 'SanDisk', 'Storage Devices', 'Kathmandu Device Supply', Decimal('139.00'), 10, 4),
            ('Sony PlayStation 5', 'Sony', 'Gaming Equipment', 'Metro IT Distribution', Decimal('499.00'), 6, 3),
            ('Xbox Series X', 'Microsoft', 'Gaming Equipment', 'Aashish Electronics Wholesale', Decimal('499.00'), 5, 3),
            ('Razer BlackShark Headset', 'Razer', 'Gaming Equipment', 'Digital Frontier Supply', Decimal('129.00'), 15, 5),
            ('Logitech G Pro Gaming Mouse', 'Logitech', 'Gaming Equipment', 'Vertex Components Nepal', Decimal('89.00'), 17, 6),
            ('Canon Pixma Printer', 'Canon', 'Printers', 'Kathmandu Device Supply', Decimal('199.00'), 11, 4),
            ('Epson EcoTank Printer', 'Epson', 'Printers', 'Future Tech Imports', Decimal('299.00'), 8, 3),
            ('Brother Laser Printer', 'Brother', 'Printers', 'Prime Network Traders', Decimal('259.00'), 7, 3),
            ('ViewSonic Office Projector', 'ViewSonic', 'Office Electronics', 'Metro IT Distribution', Decimal('649.00'), 4, 2),
            ('APC Smart UPS 1500', 'APC', 'Office Electronics', 'SmartTech Sourcing Hub', Decimal('389.00'), 6, 2),
        ]

        for name, brand, category_name, supplier_name, price, quantity, reorder in products:
            Product.objects.update_or_create(
                name=name,
                defaults={
                    'brand': brand,
                    'supplier_name': supplier_name,
                    'category': category_map[category_name],
                    'price': price,
                    'quantity': quantity,
                    'reorder_level': reorder,
                },
            )

        admin_group, _ = Group.objects.get_or_create(name='Admin')
        staff_group, _ = Group.objects.get_or_create(name='Staff')

        admin_user, created = User.objects.get_or_create(username='admin')
        if created:
            admin_user.set_password('admin12345')
            admin_user.is_staff = True
            admin_user.is_superuser = True
            admin_user.save()
        admin_user.groups.add(admin_group)

        staff_user, created = User.objects.get_or_create(username='staff')
        if created:
            staff_user.set_password('staff12345')
            staff_user.is_staff = True
            staff_user.save()
        staff_user.groups.add(staff_group)

        rng = Random(2026)
        products_for_transactions = list(Product.objects.select_related('category').all())
        purchases_seeded = self._seed_purchases(products_for_transactions, admin_user, rng)
        sales_seeded = self._seed_sales(products_for_transactions, staff_user, rng)

        self.stdout.write(
            self.style.SUCCESS(
                f'Demo data seeded successfully. Purchases created: {purchases_seeded}, Sales created: {sales_seeded}.'
            )
        )
