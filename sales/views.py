from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Sum
from django.shortcuts import redirect, render

from accounts.permissions import staff_required

from .forms import SaleForm
from .models import Sale


@login_required
def sale_list(request):
	sales = Sale.objects.select_related('product', 'sold_by').all()
	payment = request.GET.get('payment', '').strip()
	buyer = request.GET.get('buyer', '').strip()
	date_from = request.GET.get('date_from', '').strip()
	date_to = request.GET.get('date_to', '').strip()

	if payment:
		sales = sales.filter(payment_method=payment)
	if buyer:
		sales = sales.filter(buyer_name__icontains=buyer)
	if date_from:
		sales = sales.filter(date__date__gte=date_from)
	if date_to:
		sales = sales.filter(date__date__lte=date_to)

	summary = sales.aggregate(
		total_revenue=Sum('total_price'),
		total_profit=Sum('profit'),
		total_balance=Sum('balance_due'),
	)
	paginator = Paginator(sales, 12)
	page_obj = paginator.get_page(request.GET.get('page'))
	return render(
		request,
		'sales/sale_list.html',
		{
			'page_obj': page_obj,
			'summary': summary,
			'payment': payment,
			'buyer': buyer,
			'date_from': date_from,
			'date_to': date_to,
			'payment_choices': Sale.PAYMENT_METHOD_CHOICES,
		},
	)


@staff_required
def sale_create(request):
	form = SaleForm(request.POST or None)
	if form.is_valid():
		sale = form.save(commit=False)
		sale.sold_by = request.user
		sale.save()
		messages.success(request, 'Sale recorded and stock updated successfully.')
		return redirect('sales:list')
	return render(request, 'sales/sale_form.html', {'form': form})
