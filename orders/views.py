from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from cart.models import CartItem
from .forms import OrderForm
from .models import Order, Payment, OrderProduct
from cart.context_processors import cart_amount_details
import datetime
import paypalrestsdk
import requests
from store.models import Product
from django.contrib import messages
from accounts.utils import send_notification_email
from django.contrib.sites.shortcuts import get_current_site
import json
from cart.models import Coupon
from cart.views import get_coupon


PAYPAL_CLIENT_ID = settings.PAYPAL_CLIENT_ID
PAYPAL_SECRET = settings.PAYPAL_SECRET_KEY
PAYPAL_API_URL = "https://api-m.sandbox.paypal.com"

# Create your views here.


@login_required(login_url='login')
def place_order(request):
    current_user = request.user
    # if cart count is < 0 redirect to store
    cart_items = CartItem.objects.filter(user=current_user)
    cart_count = cart_items.count()
    if cart_count <= 0:
        messages.info(request, 'Please Add Items to Cart')
        return redirect('store')
    cart_amount_detail = cart_amount_details(request)
    grand_total = cart_amount_detail.get('grand_total')
    tax_dict = cart_amount_detail.get('tax_dict')
    tax_amount = sum([float(val) for item, value in tax_dict.items()
                     for key, val in value.items()])
    if request.method == 'POST':
        # print('got podst request')
        form = OrderForm(request.POST)
        # print(form)
        if form.is_valid():
            # store all the billing info inside order table
            # print('form is valid')
            coupon_code = form.cleaned_data.get('coupon_code')
            # print(coupon_code)
            coupon = get_coupon(request,coupon_code)

            data = Order()
            data.user = current_user
            data.first_name = form.cleaned_data['first_name']
            data.last_name = form.cleaned_data['last_name']
            data.email = form.cleaned_data['email']
            data.phone_number = form.cleaned_data['phone_number']
            data.address_line_1 = form.cleaned_data['address_line_1']
            data.address_line_2 = form.cleaned_data['address_line_2']
            data.country = form.cleaned_data['country']
            data.city = form.cleaned_data['city']
            data.pincode = form.cleaned_data['pincode']
            data.state = form.cleaned_data['state']
            data.order_note = form.cleaned_data['order_note']
            data.order_total = grand_total
            data.net_total = grand_total
            data.tax = tax_amount
            data.tax_data = json.dumps(tax_dict)
            data.ip = request.META.get('REMOTE_ADDR')
            if coupon:
                
                if isinstance(coupon,Coupon):
                    data.coupon=coupon
                else:
                    data.general_coupon=coupon
                # print('coupon found')
                data.discount_amount = coupon.get_discount_amount(grand_total)
                # print('discount_Amount applied')
                data.net_total = round(
                    data.order_total - data.discount_amount, 2)
                # print('discount saved')
            
            data.save()
            # generating the order ID
            yr = int(datetime.date.today().strftime('%Y'))
            dt = int(datetime.date.today().strftime('%d'))
            mt = int(datetime.date.today().strftime('%m'))
            d = datetime.date(yr, mt, dt)
            current_date = d.strftime("%Y%m%d")  # 20210305
            order_number = current_date + str(data.id)
            data.order_number = order_number
            data.save()
            order = Order.objects.get(
                user=current_user,
                is_ordered=False,
                order_number=order_number)
            context = {
                'order': order,
                'cart_items': cart_items,
            }
            return render(request, 'orders/collect_payment.html', context)
    return redirect('checkout')


def payments(request, status, transaction_id, payment_method, order_number):
    # print('request received to ')
    current_user = request.user
    order = Order.objects.get(
        order_number=order_number,
        user=current_user,
        is_ordered=False)
    payment = Payment(
        user=current_user,
        payment_id=transaction_id,
        payment_method=payment_method,
        amount_paid=order.order_total,
        status=status,
    )
    payment.save()

    # assign payment and is_ordered status
    order.payment = payment
    order.is_ordered = True
    order.save()

    # is coupon is applied we need set the coupon to used
    if isinstance(order.coupon,Coupon):
        coupon_id = order.coupon.id
        coupon = Coupon.objects.get(pk=coupon_id)
        coupon.used = True
        coupon.save()
        # print(f'This coupon {coupon} is used by {request.user}')

    cart_amount_detail = cart_amount_details(request)
    customer_subtotal = cart_amount_detail.get('subtotal')
    customer_tax_data = cart_amount_detail.get('tax_dict')
    # move products from cartitems of user to OrderProduct
    cart_items = CartItem.objects.filter(user=current_user)

    for item in cart_items:
        order_product = OrderProduct()
        order_product.order = order
        order_product.payment = payment
        order_product.user = current_user
        order_product.product = item.product
        order_product.quantity = item.quantity
        order_product.product_price = item.product.price
        order_product.ordered = True
        order_product.save()
        product_variations = item.variations.all()
        order_product.variations.set(product_variations)
        order_product.save()

        # reduce the Quantity of sold Products

        product_id = item.product.id
        product = Product.objects.get(id=product_id)
        product.stock -= item.quantity
        product.save()

    # clear the cart
    cart_items.delete()

    # send order recieved email to customer
    mail_subject = 'Thank you for ordering with us!'
    htmlfile = 'order_confirmation_email.html'
    ordered_products = OrderProduct.objects.filter(
        user=current_user, payment=payment, order=order)
    # print(customer_tax_data)
    current_site = get_current_site(request)
    # print(current_site.domain)
    context = {
        'user': current_user,
        'order': order,
        'ordered_products': ordered_products,
        'customer_subtotal': customer_subtotal,
        'customer_tax_data': customer_tax_data,
        'domain': current_site.domain
    }
    send_notification_email(
        request,
        current_user,
        mail_subject,
        htmlfile,
        context)

    response = {
        'status': 200,
        'order_number': order.order_number,
        'transaction_id': order.payment.payment_id,
        'message': 'Payment Done',
    }
    return JsonResponse(response)
    # return render(request,'orders/collect_payment.html')


@csrf_exempt
def create_order(request):
    data = json.loads(request.body)
    order_number = data.get('orderNumber')
    grand_total = cart_amount_details(request)['grand_total']
    try:
        order = Order.objects.get(
            order_number=order_number,
            user=request.user,
            is_ordered=False)
    except (Order.DoesNotExist, Exception):
        print('Invalid Order Number')
        pass
    else:
        grand_total = order.net_total

    auth = (PAYPAL_CLIENT_ID, PAYPAL_SECRET)
    # print('request recived for order creation')
    headers = {"Content-Type": "application/json"}

    order_data = {
        "intent": "CAPTURE",
        "purchase_units": [{
            "amount": {
                "currency_code": "USD",
                "value": str(grand_total),
            }
        }]
    }

    response = requests.post(
        f"{PAYPAL_API_URL}/v2/checkout/orders",
        json=order_data,
        auth=auth,
        headers=headers
    )

    if response.status_code == 201:
        return JsonResponse(response.json())  # Return the valid order ID
    else:
        return JsonResponse(response.json(), status=400)


@csrf_exempt
def capture_order(request, order_id, order_number):
    """Captures an approved PayPal order"""

    auth = (PAYPAL_CLIENT_ID, PAYPAL_SECRET)
    headers = {"Content-Type": "application/json"}

    capture_url = f"{PAYPAL_API_URL}/v2/checkout/orders/{order_id}/capture"

    response = requests.post(capture_url, auth=auth, headers=headers)

    if response.status_code == 201 or response.status_code == 200:

        response_obj = response.json()  # No need to use json.load()
        transaction = response_obj['purchase_units'][0]['payments']['captures'][0]
        # print(transaction)
        transaction_id = transaction['id']
        status = transaction['status']
        payment_method = 'PayPal'
        # print(transaction_id,status,payment_method,order_number)
        # make payment entry in database
        return payments(
            request,
            status,
            transaction_id,
            payment_method,
            order_number)

    return JsonResponse(response.json())  # Handle errors


def order_complete(request):
    # print(request)
    order_number = request.GET.get('order_no')
    transaction_id = request.GET.get('trans_id')
    try:
        order = Order.objects.get(
            order_number=order_number,
            payment__payment_id=transaction_id,
            is_ordered=True)
        # print('found order')
        ordered_products = OrderProduct.objects.filter(
            order=order, payment__payment_id=transaction_id)
        # print('found ordered Product')
        subtotal = 0
        for product in ordered_products:
            subtotal += (product.quantity * product.product_price)
        tax_dict = json.loads(order.tax_data)
        context = {
            'order': order,
            'ordered_products': ordered_products,
            'subtotal': subtotal,
            'tax_data': tax_dict,
        }
        return render(request, 'orders/order_complete.html', context)
    except Exception as e:
        return redirect('home')


def apply_coupon(request):
    if request.method == 'POST':
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            # print('successful request')
            data = json.loads(request.body)
            coupon_code = data.get('coupon')
            # total_amount=data.get('total_amount')
            cart_amount_detail = cart_amount_details(request)

            # print(coupon_code)
            coupon =get_coupon(request,coupon_code)
            if not coupon:
                return JsonResponse({'status':'Failed','message':'Invalid Coupon code!'})
            else:
                if coupon.is_valid():
                    discount_amount = coupon.get_discount_amount(
                        cart_amount_detail.get('grand_total'))
                    # print(discount_amount)
                    return JsonResponse({'status': 'Success',
                                         'message': 'Coupon Applied!',
                                         'discount_amount': discount_amount})
                else:
                    return JsonResponse(
                        {'status': 'Failed', 'message': 'Invalid Coupon Code!'})
    else:
        # print('Invalid request')
        return JsonResponse(
            {'status': 'Failed', 'message': 'Invalid Response'})
