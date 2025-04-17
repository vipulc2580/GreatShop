from django.shortcuts import render,get_object_or_404,redirect
from django.http import HttpResponse,JsonResponse
from .models import Product,Variation,ReviewRating,ProductGallery
from .forms import ReviewForm
from category.models import Category
from cart.models import CartItem,Cart
from cart.views import _cart_id
from django.core.paginator import EmptyPage,PageNotAnInteger,Paginator
from django.db.models import Q
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from orders.models import OrderProduct
from cart.context_processors import cart_amount_details
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
    reviews=None
    has_purchased=False
    product_gallery=None
    try:
        product=Product.objects.get(category__category_slug=category_slug,slug=product_slug)
        color_variations = Variation.variations.colors().filter(product=product)
        size_variations = Variation.variations.size().filter(product=product)
        reviews=ReviewRating.objects.filter(product__id=product.id,status=True).order_by('-updated_at')
        is_in_cart=CartItem.objects.filter(cart__cart_id=_cart_id(request),product=product).exists()
        product_gallery=ProductGallery.objects.filter(product=product)
        # print(product_gallery)
        # print(color_variations)
        # for color in color_variations:
        #     print(color)
        # print(size_variations)
        # print(is_in_cart)
    except Exception as e:
        raise e
    # print(product,request.user)
    if request.user.is_authenticated:
        try:
            has_purchased=OrderProduct.objects.filter(product=product,user=request.user,ordered=True).exists()

        except Exception as e:
            pass 
    context={
            'product':product,
            'is_in_cart':is_in_cart,
            'color_variation':color_variations,
            'size_variation':size_variations,
            'reviews':reviews,
            'has_purchased':has_purchased,
            'product_gallery':product_gallery,
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

@login_required(login_url='login')
def submit_review(request,product_id):
    url=request.META.get('HTTP_REFERER')
    # print(url)
    if request.method=='POST':
        try:
            review=ReviewRating.objects.get(user__id=request.user.id,product__id=product_id)
            form=ReviewForm(request.POST,instance=review)
            form.save() 
            messages.success(request,'Thank you! Your review has been updated!')
            return redirect(url)
        except ReviewRating.DoesNotExist:
            form=ReviewForm(request.POST)
            if form.is_valid():
                data=ReviewRating()
                data.subject=form.cleaned_data['subject']
                data.review=form.cleaned_data['review']
                data.rating=form.cleaned_data['rating']
                data.ip=request.META.get('REMOTE_ADDR')
                data.user_id=request.user.id 
                data.product_id=product_id 
                data.save()
                messages.success(request,'Thank you! Your review has been submitted!')
                return redirect(url)
            else:
                return redirect(url)
    return redirect('store')
            

