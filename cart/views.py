from django.shortcuts import render,redirect,get_object_or_404
from .models import Cart,CartItem
from store.models import Product,Variation
from django.core.exceptions import ObjectDoesNotExist
from django.http import JsonResponse
import json
from django.contrib.auth.decorators import login_required
# Create your views here.
def _cart_id(request):
    cart=None
    if request.user is not None or user.is_authenticated:
        try:
            # print(request.user)
            cart=Cart.objects.get(user=request.user)
            # print(f'found user related cart ${cart.cart_id}')
            return cart.cart_id
        except:
            cart=request.session.session_key
        # print(cart)
        if not cart:
            cart=request.session.create()
        return cart 
    else:
        cart=request.session.session_key
        # print(cart)
        if not cart:
            cart=request.session.create()
        return cart 

def add_cart(request,product_id):
    product=get_object_or_404(Product,id=product_id)
    product_variations=[]
    if request.method=='POST':
        for item in request.POST:
            if(item=='csrfmiddlewaretoken'): continue
            key=item
            value=request.POST.get(key)
            print(key,value)
            try:
                variation=Variation.objects.get(product=product,variation_category__iexact=key,variation_value__iexact=value)
                # print(variation)
                product_variations.append(variation)
            except Exception as e:
                pass
    cart=None
    if request.user.is_authenticated:
        try:
            cart=Cart.objects.get(cart_id=_cart_id(request)) # get cart using cart id present in the session or user based cart 
        except Cart.DoesNotExist:
            cart=Cart.objects.create(cart_id=_cart_id(request),user=request.user)
        cart.save()
        cart_items=CartItem.objects.filter(cart=cart,product=product)
        if cart_items:
            print('Cart items found')
            existing_variation_sets = []
            ids = []

            for item in cart_items:
                variation_list = set(item.variations.all())
                existing_variation_sets.append(variation_list)  # compare as sets
                ids.append(item.id)

            current_variation_set = set(product_variations)
            # print(current_variation_set)
            if current_variation_set in existing_variation_sets:
                # print('found item')
                index = existing_variation_sets.index(current_variation_set)
                item_id = ids[index]
                cart_item = CartItem.objects.get(id=item_id)
                cart_item.quantity += 1
                cart_item.save()
            else:
                cart_item=CartItem.objects.create(cart=cart,product=product,quantity=1,user=request.user)
                cart_item.variations.add(*product_variations)
                cart_item.save()
        else:
            cart_item=CartItem.objects.create(cart=cart,product=product,quantity=1,user=request.user)
            cart_item.variations.add(*product_variations)
            cart_item.save()
        return redirect('cart')
    else:
        try:
            cart=Cart.objects.get(cart_id=_cart_id(request)) # get cart using cart id present in the session 
        except Cart.DoesNotExist:
            cart=Cart.objects.create(cart_id=_cart_id(request))
        cart.save()
        cart_items=CartItem.objects.filter(cart=cart,product=product)
        if cart_items:
            print('Cart items found')
            existing_variation_sets = []
            ids = []

            for item in cart_items:
                variation_list = set(item.variations.all())
                existing_variation_sets.append(variation_list)  # compare as sets
                ids.append(item.id)

            current_variation_set = set(product_variations)
            print(current_variation_set)
            if current_variation_set in existing_variation_sets:
                print('found item')
                index = existing_variation_sets.index(current_variation_set)
                item_id = ids[index]
                cart_item = CartItem.objects.get(id=item_id)
                cart_item.quantity += 1
                cart_item.save()
            else:
                cart_item=CartItem.objects.create(cart=cart,product=product,quantity=1)
                cart_item.variations.add(*product_variations)
                cart_item.save()
        else:
            cart_item=CartItem.objects.create(cart=cart,product=product,quantity=1)
            cart_item.variations.add(*product_variations)
            cart_item.save()
        return redirect('cart')


def subtract_cart(request,product_id):
    product=get_object_or_404(Product,id=product_id)
    cart=None
    try:
        cart=Cart.objects.get(cart_id=_cart_id(request)) # get cart using cart id present in the session 
    except Cart.DoesNotExist:
        cart=Cart.objects.create(cart_id=_cart_id(request))
    cart.save()
    cart_item=None
    try:
        cart_item=CartItem.objects.get(product=product,cart=cart)
    except CartItem.DoesNotExist:
        cart_item=CartItem.objects.create(
            product=product,
            cart=cart,
            quantity=0)
    if(cart_item.quantity>1):
        cart_item.quantity-=1
        cart_item.save()
    else:
        cart_item.delete()
    # print(f'Cart item current quantity is {cart_item.quantity}')
    return redirect('cart')




def cart(request,quantity=0,total=0,cart_items=None):
    try:
        cart=Cart.objects.get(cart_id=_cart_id(request))
        cart_items=CartItem.objects.filter(cart=cart,is_active=True)
    except ObjectDoesNotExist:
        pass
    # print(cart_items)
    context={
        'cart_items':cart_items,
        'quantity':quantity,
    }
    return render(request,'store/cart.html',context)


def increment_cart_item(request):
    if request.method=='POST':
          if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            try:
                data=json.loads(request.body)
                item_id=data.get('item_id')
                status='Failed'
                message='Error Occured'
                try:
                    cart_item=CartItem.objects.get(id=item_id)
                    cart_item.quantity+=1
                    cart_item.save()
                    # print('Cart Item quantity increment')
                    status='Success'
                    message='Item Quantity updated successfully!'
                    return JsonResponse({
                    'status':status,
                    'message':message,
                    'current_quantity':cart_item.quantity
                })
                except Exception as e:
                    pass
                return JsonResponse({
                    'status':status,
                    'message':message,
                })
            except Exception as e:
                return JsonResponse({
                  'status':'Failed',
                    'message':'Bad request'
                })
    else:
        return JsonResponse({
            'status':'Failed',
            'message':'Bad request'
        })


def decrement_cart_item(request):
    if request.method=='POST':
          if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            try:
                data=json.loads(request.body)
                item_id=data.get('item_id')
                # print(item_id)
                status='Failed'
                message='Error Occured'
                try:
                    cart_item=CartItem.objects.get(id=item_id)
                    cart_item.quantity-=1
                    if(cart_item.quantity==0): return remove_cart_item(request)
                    cart_item.save()
                    status='Success'
                    message='Item Quantity updated successfully!'
                    return JsonResponse({
                    'status':status,
                    'message':message,
                    'current_quantity':cart_item.quantity
                })
                except Exception as e:
                    pass
                return JsonResponse({
                    'status':status,
                    'message':message,
                })
            except Exception as e:
                return JsonResponse({
                  'status':'Failed',
                    'message':'Bad request'
                })
    else:
        return JsonResponse({
            'status':'Failed',
            'message':'Bad request'
        })

def remove_cart_item(request):
    if request.method=='POST':
          if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            try:
                data=json.loads(request.body)
                item_id=data.get('item_id')
                # print(item_id)
                status='Failed'
                message='Error Occured'
                try:
                    cart_item=CartItem.objects.get(id=item_id)
                    # cart_item.quantity=0
                    cart_item.delete()
                    status='Success'
                    message='Item deleted successfully!'
                    return JsonResponse({
                    'status':status,
                    'message':message,
                    'current_quantity':0,
                    'remove_quantity':cart_item.quantity
                })
                except Exception as e:
                    pass
                return JsonResponse({
                    'status':status,
                    'message':message,
                })
            except Exception as e:
                return JsonResponse({
                  'status':'Failed',
                    'message':'Bad request'
                })
    else:
        return JsonResponse({
            'status':'Failed',
            'message':'Bad request'
        })


@login_required(login_url='login')
def checkout(request,quantity=0,total=0,cart_items=None):
    if request.method=='POST':
        print(request.POST)
    tax,grand_total=0,0
    try:
        cart=Cart.objects.get(cart_id=_cart_id(request))
        cart_items=CartItem.objects.filter(cart=cart,is_active=True)
        for cart_item in cart_items:
            total+=(cart_item.quantity*cart_item.product.price)
            quantity+=(cart_item.quantity)
        tax=(total*2)/100
        grand_total=tax+total
    except ObjectDoesNotExist:
        pass
    # print(cart_items)
    context={
        'cart_items':cart_items,
        'total':total,
        'quantity':quantity,
        'grand_total':grand_total,
        'tax':tax
    }
    return render(request,'store/checkout.html',context)