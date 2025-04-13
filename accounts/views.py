from django.shortcuts import render,redirect
from django.http import HttpResponse
from .forms import RegistrationForm,LoginForm,ForgotPasswordForm,ResetPasswordForm
from .models import User
from django.contrib import messages
from django.contrib.auth import authenticate,login,logout
from django.contrib.auth.decorators import login_required
from .utils import send_verification_email
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_decode
import uuid
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
            mail_subject='Please activate your account!'
            htmlfile='account_verification.html'
            send_verification_email(request=request,user=user,mail_subject=mail_subject,htmlfile=htmlfile)
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
                login(request,user)
                messages.success(request,'Logged In Successfully!')
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
                send_verification_email(request=request,user=user,mail_subject=mail_subject,htmlfile=htmlfile)
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
    return render(request,'accounts/profile.html')