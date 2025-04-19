from django.shortcuts import render, redirect
from django.http import JsonResponse
from store.models import Product
from django.contrib import admin, messages
from django.utils import timezone
from cart.models import Coupon
from cart.forms import CouponForm
import csv
import io
import uuid
from django.conf import settings
from accounts.models import User
from accounts.utils import send_notification_email
from django.contrib.sites.shortcuts import get_current_site
from django.contrib.admin.views.decorators import staff_member_required
from django.db import IntegrityError


def home(request):
    products = Product.objects.filter(is_available=True)
    context = {
        'products': products
    }
    return render(request, 'index.html', context)


@staff_member_required
def assign_coupons(request):
    form = CouponForm()
    current_site = get_current_site(request)
    if request.method == 'POST':
        form = CouponForm(request.POST, request.FILES)
        if form.is_valid():
            csv_file = form.cleaned_data.get('csv_file')
            email_subject = form.cleaned_data.get('email_subject')
            code = form.cleaned_data.get('code').upper()
            discount = form.cleaned_data.get('discount')
            validity_days = form.cleaned_data.get('validity_days')
            htmlfile = 'discount_email.html'
            rows = csv.reader(csv_file.read().decode('utf-8').splitlines())
            users_not_mailed = []
            users_coupon_exists = []
            emailed = 0
            for row in rows:
                email = row[0]
                # print(email)
                try:
                    user = User.objects.get(email__exact=email)
                    code = code
                    expires_at = timezone.now() + timezone.timedelta(days=validity_days)
                    if not Coupon.objects.filter(
                            code=code, user=user, used=False).exists():
                        try:
                            Coupon.objects.create(
                                code=code,
                                discount_percent=discount,
                                user=user,
                                expires_at=expires_at,
                            )
                        except IntegrityError:
                            print('Integrity Error')
                    else:
                        print(f'Skipped {code} and {user} already exists')
                    context = {
                        'domain': current_site.domain,
                        'user': user,
                        'code': code,
                        'percent': discount,
                        'valid_days': validity_days
                    }
                    # print('email has been sent')
                    send_notification_email(
                        request=request,
                        user=user,
                        mail_subject=email_subject,
                        htmlfile=htmlfile,
                        context=context)
                    emailed += 1
                except User.DoesNotExist:
                    users_not_mailed.append(email)
                    continue
            response_data = {'status': 200, 'mailed': emailed}
            if len(users_not_mailed) != 0:
                csv_buffer = io.StringIO()
                csv_writer = csv.writer(csv_buffer)
                csv_writer.writerow(['Email', 'Reason'])

                for email in users_not_mailed:
                    csv_writer.writerow([email, 'User not found!'])

                response_data['has_failures'] = True
                response_data['failed_count'] = len(users_not_mailed)
                response_data['csv_content'] = csv_buffer.getvalue()
            else:
                response_data['has_failures'] = False

            return JsonResponse(response_data)
        else:
            print('form is invalid')
            return redirect('admin_assign_coupons')
    context = {
        'form': form,
    }
    return render(request, 'admin/assign_coupon.html', context)
