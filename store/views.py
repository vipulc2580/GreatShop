from django.shortcuts import render,get_object_or_404
from django.http import HttpResponse
from store.models import Product
from category.models import Category
# Create your views here.

def store(request,category_slug=None):
    categories=None
    products=None
    if category_slug!=None:
        categories=get_object_or_404(Category,category_slug=category_slug)
        products=Product.objects.filter(is_available=True,category=categories)
        product_count=products.count()
    else:
        products=Product.objects.filter(is_available=True)
        product_count=products.count()
    context={
        'products':products,
        'product_count':product_count,
    }
    return render(request,'store/unistore.html',context)

def product_detail(request,category_slug,product_slug):
    product=None
    try:
        product=Product.objects.get(category__category_slug=category_slug,slug=product_slug)
    except Exception as e:
        raise e
    context={
            'product':product,
        }
    return render(request,'store/new_product_detail.html',context)