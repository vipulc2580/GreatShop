from django.shortcuts import render,redirect,get_object_or_404
from django.http import HttpResponse
from .forms import RegistrationForm,LoginForm,ForgotPasswordForm,ResetPasswordForm,UserForm,UserProfileForm,ChangePasswordForm
from .models import User,UserProfile
from django.contrib import messages
from django.contrib.auth import authenticate,login,logout
from django.contrib.auth.decorators import login_required
from .utils import send_notification_email
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_decode
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.contrib.sites.shortcuts import get_current_site
import uuid
import json
from cart.views import _cart_id
from cart.models import Cart,CartItem
from orders.models import Order,OrderProduct
import requests
# Create your views here.
def register(request):
    form=RegistrationForm()
    if request.method=='POST':
        form=RegistrationForm(request.POST)
        if form.is_valid():
        # print('data is valid')
            first_name=form.cleaned_data['first_name']
            last_name=form.cleaned_data['last_name']
            phone_number=form.cleaned_data['phone_number']
            email=form.cleaned_data['email']
            password=form.cleaned_data['password1']
            username=email.split('@')[0]
            user=User.objects.create_user(first_name=first_name,last_name=last_name,email=email,username=username,password=password)
            user.phone_number=phone_number
            user.save()
            # messages.success(request, 'User registered and Verfication Email has been sent!')
            # send a verification email 
            current_site = get_current_site(request)
            mail_subject='Please activate your account!'
            htmlfile='account_verification.html'
            context={
            'user': user,
            'domain': current_site.domain,
            'uid': urlsafe_base64_encode(force_bytes(user.pk)),  
            'token': default_token_generator.make_token(user),
            }
            send_notification_email(request=request,user=user,mail_subject=mail_subject,htmlfile=htmlfile,context=context)
            return redirect(f'/accounts/login/?command=verification&email={email}')
    context={
    'form':form,
    }
    return render(request,'accounts/register.html',context)

def login_view(request):
    form=LoginForm()
    if request.method=='POST':
        form=LoginForm(request.POST)
        if form.is_valid():
            email=form.cleaned_data['email']
            password=form.cleaned_data['password']
            user=authenticate(request,email=email,password=password)
            if user is not None:
                try:
                    # print('Enter try block')
                    # print(_cart_id(request))
                    cart=Cart.objects.get(cart_id=_cart_id(request))
                    # if user based cart is already present then session cart mein ko delete karo 
                    user_cart = Cart.objects.filter(user=user).first()
                    if user_cart:
                        # print('found user cart')
                        cart_items=CartItem.objects.filter(cart=cart)
                        # find which cart item can be grouped
                        user_cart_items=CartItem.objects.filter(cart=user_cart)
                        # print(f'User cart item {user_cart_items}')
                        # print(f'session cart item {cart_items}')
                        existing_variation_sets = []
                        ids = []
                        for item in user_cart_items:
                            variation_list = set(item.variations.all())
                            existing_variation_sets.append(variation_list)  # compare as sets
                            ids.append(item.id)
                        # print(existing_variation_sets)
                        # print(user_cart_items,cart_items)
                        not_included_ids=[]
                        item_deletes=[]
                        for item in cart_items:
                            current_variation=set(item.variations.all())
                            # print(current_variation)
                            if current_variation in existing_variation_sets:
                                # print('variation is present')
                                idx=existing_variation_sets.index(current_variation)
                                # print(idx)
                                item_qty_update=CartItem.objects.get(id=ids[idx])
                                # print(item_qty_update.quantity)
                                item_qty_update.quantity+=item.quantity
                                item_qty_update.save()
                                # print(item_qty_update.quantity)
                                item_deletes.append(item.id)
                            else:
                                not_included_ids.append(item.id)
                        # print(item_deletes,not_included_ids)
                        for item_id in item_deletes:
                            item=CartItem.objects.get(id=item_id)
                            item.delete()
                        for item_id in not_included_ids:
                            item=CartItem.objects.get(id=item_id)
                            item.user=user
                            item.cart=user_cart
                            item.save()

                        # cart.delete()
                    # print('Cart found')
                    else:
                        cart.user=user
                        cart.save()
                    # print('user assigned')
                        cart_items=CartItem.objects.filter(cart=cart)
                        # print(cart_items)
                        if cart_items:
                            for item in cart_items:
                                item.user=user
                                item.save()
                            # print('User ASsigned to Cart Items')
                except Exception as e:
                    pass
                    # print('entered except block')
                login(request,user)
                messages.success(request,'Logged In Successfully!')
                url=request.META.get('HTTP_REFERER')
                try:
                    query=requests.utils.urlparse(url).query
                    params=dict(x.split('=') for x in query.split('&'))
                    print(params)
                    if 'next' in params:
                        nextPage=params.get('next')
                        return redirect(nextPage)
                except:
                    return redirect('home')
            else:
                form.add_error(None,'Invalid Credentails')
    context={
        'form':form
    }
    return render(request,'accounts/login.html',context)

@login_required(login_url='login')
def logout_view(request):
    # return HttpResponse('<h2>You will be logout</h2>')
    logout(request)
    messages.error(request,'Logged Out Successfully!')
    return redirect('home')


def forgot_password(request):
    form=ForgotPasswordForm()
    if request.method=='POST':
        form=ForgotPasswordForm(request.POST)
        if form.is_valid():
            email=form.cleaned_data['email']
            print(email)
            try:
                user=User.objects.get(email__exact=email)
                mail_subject='Please Reset your password!'
                htmlfile='reset_password_link.html'
                current_site = get_current_site(request)
                context={
                'user': user,
                'domain': current_site.domain,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),  
                'token': default_token_generator.make_token(user),
                }
                send_notification_email(request=request,user=user,mail_subject=mail_subject,htmlfile=htmlfile,context=context)
                messages.success(request,'Password Reset Email has been sent!')
                return redirect('login')
            except User.DoesNotExist:
                form.add_error(None,'Invalid Email Address!')
    context={
        'form':form
    }
    return render(request,'accounts/forgot_password.html',context)


def activate_account(request,uidb64,token):
    try:
        uid=urlsafe_base64_decode(uidb64).decode()
        user=User._default_manager.get(pk=uid)
    except (TypeError,OverflowError,ValueError,User.DoesNotExist):
        user=None
    if user is not None and default_token_generator.check_token(user,token):
        user.is_active=True
        user.save()
        messages.success(request,'Congratulations,Your account has been verified!')
        return redirect('login')
    else:
        messages.error(request,'Invalid Verfication Link')    
    return redirect('home')


def validate_reset_password(request,uidb64,token):
    try:
        uid=urlsafe_base64_decode(uidb64).decode()
        user=User._default_manager.get(pk=uid)
    except:
        user=None
    if user is not None and default_token_generator.check_token(user,token):
        session_token = str(uuid.uuid4())
        request.session['reset_user_id'] = user.id
        request.session['reset_session_token'] = session_token
        messages.success(request,'Please reset your password')
        return redirect(f'/accounts/reset-password/{session_token}/')
    else:
        messages.error(request,'Invalid Password Reset Link')
    return redirect('login')

def reset_password(request,stored_token):
    user_id=request.session.get('reset_user_id')
    session_token = request.session.get('reset_session_token')
    user=None
    if not user_id or not session_token or stored_token!=session_token:
        messages.error(request,'Invalid Password Reset Link')
        return redirect('login')
    try:
        user=User.objects.get(pk=user_id)
    except User.DoesNotExist:
        messages.error(request,'Invalid Password Reset Link')
        return redirect('login')
    form=ResetPasswordForm()
    if request.method=='POST':
        form=ResetPasswordForm(request.POST)
        if form.is_valid():
            del request.session['reset_user_id']
            del request.session['reset_session_token']
            password=form.cleaned_data['password']
            user.set_password(password)
            user.save()
            messages.success(request,'Password changed successfully!')
            return redirect('login')

    context={
        'form':form,
        'session_token':stored_token,
    }
    return render(request,'accounts/reset_password.html',context)

@login_required(login_url='login')
def profile(request):
    orders=Order.objects.filter(user=request.user,is_ordered=True).order_by('-created_at')
    order_count=orders.count()
    try:
        user_profile = UserProfile.objects.only('profile_picture').get(user=request.user)
    except Exception as e:
        user_profile=None

    context={
        'order_count':order_count,
        'user_profile':user_profile,
    }
    return render(request,'accounts/profile.html',context)

@login_required(login_url='login')
def my_orders(request):
    orders=Order.objects.filter(user=request.user,is_ordered=True).order_by('-created_at')
    context={
        'orders':orders,
    }
    return render(request,'accounts/my_orders.html',context)

@login_required(login_url='login')
def edit_profile(request):
    user_profile=get_object_or_404(UserProfile,user=request.user)
    profile_url=None if user_profile.profile_picture=='' else user_profile.profile_picture.url
    profile_form=UserProfileForm(instance=user_profile)
    user_form=UserForm(instance=request.user)
    if request.method=='POST':
        user_form=UserForm(request.POST,instance=request.user)
        profile_form=UserProfileForm(request.POST,request.FILES,instance=user_profile)
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request,'Profile has been updated!')
            return redirect('edit_profile')
    # print(user_form.fields)
    context={
        'user_form':user_form,
        'profile_form':profile_form,
        'profile_url':profile_url,
    }
    return render(request,'accounts/edit_profile.html',context)

@login_required(login_url='login')
def change_password(request):
    form=ChangePasswordForm(user=request.user)
    if request.method=='POST':
        form=ChangePasswordForm(request.POST,user=request.user)
        if form.is_valid():
            user=User.objects.get(id=request.user.id)
            new_password=form.cleaned_data['new_password']
            user.set_password(new_password)
            user.save()
            login(request,user)
            messages.success(request,'Password has been updated successfully!')
            return redirect('profile')
    context={
        'form':form,
    }
    return render(request,'accounts/change_password.html',context)

@login_required(login_url='login')
def order_detail(request,order_id):
    order=None 
    subtotal=0
    tax_data=0
    ordered_products=None 
    try:
        # print(order_id)
        order=Order.objects.get(order_number=order_id,user=request.user,is_ordered=True)
        # print('order found')
        ordered_products=OrderProduct.objects.filter(order=order,user=request.user,ordered=True).order_by('updated_at')
        # print('ordered_products found')
        tax_data=json.loads(order.tax_data)
        for product in ordered_products:
            subtotal+=(product.quantity*product.product_price)
        context={
            'order':order,
            'ordered_products':ordered_products,
            'subottal':subtotal,
            'tax_data':tax_data,
        } 
        return render(request,'orders/order_detail.html',context)
    except:
        messages.error(request,'Error occured!Try again later.')
        return redirect('profile')