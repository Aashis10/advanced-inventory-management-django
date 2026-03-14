import csv
from io import BytesIO

from django.contrib.auth.decorators import login_required
from django.db.models import F, Sum
from django.http import HttpResponse
from django.shortcuts import render
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas

from products.models import Product
from purchases.models import Purchase
from sales.models import Sale


def _pdf_response(filename):
	return HttpResponse(content_type='application/pdf', headers={'Content-Disposition': f'attachment; filename="{filename}"'})


def _build_pdf(title, headers, rows, filename):
	buffer = BytesIO()
	pdf = canvas.Canvas(buffer, pagesize=A4)
	width, height = A4
	y = height - 20 * mm

	pdf.setFont('Helvetica-Bold', 13)
	pdf.drawString(20 * mm, y, title)
	y -= 10 * mm

	pdf.setFont('Helvetica-Bold', 10)
	pdf.drawString(20 * mm, y, ' | '.join(headers))
	y -= 6 * mm

	pdf.setFont('Helvetica', 9)
	for row in rows:
		if y < 20 * mm:
			pdf.showPage()
			y = height - 20 * mm
			pdf.setFont('Helvetica', 9)
		pdf.drawString(20 * mm, y, ' | '.join(map(str, row))[:145])
		y -= 5 * mm

	pdf.save()
	buffer.seek(0)
	response = _pdf_response(filename)
	response.write(buffer.read())
	return response


@login_required
def reports_home(request):
	inventory_value = Product.objects.aggregate(total=Sum(F('price') * F('quantity')))['total'] or 0
	total_sales_value = Sale.objects.aggregate(total=Sum('total_price'))['total'] or 0
	total_purchase_value = Purchase.objects.aggregate(total=Sum('total_price'))['total'] or 0
	total_profit = Sale.objects.aggregate(total=Sum('profit'))['total'] or 0
	context = {
		'sales_count': Sale.objects.count(),
		'purchase_count': Purchase.objects.count(),
		'inventory_count': Product.objects.count(),
		'low_stock_count': Product.objects.filter(quantity__lte=F('reorder_level')).count(),
		'inventory_value': inventory_value,
		'total_sales_value': total_sales_value,
		'total_purchase_value': total_purchase_value,
		'total_profit': total_profit,
	}
	return render(request, 'reports/reports_home.html', context)


@login_required
def sales_report_csv(request):
	response = HttpResponse(content_type='text/csv')
	response['Content-Disposition'] = 'attachment; filename="sales_report.csv"'
	writer = csv.writer(response)
	writer.writerow(['Buyer', 'Product', 'Qty Sold', 'Payment', 'Total Price', 'Amount Paid', 'Balance Due', 'Profit', 'Date', 'Sold By'])
	for sale in Sale.objects.select_related('product', 'sold_by'):
		writer.writerow([
			sale.buyer_name,
			sale.product.name,
			sale.quantity,
			sale.get_payment_method_display(),
			sale.total_price,
			sale.amount_paid,
			sale.balance_due,
			sale.profit,
			sale.date.strftime('%Y-%m-%d %H:%M'),
			sale.sold_by.username,
		])
	return response


@login_required
def purchase_report_csv(request):
	response = HttpResponse(content_type='text/csv')
	response['Content-Disposition'] = 'attachment; filename="purchase_report.csv"'
	writer = csv.writer(response)
	writer.writerow(['Supplier', 'Product', 'Qty', 'Purchase Price', 'Total', 'Payment', 'Amount Paid', 'Balance Due', 'Date', 'Created By'])
	for purchase in Purchase.objects.select_related('product', 'created_by'):
		writer.writerow([
			purchase.supplier_name,
			purchase.product.name,
			purchase.quantity,
			purchase.purchase_price,
			purchase.total_price,
			purchase.get_payment_method_display(),
			purchase.amount_paid,
			purchase.balance_due,
			purchase.purchase_date.strftime('%Y-%m-%d %H:%M'),
			purchase.created_by.username,
		])
	return response


@login_required
def inventory_report_csv(request):
	response = HttpResponse(content_type='text/csv')
	response['Content-Disposition'] = 'attachment; filename="inventory_report.csv"'
	writer = csv.writer(response)
	writer.writerow(['Product', 'Category', 'Brand', 'Price', 'Quantity', 'Reorder Level', 'Inventory Value'])
	for product in Product.objects.select_related('category'):
		writer.writerow([product.name, product.category.name, product.brand, product.price, product.quantity, product.reorder_level, product.inventory_value])
	return response


@login_required
def low_stock_report_csv(request):
	response = HttpResponse(content_type='text/csv')
	response['Content-Disposition'] = 'attachment; filename="low_stock_report.csv"'
	writer = csv.writer(response)
	writer.writerow(['Product', 'Category', 'Quantity', 'Reorder Level'])
	for product in Product.objects.select_related('category').filter(quantity__lte=F('reorder_level')):
		writer.writerow([product.name, product.category.name, product.quantity, product.reorder_level])
	return response


@login_required
def sales_report_pdf(request):
	rows = [
		[sale.buyer_name, sale.product.name, sale.quantity, sale.total_price, sale.balance_due, sale.profit, sale.date.strftime('%Y-%m-%d')]
		for sale in Sale.objects.select_related('product', 'sold_by')
	]
	return _build_pdf('Sales Report', ['Buyer', 'Product', 'Qty', 'Total', 'Balance', 'Profit', 'Date'], rows, 'sales_report.pdf')


@login_required
def purchase_report_pdf(request):
	rows = [
		[
			purchase.supplier_name,
			purchase.product.name,
			purchase.quantity,
			purchase.total_price,
			purchase.balance_due,
			purchase.purchase_date.strftime('%Y-%m-%d'),
		]
		for purchase in Purchase.objects.select_related('product', 'created_by')
	]
	return _build_pdf('Purchase Report', ['Supplier', 'Product', 'Qty', 'Total', 'Balance', 'Date'], rows, 'purchase_report.pdf')


@login_required
def inventory_report_pdf(request):
	rows = [
		[product.name, product.category.name, product.brand, product.quantity]
		for product in Product.objects.select_related('category')
	]
	return _build_pdf('Inventory Report', ['Product', 'Category', 'Brand', 'Qty'], rows, 'inventory_report.pdf')


@login_required
def low_stock_report_pdf(request):
	rows = [
		[product.name, product.category.name, product.quantity, product.reorder_level]
		for product in Product.objects.select_related('category').filter(quantity__lte=F('reorder_level'))
	]
	return _build_pdf('Low Stock Report', ['Product', 'Category', 'Qty', 'Reorder'], rows, 'low_stock_report.pdf')


@login_required
def profit_report_csv(request):
	response = HttpResponse(content_type='text/csv')
	response['Content-Disposition'] = 'attachment; filename="profit_report.csv"'
	writer = csv.writer(response)
	writer.writerow(['Date', 'Product', 'Buyer', 'Revenue', 'Profit'])
	for sale in Sale.objects.select_related('product'):
		writer.writerow([
			sale.date.strftime('%Y-%m-%d'),
			sale.product.name,
			sale.buyer_name,
			sale.total_price,
			sale.profit,
		])
	return response


@login_required
def profit_report_pdf(request):
	rows = [
		[sale.date.strftime('%Y-%m-%d'), sale.product.name, sale.buyer_name, sale.total_price, sale.profit]
		for sale in Sale.objects.select_related('product')
	]
	return _build_pdf('Profit Report', ['Date', 'Product', 'Buyer', 'Revenue', 'Profit'], rows, 'profit_report.pdf')
