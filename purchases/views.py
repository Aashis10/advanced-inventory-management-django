from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Sum
from django.shortcuts import get_object_or_404, redirect, render

from accounts.permissions import staff_required

from .forms import PurchaseForm
from .models import Purchase


@login_required
def purchase_list(request):
    purchases = Purchase.objects.select_related('product', 'created_by').all()
    supplier = request.GET.get('supplier', '').strip()
    payment = request.GET.get('payment', '').strip()
    date_from = request.GET.get('date_from', '').strip()
    date_to = request.GET.get('date_to', '').strip()

    if supplier:
        purchases = purchases.filter(supplier_name__icontains=supplier)
    if payment:
        purchases = purchases.filter(payment_method=payment)
    if date_from:
        purchases = purchases.filter(purchase_date__date__gte=date_from)
    if date_to:
        purchases = purchases.filter(purchase_date__date__lte=date_to)

    summary = purchases.aggregate(
        total_cost=Sum('total_price'),
        total_balance=Sum('balance_due'),
    )
    paginator = Paginator(purchases, 12)
    page_obj = paginator.get_page(request.GET.get('page'))
    return render(
        request,
        'purchases/purchase_list.html',
        {
            'page_obj': page_obj,
            'summary': summary,
            'supplier': supplier,
            'payment': payment,
            'date_from': date_from,
            'date_to': date_to,
            'payment_choices': Purchase.PAYMENT_METHOD_CHOICES,
        },
    )


@staff_required
def purchase_create(request):
    form = PurchaseForm(request.POST or None)
    if form.is_valid():
        purchase = form.save(commit=False)
        purchase.created_by = request.user
        purchase.save()
        messages.success(request, 'Purchase recorded and stock updated successfully.')
        return redirect('purchases:list')
    return render(request, 'purchases/purchase_form.html', {'form': form, 'title': 'Record Purchase'})


@staff_required
def purchase_update(request, pk):
    purchase = get_object_or_404(Purchase, pk=pk)
    form = PurchaseForm(request.POST or None, instance=purchase)
    if form.is_valid():
        updated = form.save(commit=False)
        updated.created_by = purchase.created_by
        updated.save()
        messages.success(request, 'Purchase updated successfully.')
        return redirect('purchases:list')
    return render(request, 'purchases/purchase_form.html', {'form': form, 'title': 'Edit Purchase'})
