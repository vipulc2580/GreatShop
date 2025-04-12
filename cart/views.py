from django.shortcuts import render,redirect,get_object_or_404
from .models import Cart,CartItem
from store.models import Product,Variation
from django.core.exceptions import ObjectDoesNotExist
from django.http import JsonResponse
import json
# Create your views here.
def _cart_id(request):
    cart=request.session.session_key
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
    try:
        cart=Cart.objects.get(cart_id=_cart_id(request)) # get cart using cart id present in the session 
    except Cart.DoesNotExist:
        cart=Cart.objects.create(cart_id=_cart_id(request))
    cart.save()
    cart_items=CartItem.objects.filter(cart=cart,product=product)
    if cart_items:
        existing_variations=[]
        ids=[]
        for item in cart_items:
            existing_variations.append(list(item.variations.all()))
            ids.append(item.id)
        if product_variations in existing_variations:
            index=existing_variations.index(product_variations)
            item_id=ids[index]
            cart_item=CartItem.objects.get(id=item_id)
            cart_item.quantity+=1
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
                print(item_id)
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