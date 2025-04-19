from django.shortcuts import render,redirect,get_object_or_404
from .models import Cart,CartItem,Coupon,GeneralCoupon
from store.models import Product,Variation
from django.core.exceptions import ObjectDoesNotExist
from django.http import JsonResponse
import json
from django.contrib.auth.decorators import login_required
from orders.models import Tax


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
                    cart_amount_detail=get_cart_details(request)
                    
                    total=cart_amount_detail.get('grand_total')
                    subtotal=cart_amount_detail.get('subtotal')
                    cgst_amount=cart_amount_detail.get('cgst_amount')
                    sgst_amount=cart_amount_detail.get('sgst_amount')

                    # print('Cart Item quantity increment')
                    # print('hi')
                    status='Success'
                    message='Item Quantity updated successfully!'
                    return JsonResponse({
                    'status':status,
                    'message':message,
                    'current_quantity':cart_item.quantity,
                    'total':total,
                    'subtotal':subtotal,
                    'cgst_amount':cgst_amount,
                    'sgst_amount':sgst_amount,
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
                    cart_amount_detail=get_cart_details(request)
                    
                    total=cart_amount_detail.get('grand_total')
                    subtotal=cart_amount_detail.get('subtotal')
                    cgst_amount=cart_amount_detail.get('cgst_amount')
                    sgst_amount=cart_amount_detail.get('sgst_amount')
                    status='Success'
                    message='Item Quantity updated successfully!'
                    return JsonResponse({
                    'status':status,
                    'message':message,
                    'current_quantity':cart_item.quantity,
                    'total':total,
                    'subtotal':subtotal,
                    'cgst_amount':cgst_amount,
                    'sgst_amount':sgst_amount,
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
                    cart_amount_detail=get_cart_details(request)
                    
                    total=cart_amount_detail.get('grand_total')
                    subtotal=cart_amount_detail.get('subtotal')
                    cgst_amount=cart_amount_detail.get('cgst_amount')
                    sgst_amount=cart_amount_detail.get('sgst_amount')
                    status='Success'
                    message='Item deleted successfully!'
                    return JsonResponse({
                    'status':status,
                    'message':message,
                    'current_quantity':0,
                    'remove_quantity':cart_item.quantity,
                    'total':total,
                    'subtotal':subtotal,
                    'cgst_amount':cgst_amount,
                    'sgst_amount':sgst_amount,
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
def checkout(request):
    cart_items=None
    try:
        cart=Cart.objects.get(cart_id=_cart_id(request))
        cart_items=CartItem.objects.filter(cart=cart,is_active=True)
    except ObjectDoesNotExist:
        pass
    # print(cart_items)
    context={
        'cart_items':cart_items,
    }
    return render(request,'store/checkout.html',context)


def get_cart_details(request):
    grand_total,subtotal,total_tax_amount=0,0,0
    # tax_dict={}
    cgst_amount,sgst_amount=0,0
    try:
        cart=Cart.objects.get(cart_id=_cart_id(request))
        # print('cart_found')
        cart_items=CartItem.objects.filter(cart=cart)
        # print('cart_items found')
        taxes=Tax.objects.all()
        for item in cart_items:
            subtotal+=(item.product.price*item.quantity)

        for tax in taxes:
            percent=tax.tax_percent
            tax_type=tax.tax_type
            # print(percent,tax_type)
            # print("subtotal:", subtotal, type(subtotal))
            # print("percent:", percent, type(percent))
            tax_amount = round((float(subtotal) * (percent / 100.00)), 2)
            # print(tax_amount,type(tax_amount))
            total_tax_amount+=tax_amount
            # print(tax_amount)
            if tax_type=='CGST':
                cgst_amount=tax_amount
            if tax_type=='SGST':
                sgst_amount=tax_amount
    except:
        pass    
    # print(tax_dict)
    grand_total=float(subtotal)+total_tax_amount
    grand_total=round(grand_total,2)
    context={'grand_total':grand_total,'subtotal':subtotal,'cgst_amount':cgst_amount,'sgst_amount':sgst_amount}
    # print(context)
    return context

def get_coupon(request,coupon_code):
    try:
        coupon=GeneralCoupon.objects.get(code=coupon_code,is_active=True)
        return coupon
    except:
        print('General Coupon does not exist will check for user specific coupon')
        try:
            coupon=Coupon.objects.get(code=coupon_code,user=request.user,used=False)
            return coupon
        except:
            print('No coupons found')
        return None