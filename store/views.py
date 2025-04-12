from django.shortcuts import render,get_object_or_404,redirect
from django.http import HttpResponse
from store.models import Product,Variation
from category.models import Category
from cart.models import CartItem,Cart
from cart.views import _cart_id
from django.core.paginator import EmptyPage,PageNotAnInteger,Paginator
from django.db.models import Q
# Create your views here.

def store(request,category_slug=None):
    categories=None
    products=None
    if category_slug!=None:
        categories=get_object_or_404(Category,category_slug=category_slug)
        products=Product.objects.filter(is_available=True,category=categories).order_by('id')
        product_count=products.count()
        paginator=Paginator(products,2)
        page=request.GET.get('page')
        paged_products=paginator.get_page(page)
    else:
        products=Product.objects.filter(is_available=True).order_by('id')
        paginator=Paginator(products,6)
        page=request.GET.get('page')
        paged_products=paginator.get_page(page)
        product_count=products.count()
    context={
        'products':paged_products,
        'product_count':product_count,
    }
    return render(request,'store/unistore.html',context)

def product_detail(request,category_slug,product_slug):
    product=None
    is_in_cart=False
    size_variations=None
    color_variations=None
    try:
        product=Product.objects.get(category__category_slug=category_slug,slug=product_slug)
        is_in_cart=CartItem.objects.filter(cart__cart_id=_cart_id(request),product=product).exists()
        color_variations = Variation.variations.colors().filter(product=product)
        size_variations = Variation.variations.size().filter(product=product)
        # print(color_variations)
        # for color in color_variations:
        #     print(color)
        # print(size_variations)
        # print(is_in_cart)
    except Exception as e:
        raise e
    context={
            'product':product,
            'is_in_cart':is_in_cart,
            'color_variation':color_variations,
            'size_variation':size_variations,
            }
    return render(request,'store/new_product_detail.html',context)

def search(request):
    keyword=request.GET.get('keyword')
    page=request.GET.get('page')
    if not keyword and not page:
        return redirect('store')
    else:
        products=Product.objects.filter(
                Q(description__icontains=keyword) |
                Q(product_name__icontains=keyword)
            ).distinct()
        product_count=products.count()
        paginator=Paginator(products,2)
        page=request.GET.get('page')
        paged_products=paginator.get_page(page)
        context={
            'products':paged_products,
            'product_count':product_count,
            'keyword':keyword
        }
        return render(request,'store/unistore.html',context)