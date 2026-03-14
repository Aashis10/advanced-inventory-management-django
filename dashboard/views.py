import json
from datetime import timedelta

from django.contrib.auth.decorators import login_required
from django.db.models import DecimalField, ExpressionWrapper
from django.db.models import Avg, Case, Count, F, Sum, Value, When
from django.db.models.functions import TruncMonth
from django.shortcuts import render
from django.utils import timezone

from products.models import Category, Product
from purchases.models import Purchase
from sales.models import Sale


@login_required
def home(request):
	now = timezone.now()
	since = now - timedelta(days=365)
	today = now.date()

	total_products = Product.objects.count()
	total_categories = Category.objects.count()
	total_inventory_value = Product.objects.aggregate(total=Sum(F('price') * F('quantity')))['total'] or 0
	products_sold_today = Sale.objects.filter(date__date=today).aggregate(total=Sum('quantity'))['total'] or 0

	low_stock_products = Product.objects.filter(quantity__lte=F('reorder_level')).order_by('quantity', 'name')[:6]

	category_distribution = (
		Sale.objects.filter(date__gte=since)
		.values('product__category__name')
		.annotate(total=Sum('total_price'))
		.order_by('-total')
	)
	monthly_sales = (
		Sale.objects.filter(date__gte=since)
		.annotate(month=TruncMonth('date'))
		.values('month')
		.annotate(total=Sum('total_price'))
		.order_by('month')
	)
	top_selling = (
		Sale.objects.values('product__name')
		.annotate(total_qty=Sum('quantity'))
		.order_by('-total_qty')[:5]
	)

	low_stock_rows = []
	for item in low_stock_products:
		reorder_amount = max(item.reorder_level * 2 - item.quantity, item.reorder_level)
		low_stock_rows.append({
			'name': item.name,
			'quantity': item.quantity,
			'reorder_suggestion': reorder_amount,
		})

	context = {
		'total_products': total_products,
		'total_categories': total_categories,
		'total_inventory_value': total_inventory_value,
		'products_sold_today': products_sold_today,
		'low_stock_count': low_stock_products.count(),
		'low_stock_rows': low_stock_rows,
		'category_labels': json.dumps([item['product__category__name'] or 'Uncategorized' for item in category_distribution]),
		'category_values': json.dumps([float(item['total']) for item in category_distribution]),
		'monthly_labels': json.dumps([item['month'].strftime('%b %Y') for item in monthly_sales]),
		'monthly_values': json.dumps([float(item['total']) for item in monthly_sales]),
		'top_labels': json.dumps([item['product__name'] for item in top_selling]),
		'top_values': json.dumps([item['total_qty'] for item in top_selling]),
	}
	return render(request, 'dashboard/dashboard.html', context)


@login_required
def settings_page(request):
	return render(request, 'dashboard/settings.html')


@login_required
def analytics_page(request):
	now = timezone.now()
	range_days = request.GET.get('range', '365')
	if range_days not in {'30', '90', '180', '365'}:
		range_days = '365'
	since = now - timedelta(days=int(range_days))

	monthly_revenue = (
		Sale.objects.filter(date__gte=since)
		.annotate(month=TruncMonth('date'))
		.values('month')
		.annotate(total=Sum('total_price'))
		.order_by('month')
	)
	monthly_profit = (
		Sale.objects.filter(date__gte=since)
		.annotate(month=TruncMonth('date'))
		.values('month')
		.annotate(total=Sum('profit'))
		.order_by('month')
	)
	profit_margin = (
		Sale.objects.filter(date__gte=since)
		.annotate(
			month=TruncMonth('date'),
			margin=ExpressionWrapper(
				(F('profit') * Value(100.0)) / F('total_price'),
				output_field=DecimalField(max_digits=8, decimal_places=2),
			),
		)
		.values('month')
		.annotate(avg_margin=Avg('margin'))
		.order_by('month')
	)
	stock_trend = Product.objects.aggregate(
		in_stock=Count(Case(When(quantity__gt=F('reorder_level'), then=Value(1)))),
		low_stock=Count(Case(When(quantity__gt=0, quantity__lte=F('reorder_level'), then=Value(1)))),
		out_of_stock=Count(Case(When(quantity=0, then=Value(1)))),
	)
	sales_by_category = (
		Sale.objects.values('product__category__name')
		.annotate(total=Sum('total_price'))
		.order_by('-total')
	)
	stock_movement = (
		Purchase.objects.filter(purchase_date__gte=since)
		.annotate(month=TruncMonth('purchase_date'))
		.values('month')
		.annotate(incoming=Sum('quantity'))
		.order_by('month')
	)
	sales_movement = (
		Sale.objects.filter(date__gte=since)
		.annotate(month=TruncMonth('date'))
		.values('month')
		.annotate(outgoing=Sum('quantity'))
		.order_by('month')
	)

	incoming_map = {item['month']: item['incoming'] or 0 for item in stock_movement}
	outgoing_map = {item['month']: item['outgoing'] or 0 for item in sales_movement}
	movement_months = sorted(set(incoming_map.keys()) | set(outgoing_map.keys()))

	context = {
		'selected_range': range_days,
		'sales_category_labels': json.dumps([i['product__category__name'] or 'Uncategorized' for i in sales_by_category]),
		'sales_category_values': json.dumps([float(i['total']) for i in sales_by_category]),
		'revenue_labels': json.dumps([i['month'].strftime('%b %Y') for i in monthly_revenue]),
		'revenue_values': json.dumps([float(i['total']) for i in monthly_revenue]),
		'profit_values': json.dumps([float(i['total']) for i in monthly_profit]),
		'margin_labels': json.dumps([i['month'].strftime('%b %Y') for i in profit_margin]),
		'margin_values': json.dumps([float(i['avg_margin']) for i in profit_margin]),
		'movement_labels': json.dumps([m.strftime('%b %Y') for m in movement_months]),
		'movement_incoming': json.dumps([incoming_map.get(m, 0) for m in movement_months]),
		'movement_outgoing': json.dumps([outgoing_map.get(m, 0) for m in movement_months]),
		'stock_snapshot_labels': json.dumps(['In Stock', 'Low Stock', 'Out of Stock']),
		'stock_snapshot_values': json.dumps([
			stock_trend['in_stock'],
			stock_trend['low_stock'],
			stock_trend['out_of_stock'],
		]),
	}
	return render(request, 'dashboard/analytics.html', context)


@login_required
def global_search(request):
	query = request.GET.get('q', '').strip()
	product_results = Product.objects.none()
	category_results = Category.objects.none()
	sale_results = Sale.objects.none()

	if query:
		product_results = Product.objects.filter(name__icontains=query).select_related('category')[:10]
		category_results = Category.objects.filter(name__icontains=query)[:10]
		sale_results = Sale.objects.filter(product__name__icontains=query).select_related('product', 'sold_by')[:10]

	context = {
		'query': query,
		'product_results': product_results,
		'category_results': category_results,
		'sale_results': sale_results,
	}
	return render(request, 'dashboard/search_results.html', context)

# Create your views here.
