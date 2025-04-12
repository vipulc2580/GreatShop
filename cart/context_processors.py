from .models import CartItem,Cart
from .views import _cart_id
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
        