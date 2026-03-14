from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Count, F, Q, Sum
from django.shortcuts import get_object_or_404, redirect, render

from accounts.permissions import admin_required, staff_required
from purchases.models import Purchase
from sales.models import Sale

from .forms import CategoryForm, ProductForm
from .models import ActivityLog, Category, Product


@login_required
def product_list(request):
	search = request.GET.get('search', '').strip()
	category_id = request.GET.get('category', '')
	brand = request.GET.get('brand', '').strip()
	stock = request.GET.get('stock', '')
	sort = request.GET.get('sort', '-created_at')

	queryset = Product.objects.select_related('category').all()

	if search:
		queryset = queryset.filter(
			Q(name__icontains=search)
			| Q(brand__icontains=search)
			| Q(category__name__icontains=search)
		)

	if category_id:
		queryset = queryset.filter(category_id=category_id)

	if brand:
		queryset = queryset.filter(brand__iexact=brand)

	if stock == 'in':
		queryset = queryset.filter(quantity__gt=F('reorder_level'))
	elif stock == 'low':
		queryset = queryset.filter(quantity__gt=0, quantity__lte=F('reorder_level'))
	elif stock == 'out':
		queryset = queryset.filter(quantity=0)

	allowed_sorts = ['name', '-name', 'price', '-price', 'quantity', '-quantity', 'created_at', '-created_at']
	if sort not in allowed_sorts:
		sort = '-created_at'
	queryset = queryset.order_by(sort)

	paginator = Paginator(queryset, 8)
	page_obj = paginator.get_page(request.GET.get('page'))

	context = {
		'page_obj': page_obj,
		'categories': Category.objects.all(),
		'brands': Product.objects.exclude(brand='').values_list('brand', flat=True).distinct().order_by('brand'),
		'search': search,
		'category_id': category_id,
		'brand': brand,
		'stock': stock,
		'sort': sort,
		'search_suggestions': Product.objects.values_list('name', flat=True)[:50],
	}
	return render(request, 'products/product_list.html', context)


@login_required
def product_detail(request, pk):
	product = get_object_or_404(Product.objects.select_related('category'), pk=pk)
	recent_sales = Sale.objects.filter(product=product).select_related('sold_by').order_by('-date')[:8]
	sales_summary = Sale.objects.filter(product=product).aggregate(
		total_sold=Sum('quantity'),
		total_revenue=Sum('total_price'),
		total_profit=Sum('profit'),
	)
	latest_purchase = Purchase.objects.filter(product=product).order_by('-purchase_date').first()
	return render(
		request,
		'products/product_detail.html',
		{
			'product': product,
			'recent_sales': recent_sales,
			'sales_summary': sales_summary,
			'latest_supplier': latest_purchase.supplier_name if latest_purchase else 'Not available',
		},
	)


@staff_required
def product_create(request):
	form = ProductForm(request.POST or None, request.FILES or None)
	if form.is_valid():
		product = form.save()
		ActivityLog.record(
			action='product_added',
			message=f'Product {product.name} added by {request.user.username}',
			related_product=product,
			user=request.user,
		)
		messages.success(request, 'Product added successfully.')
		return redirect('products:list')
	return render(request, 'products/product_form.html', {'form': form, 'title': 'Add Product'})


@staff_required
def product_update(request, pk):
	product = get_object_or_404(Product, pk=pk)
	form = ProductForm(request.POST or None, request.FILES or None, instance=product)
	if form.is_valid():
		product = form.save()
		ActivityLog.record(
			action='stock_updated',
			message=f'{product.name} stock updated by {request.user.username}',
			related_product=product,
			user=request.user,
		)
		messages.success(request, 'Product updated successfully.')
		return redirect('products:list')
	return render(request, 'products/product_form.html', {'form': form, 'title': 'Edit Product'})


@staff_required
def product_delete(request, pk):
	product = get_object_or_404(Product, pk=pk)
	if request.method == 'POST':
		product.delete()
		messages.warning(request, 'Product deleted successfully.')
		return redirect('products:list')
	return render(request, 'products/product_confirm_delete.html', {'product': product})


@login_required
def category_list(request):
	categories = Category.objects.annotate(product_count=Count('products')).order_by('name')
	return render(request, 'products/category_list.html', {'categories': categories})


@login_required
def category_detail(request, pk):
	category = get_object_or_404(Category.objects.annotate(product_count=Count('products')), pk=pk)
	products = category.products.all().order_by('name')
	return render(
		request,
		'products/category_detail.html',
		{
			'category': category,
			'products': products,
		},
	)


@staff_required
def category_create(request):
	form = CategoryForm(request.POST or None, request.FILES or None)
	if form.is_valid():
		form.save()
		messages.success(request, 'Category created successfully.')
		return redirect('products:category_list')
	return render(request, 'products/category_form.html', {'form': form, 'title': 'Add Category'})


@staff_required
def category_update(request, pk):
	category = get_object_or_404(Category, pk=pk)
	form = CategoryForm(request.POST or None, request.FILES or None, instance=category)
	if form.is_valid():
		form.save()
		messages.success(request, 'Category updated successfully.')
		return redirect('products:category_list')
	return render(request, 'products/category_form.html', {'form': form, 'title': 'Edit Category'})


@staff_required
def category_delete(request, pk):
	category = get_object_or_404(Category, pk=pk)
	if request.method == 'POST':
		category.delete()
		messages.warning(request, 'Category deleted successfully.')
		return redirect('products:category_list')
	return render(request, 'products/category_confirm_delete.html', {'category': category})

# Create your views here.
