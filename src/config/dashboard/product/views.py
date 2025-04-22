from django.template.response import TemplateResponse
from django.http import JsonResponse
from config.products.models import (Type, Categories, Products, ProductionProductInfo, ProductionProduct,
                                    ProductionProductStockItem, QuantityChange, Currency)
from config.user.models import User
from django.core.paginator import Paginator
from config.dashboard.views import staff_member_required
from .forms import TypeForm, CategoryForm, ProductForm, ProductionProductForm, ProductInfoForm, ProductProdactionCreateForm
from django.shortcuts import redirect
from django.conf import settings
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from config.dashboard.decorators import role_required
from . import services

def is_ajax(request):
    return request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest'


@staff_member_required
@role_required(['seo'])
def type_list(request):
    page = int(request.GET.get("page", 1))
    entries = int(request.GET.get("entries", 25))
    search = request.GET.get("search", "")
    types = Type.objects.all().order_by("-id")
    paginator = Paginator(types, entries)
    types = paginator.page(page)
    context = {
        "types": types,
        "entries_list": [5, 25, 50, 100, 250],
        "entries": entries,
        "search": search,
        "MEDIA_URL": settings.MEDIA_HOST
    }
    return TemplateResponse(request, 'product/type_list.html', context)


@staff_member_required
@role_required(['seo'])
def type_create(request):
    type_one = None
    form = TypeForm(request.POST or None)
    if request.POST:
        form = TypeForm(request.POST or None)
        if form.is_valid():
            form.save()
            return redirect(f"dashboard:type-list")
        else:
            print(form.errors)
    context = {
        'form': form,
        'type_one': type_one
    }
    return TemplateResponse(request, 'product/type_create.html', context)


@staff_member_required
@role_required(['seo'])
def type_edit(request, pk):
    type_one = Type.objects.filter(id=pk).first()
    form = TypeForm(request.POST or None, instance=type_one)
    if request.POST:
        form = TypeForm(request.POST or None, instance=type_one)
        if form.is_valid():
            form.save()
            return redirect(f"dashboard:type-list")
        else:
            print(form.errors)
    context = {
        'form': form,
        'type_one': type_one
    }
    return TemplateResponse(request, 'product/type_create.html', context)


@staff_member_required
@role_required(['seo', 'zav-sklad'])
def category_list(request):
    page = int(request.GET.get("page", 1))
    entries = int(request.GET.get("entries", 25))
    search = request.GET.get("search", "")
    categories = Categories.objects.all().order_by("-id")
    paginator = Paginator(categories, entries)
    categories = paginator.page(page)
    context = {
        "categories": categories,
        "entries_list": [5, 25, 50, 100, 250],
        "entries": entries,
        "search": search,
        "MEDIA_URL": settings.MEDIA_HOST
    }
    return TemplateResponse(request, 'product/category_list.html', context)


@staff_member_required
@role_required(['seo', 'zav-sklad'])
def category_create(request):
    category = None
    form = CategoryForm(request.POST or None)
    if request.POST:
        image = ""
        if request.FILES:
            path = default_storage.save(f"files/{request.FILES['file']}",
                                        ContentFile(request.FILES["file"].read()))
            image = f"/media/{path}"
        form = CategoryForm(request.POST or None, request.FILES or None, instance=Categories(
            image=image
        ))
        if form.is_valid():
            form.save()
            return redirect(f"dashboard:category-list")
        else:
            print(form.errors)
    context = {
        'form': form,
        'category': category
    }
    return TemplateResponse(request, 'product/category_form.html', context)


@staff_member_required
@role_required(['seo', 'zav-sklad'])
def category_edit(request, pk):
    category = Categories.objects.filter(id=pk).first()
    form = CategoryForm(request.POST or None, request.FILES or None, instance=category)
    if request.POST:
        form = CategoryForm(request.POST or None, request.FILES or None, instance=category)
        if request.FILES:
            path = default_storage.save(f"files/{request.FILES['file']}",
                                        ContentFile(request.FILES["file"].read()))
            category.image = f"/media/{path}"
        if form.is_valid():
            form.save()
            return redirect(f"dashboard:category-list")
        else:
            print(form.errors)
    context = {
        'form': form,
        'category': category
    }
    return TemplateResponse(request, 'product/category_form.html', context)


@staff_member_required
@role_required(['seo', 'manufacturer'])
def product_list(request):
    page = int(request.GET.get("page", 1))
    entries = int(request.GET.get("entries", 25))
    search = request.GET.get("search", "")
    products = Products.objects.all().order_by("-id")
    paginator = Paginator(products, entries)
    products = paginator.page(page)

    context = {
        "products": products,
        "entries_list": [5, 25, 50, 100, 250],
        "entries": entries,
        "search": search,
        "MEDIA_URL": settings.MEDIA_HOST,
        "type": "stock"
    }
    return TemplateResponse(request, 'product/product_list.html', context)


@staff_member_required
@role_required(['seo', 'manufacturer'])
def product_create(request):
    product = None
    form = ProductForm(request.POST or None)
    if request.POST:
        image = ""
        if request.FILES:
            path = default_storage.save(f"files/{request.FILES['file']}",
                                        ContentFile(request.FILES["file"].read()))
            image = f"/media/{path}"
        form = ProductForm(request.POST or None, request.FILES or None, instance=Products(
            images=[image]
        ))
        if form.is_valid():
            data = form.save()
            QuantityChange.objects.create(
                product=data,
                user=request.user,
                change_type='add',
                type='amount',
                quantity_changed=data.amount
            )
            return redirect(f"dashboard:product-list")
        else:
            print(form.errors)
    context = {
        'form': form,
        'product': product,
        'type': 'stock'
    }
    return TemplateResponse(request, 'product/form.html', context)


@staff_member_required
@role_required(['seo', 'manufacturer'])
def product_edit(request, pk):
    product = Products.objects.filter(id=pk).first()
    amount = product.amount
    form = ProductForm(request.POST or None, request.FILES or None, instance=product)
    if request.POST:
        form = ProductForm(request.POST or None, request.FILES or None, instance=product)
        if request.FILES:
            path = default_storage.save(f"files/{request.FILES['file']}",
                                        ContentFile(request.FILES["file"].read()))
            product.images = [f"/media/{path}"]
        if form.is_valid():
            data = form.save()
            QuantityChange.objects.create(
                product=data,
                user=request.user,
                change_type='add',
                type='amount',
                quantity_changed=abs(data.amount - amount)
            )
            return redirect(f"dashboard:product-list")
        else:
            print(form.errors)
    context = {
        'form': form,
        'product': product,
        'type': 'stock'
    }
    return TemplateResponse(request, 'product/form.html', context)


@staff_member_required
@role_required(['seo', 'manufacturer'])
def defect_list(request):
    page = int(request.GET.get("page", 1))
    entries = int(request.GET.get("entries", 25))
    search = request.GET.get("search", "")
    products = Products.objects.all().order_by("-id")
    paginator = Paginator(products, entries)
    products = paginator.page(page)
    context = {
        "products": products,
        "entries_list": [5, 25, 50, 100, 250],
        "entries": entries,
        "search": search,
        "MEDIA_URL": settings.MEDIA_HOST
    }
    return TemplateResponse(request, 'product/defect_list.html', context)


@staff_member_required
@role_required(['seo', 'manufacturer'])
def defect_edit(request, pk):
    product = Products.objects.filter(id=pk).first()
    defect = product.defect
    form = ProductForm(request.POST or None, request.FILES or None, instance=product)
    if request.POST:
        form = ProductForm(request.POST or None, request.FILES or None, instance=product)
        if request.FILES:
            path = default_storage.save(f"files/{request.FILES['file']}",
                                        ContentFile(request.FILES["file"].read()))
            product.images = [f"/media/{path}"]
        if form.is_valid():
            data = form.save()
            QuantityChange.objects.create(
                product=data,
                user=request.user,
                change_type='add',
                type='defect',
                quantity_changed=(data.defect - defect)
            )
            return redirect(f"dashboard:defect-list")
        else:
            print(form.errors)
    context = {
        'form': form,
        'product': product,
        'type': 'defect'
    }
    return TemplateResponse(request, 'product/form.html', context)


@staff_member_required
@role_required(['seo', 'agent', 'zav-sklad', 'manufacturer', 'accountant'])
def production_product_list(request):
    page = int(request.GET.get("page", 1))
    entries = int(request.GET.get("entries", 25))
    search = request.GET.get("search", "")
    status = request.GET.get("status", "")
    category = int(request.GET.get("category", 0))
    form = ProductProdactionCreateForm(request.POST or None)
    if request.POST:
        if form.is_valid():
            form.save()
            return redirect('dashboard:production-product-list')
        else:
            print("error form", form.errors)
    if status:
        products = ProductionProduct.objects.filter(status=status, amount__gt=0).order_by('-id')
    else:
        products = ProductionProduct.objects.filter(status__in=(2,3), amount__gt=0).order_by('-id')
    if category:
        products = products.filter(production_product__category_id=category).order_by('-id')
    categories = Categories.objects.all().order_by('id')
    paginator = Paginator(products, entries)
    products = paginator.page(page)
    currencies = Currency.objects.all().order_by('id')
    
    context = {
        "products": products,
        "entries_list": [5, 25, 50, 100, 250],
        "entries": entries,
        "status": status,
        "MEDIA_URL": settings.MEDIA_HOST,
        "role": request.user.role.slug,
        "price_change": request.GET.get('price_change', 'A'),
        "currencies": currencies,
        'categories_list': categories,
        'category':category,
        'form': form
    }
    if status in (2, '2'):
        return TemplateResponse(request, 'product/production_product_list_amount_0.html', context)
    return TemplateResponse(request, 'product/production_product_list.html', context)

@staff_member_required
@role_required(['seo', 'agent', 'zav-sklad', 'manufacturer'])
def prepack_product_list(request):
    if is_ajax(request=request):
        product_info = ProductionProductInfo.objects.filter(category_id=request.POST.get('category_id')).values()
        return JsonResponse({'products': list(product_info)})
    elif request.POST:
        products = request.POST.getlist('product')
        count = 1
        total_amount = 0
        for product in products:
            prodution_product = ProductionProduct.objects.filter(id=product).first()
            prodution_product.amount -=  int(request.POST.get(f'amount_{count}'))
            prodution_product.save()
            total_amount += (int(request.POST.get(f'amount_{count}')) * prodution_product.one_m)
            count += 1
        production_product= ProductionProduct.objects.filter(production_product_id=request.POST.get('production_product'), status=2).first()
        if production_product:
            production_product.amount += total_amount
            production_product.save()
        else:
            ProductionProduct.objects.create(
                production_product_id=request.POST.get('production_product'),
                amount = total_amount,
                status = 2
            )
        return redirect('dashboard:production-product-list')
    search = request.GET.get("search", "")
    products = ProductionProduct.objects.filter(status=1).order_by('-id')
    currencies = Currency.objects.all().order_by('id')
    context = {
        "products": products,
        "search": search,
        "MEDIA_URL": settings.MEDIA_HOST,
        "role": request.user.role.slug,
        "price_change": request.GET.get('price_change', 'A'),
        "currencies": currencies,
        'categories': Categories.objects.all(),
    }
    return TemplateResponse(request, 'product/prepack_product_list.html', context)


@staff_member_required
@role_required(['seo'])
def production_product_income_list(request):
    page = int(request.GET.get("page", 1))
    entries = int(request.GET.get("entries", 25))
    search = request.GET.get("search", "")
    products = services.get_production_products_income(request)
    paginator = Paginator(products, entries)
    # products = paginator.page(page)
    context = {
        "products": products['items'],
        "entries_list": [5, 25, 50, 100, 250],
        "entries": entries,
        "search": search,
        "MEDIA_URL": settings.MEDIA_HOST,
        "role": request.user.role.slug,
        "price_change": request.GET.get('price_change', 'A')
    }
    return TemplateResponse(request, 'product/production_product_income_list.html', context)


@staff_member_required
@role_required(['seo', 'manufacturer', 'zav-sklad'])
def production_product_info_list(request):
    page = int(request.GET.get("page", 1))
    entries = int(request.GET.get("entries", 25))
    search = request.GET.get("search", "")
    products = ProductionProductInfo.objects.all().order_by("-id")
    paginator = Paginator(products, entries)
    products = paginator.page(page)
    available_stock_products = Products.objects.all()
    workers = User.objects.filter(role_id=7)
    context = {
        "products": products,
        "entries_list": [5, 25, 50, 100, 250],
        "entries": entries,
        "search": search,
        "MEDIA_URL": settings.MEDIA_HOST,
        "form": ProductionProductForm(),
        "available_stock_products": available_stock_products,
        "workers": workers
    }
    return TemplateResponse(request, 'product/production_product_info_list.html', context)


@staff_member_required
@role_required(['seo', 'manufacturer', 'zav-sklad'])
def add_production_product(request):
    if request.method == 'POST':
        form = ProductionProductForm(request.POST)
        if request.POST:
            form_data = request.POST
            product_id = form_data['productId']
            formData = request.POST.get('formData')
            parsed_data = {}
            for key_value_pair in formData.split('&'):
                key, value = key_value_pair.split('=')
                parsed_data[key] = value

            amount = parsed_data.get('amount')
            amount_m = parsed_data.get('amount_m')
            worker = parsed_data.get('worker')
            new_pp = ProductionProduct.objects.create(
                amount=amount,
                amount_old=amount,
                amount_m = amount_m,
                one_m = int(amount_m) / int(amount),
                production_product=ProductionProductInfo.objects.filter(id=int(product_id)).first(),
                worker=User.objects.get(id=int(worker))
            )
            i = 1
            while parsed_data.get(f"stock_product_{i}", False):
                product = Products.objects.get(id=int(parsed_data.get(f'stock_product_{i}')))
                ProductionProductStockItem.objects.create(
                    production_product=new_pp,
                    stock_product=product,
                    amount=parsed_data.get(f'used_amount_{i}', 0) if parsed_data.get(f'used_amount_{i}', 0) else 0 ,
                    defect_amount=parsed_data.get(f'defect_amount_{i}', 0) if parsed_data.get(f'defect_amount_{i}', 0) else 0
                )
                if parsed_data.get(f'used_amount_{i}', 0):
                    QuantityChange.objects.create(
                        product=product,
                        user=request.user,
                        change_type='subtract',
                        type='amount',
                        quantity_changed=parsed_data.get(f'used_amount_{i}', 0)
                    )
                    product.amount -= int(parsed_data.get(f'used_amount_{i}', 0))
                if parsed_data.get(f'defect_amount_{i}', 0):
                    QuantityChange.objects.create(
                        product=product,
                        user=request.user,
                        change_type='subtract',
                        type='defect',
                        quantity_changed=parsed_data.get(f'defect_amount_{i}', 0)
                    )
                    product.defect -= int(parsed_data.get(f'defect_amount_{i}', 0))
                product.save()
                i += 1
            response_data = {'success': True, 'product_id': product_id}
            return JsonResponse(response_data)
        else:
            return JsonResponse({'success': False, 'errors': form.errors})
    else:
        form = ProductionProductForm()

    return TemplateResponse(request, 'product/add_production_product.html', {'form': form})


@staff_member_required
@role_required(['seo', 'zav-sklad', 'accountant'])
def add_price_product(request):
    if request.method == 'POST':
        product_id = request.POST.get('productId')
        production_id = request.POST.get('production_id')
        formData = request.POST.get('formData')
        parsed_data = {}
        for key_value_pair in formData.split('&'):
            key, value = key_value_pair.split('=')
            parsed_data[key] = value
        real_product = ProductionProductInfo.objects.filter(id=product_id).first()
        if real_product:
            real_product.price = {
                "A": parsed_data.get('price_a'),
                "percentage_A": parsed_data.get('percentage_a'),
                "B": parsed_data.get('price_b'),
                "percentage_B": parsed_data.get('percentage_b'),
                "C": parsed_data.get('price_c'),
                "percentage_C": parsed_data.get('percentage_c'),
            }
            real_product.currency = Currency.objects.get(id=int(parsed_data.get('currency')))
            real_product.save()
        production_product = ProductionProduct.objects.filter(id=production_id).first()
        production_product.status = 3
        production_product.cost = parsed_data.get('cost')
        production_product.save()
        return JsonResponse({'success': True, 'product_id': product_id})
    else:
        return JsonResponse({'success': False})


@staff_member_required
@role_required(['seo'])
def defect_list_history(request):
    page = int(request.GET.get("page", 1))
    entries = int(request.GET.get("entries", 25))
    search = request.GET.get("search", "")
    products = services.get_defect_products(request)
    paginator = Paginator(products, entries)
    # products = paginator.page(page)
    context = {
        "products": products['items'],
        "entries_list": [5, 25, 50, 100, 250],
        "entries": entries,
        "search": search,
        "MEDIA_URL": settings.MEDIA_HOST
    }
    return TemplateResponse(request, 'product/defect-list-history.html', context)


@staff_member_required
@role_required(['seo', 'manufacturer', 'zav-sklad'])
def production_product_info_create(request):
    product = None
    form = ProductInfoForm(request.POST or None)
    if request.POST:
        image = ""
        if request.FILES:
            path = default_storage.save(f"files/{request.FILES['file']}",
                                        ContentFile(request.FILES["file"].read()))
            image = f"/media/{path}"
        form = ProductInfoForm(request.POST or None, request.FILES or None, instance=ProductionProductInfo(
            images=[image],
            currency=Currency.objects.get(pk=1)
        ))
        if form.is_valid():
            data = form.save()
            return redirect(f"dashboard:production-product-info-list")
        else:
            print(form.errors)
    context = {
        'form': form,
        'product': product
    }
    return TemplateResponse(request, 'product/add_production_product.html', context)

@staff_member_required
@role_required(['seo', 'manufacturer', 'zav-sklad'])
def production_product_info_edit(request, pk):
    product = ProductionProductInfo.objects.filter(id=pk).first()
    form = ProductInfoForm(request.POST or None, request.FILES or None, instance=product)
    if request.POST:
        form = ProductInfoForm(request.POST or None, request.FILES or None, instance=product)
        if request.FILES:
            path = default_storage.save(f"files/{request.FILES['file']}",
                                        ContentFile(request.FILES["file"].read()))
            product.images = [f"/media/{path}"]
        if form.is_valid():
            data = form.save()
            return redirect(f"dashboard:production-product-info-list")
        else:
            print(form.errors)
    context = {
        'form': form,
        'product': product,
    }
    return TemplateResponse(request, 'product/add_production_product.html', context)


def production_product_accepted(request, pk):
    ProductionProduct.objects.filter(id=pk).update(
        accepted = 2
    )
    return JsonResponse({'success': True})

def production_product_cancel(request, pk):
    ProductionProduct.objects.filter(id=pk).update(
        accepted = 3
    )
    return JsonResponse({'success': True})