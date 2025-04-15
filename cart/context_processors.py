from .models import CartItem,Cart
from .views import _cart_id
from orders.models import Tax

def cart_counter(request):
    if 'admin' in request.path:
        return {}
    else:
        quantity=0
        try:
            cart=Cart.objects.get(cart_id=_cart_id(request))
            cart_items=CartItem.objects.filter(cart=cart)
            for item in cart_items:
                quantity+=(item.quantity)
        except Cart.DoesNotExist:
            pass 
        return {'cart_count':quantity}
        

def cart_amount_details(request):
    if 'admin' in request.path:
        return {}
    else:
        grand_total,subtotal,total_tax_amount=0,0,0
        tax_dict={}
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
                tax_dict.update({str(tax.tax_type):{str(percent):str(tax_amount)}})
        except:
            pass    
        # print(tax_dict)
        grand_total=float(subtotal)+total_tax_amount
        grand_total=round(grand_total,2)
        context={'grand_total':grand_total,'subtotal':subtotal,'tax_dict':tax_dict}
        # print(context)
        return context
