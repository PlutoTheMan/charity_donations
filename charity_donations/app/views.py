from django.shortcuts import render
from django.views import View
from .models import Donation, Institution, Category
from .forms import SignUpForm, DonationForm, UserEditForm, UserEditPasswordForm, ForgotPasswordForm,\
    ForgotPasswordNewPasswordForm
from django.shortcuts import redirect, HttpResponse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.contrib.auth import get_user_model
import json
import datetime
# FOR EMAILS
from .token import account_activation_token
from django.template.loader import render_to_string
from django.contrib.sites.shortcuts import get_current_site
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.core.mail import send_mail
from django.core.exceptions import ValidationError

class LandingPage(View):
    def get(self, request):
        donations = Donation.count_all()
        institutions_donated = Institution.count_all_donated()

        institutions = Institution.objects.filter(type=1).order_by('pk')
        institutions_paginator = Paginator(institutions, 5)
        institutions_page = request.GET.get('institutions_page')
        institutions_paginated = institutions_paginator.get_page(institutions_page)

        non_governmental_institutions = Institution.objects.filter(type=2)
        local_institutions = Institution.objects.filter(type=3)

        return render(request, "index.html", {
            'institutions': institutions,
            'non_governmental_institutions': non_governmental_institutions,
            'local_institutions': local_institutions,
            'donations_count': donations,
            'institutions_donated': institutions_donated,
            'institutions_paginated': institutions_paginated,
            'institutions_range': range(1, len(institutions)//5+2),
        })

def get_institution_page(request, page):
    print(page)
    institutions = Institution.objects.filter(type=1).order_by('-id').reverse()[(int(page)-1)*5:int(page)*5]
    parsed = []
    for i in institutions:
        r = {
            'name': i.name,
            'description': i.description,
            'categories': [],
        }

        for c in i.categories.all():
            r['categories'].append(c.name)
        parsed.append(r)

    return JsonResponse(parsed, safe=False)

class Logout(View):
    def get(self, request):
        logout(request)
        return redirect('home')

class Login(View):
    def get(self, request):
        return render(request, "login.html")
    def post(self, request):
        username = request.POST.get('email', '')
        password = request.POST.get('password', '')

        user_check = User.objects.filter(username=username).first()
        auth = authenticate(request, username=username, password=password)

        # IF WRONG PASSWORD
        if user_check and auth is None:
            if not user_check.is_active:
                return render(request, "login.html", {'not_activated': True})
            return render(request, "login.html", {'wrong_password': True})

        if auth is not None:
            login(request, auth)
            return redirect("home")
        else:
            return redirect("register")

class Register(View):
    def get(self, request):
        form = SignUpForm()
        return render(request, "register.html", {
            'form': form,
        })
    def post(self, request):
        form = {
            "first_name": request.POST.get('name', ''),
            "last_name": request.POST.get('surname', ''),
            "email": request.POST.get('email', ''),
            "username": request.POST.get('email', ''),
            "password1": request.POST.get('password', ''),
            "password2": request.POST.get('password2', ''),
        }

        form_check = SignUpForm(form)

        if form_check.is_valid():
            user = form_check.save(commit=False)
            user.is_active = False
            user.save()
            current_site = get_current_site(request)
            mail_subject = 'Activation link has been sent to your email id'
            message = render_to_string('acc_active_email.html', {
                'user': user,
                'domain': current_site.domain,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'token': account_activation_token.make_token(user),
            })

            to_email = form_check.cleaned_data.get('email')

            send_mail(
                mail_subject,
                message,
                'settings.EMAIL_HOST_USER',
                [to_email],
                fail_silently=False
            )
            print("TEST2")
            print("EMAIL SENT!")
            return redirect('login')
        else:
            print(form_check.errors)
        return render(request, "register.html", {
            'form': form_check,
        })

class AddDonation(View):
    def get(self, request):
        if request.user.is_authenticated:
            categories = Category.objects.all()
            institutions = Institution.objects.all()
            return render(request, "form.html", {'categories': categories, "institutions": institutions})
        else:
            return redirect('login')

class ConfirmDonation(View):
    def get(self, request):
        return redirect('home')

    def post(self, request):
        raw_categories = json.loads(request.POST.get('checked_categories', 'empty?'))
        parsed_categories = [int(i) for i in raw_categories]

        form_data = {
            "quantity": request.POST.get('bags', ''),
            "categories": parsed_categories,
            "institution": request.POST.get('organization', ''),
            "address": request.POST.get('address', ''),
            "phone_number": request.POST.get('phone', ''),
            "city": request.POST.get('city', ''),
            "zip_code": request.POST.get('postcode', ''),
            "pick_up_date": request.POST.get('data', ''),
            "pick_up_time": request.POST.get('time', ''),
            "pick_up_comment": request.POST.get('more_info', ''),
            "user": request.user
        }

        form = DonationForm(form_data)

        if form.is_valid():
            form.save()
            return render(request, "form-confirmation.html")
        else:
            return render(request, "form-confirmation.html", {"error": form.errors})

class UserView(View):
    def get(self, request, name):
        user = User.objects.filter(username=name).first()
        user_donations_done = Donation.objects.filter(user=user, picked_up=True)
        user_donations_in_progress = Donation.objects.filter(user=user, picked_up=False)
        user = User.objects.filter(username=name).first()
        return render(request, "user.html", {
            "user": user,
            "user_donations_done": user_donations_done,
            "user_donations_in_progress": user_donations_in_progress,
        })

class MarkDonationAsDone(View):
    def get(self, request, _id):
        return redirect("home")
    def post(self, request, _id):
        user = request.user
        print(_id)
        donation = Donation.objects.filter(pk=_id).first()
        if donation:
            donation.picked_up = True
            current_date = datetime.datetime.now()
            donation.picked_up_date = current_date.strftime("%Y-%m-%d")
            donation.picked_up_time = current_date.strftime("%H:%M:%S")
            donation.save()
        print(donation)
        return redirect(f"/user/{user.username}")

class UserSettings(View):
    def get(self, request):
        if not request.user.is_authenticated:
            return redirect("home")
        form = UserEditForm(instance=request.user)
        form_password = UserEditPasswordForm()
        return render(request, 'settings.html', {'form': form, 'form_password': form_password})

class ChangePersonalData(View):
    def post(self, request):
        form = UserEditForm(request.POST, instance=request.user)

        if form.is_valid():
            password = form.cleaned_data['confirm_password']
            check_password = request.user.check_password(password)

            if check_password:
                form.save()
        return redirect("settings")

class ChangePassword(View):
    def post(self, request):
        form_password = UserEditPasswordForm(request.POST)
        if form_password.is_valid():
            password = form_password.cleaned_data['password']
            check_password = request.user.check_password(password)

            if check_password:
                password1 = form_password.cleaned_data['new_password']
                password2 = form_password.cleaned_data['new_password_repeat']
                if password1 == password2:
                    if 'err_password' in request.session:
                        del request.session['err_password']
                    request.session['msg_password_success'] = 'Poprawnie zmieniono hasło.'
                    print(password1)
                    u = User.objects.get(username=request.user.username)
                    username = u.username
                    u.set_password(password1)
                    u.save()
                    return redirect("home")
                else:
                    request.session['err_password'] = 'Nowe hasła różnią się od siebie.'
                    return redirect("settings")
            else:
                request.session['err_password'] = 'Podaj poprawne aktualne hasło.'
                return redirect("settings")
        return redirect("settings")
        # return render(request, 'settings.html', {'form': form, 'form_password': form_password})

class ForgotPassword(View):
    def get(self, request):
        form = ForgotPasswordForm()
        return render(request, "forgot_password.html", {'form': form})

class RequestForgotPassword(View):
    def post(self, request):
        form = ForgotPasswordForm(request.POST)
        if form.is_valid():
            to_email = form.cleaned_data['email']
            user = User.objects.filter(email=to_email).first()
            if user:
                current_site = get_current_site(request)
                mail_subject = 'Password reset.'
                message = render_to_string('acc_password_reset.html', {
                    'user': user,
                    'domain': current_site.domain,
                    'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                    'token': account_activation_token.make_token(user),
                })

                send_mail(
                    mail_subject,
                    message,
                    'settings.EMAIL_HOST_USER',
                    [to_email],
                    fail_silently=False
                )
                return render(request, "forgot_password.html", {'form': form, 'info': 'Na adres email został wysłany link aktywacyjny.'})
            else:
                print("NIE MA USERA")
                return render(request, "forgot_password.html", {'form': form, 'err': 'Podany email jest nieprawidłowy.'})
        return render(request, "forgot_password.html", {'form': form})

def activate(request, uidb64, token):
    User = get_user_model()
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except(TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
    if user is not None and account_activation_token.check_token(user, token):
        user.is_active = True
        user.save()
        return HttpResponse('Thank you for your email confirmation. Now you can login your account.')
    else:
        return HttpResponse('Activation link is invalid!')

def reset_password(request, uidb64, token):
    if request.method == 'GET':
        User = get_user_model()
        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=uid)
        except(TypeError, ValueError, OverflowError, User.DoesNotExist):
            user = None
        if user is not None and account_activation_token.check_token(user, token):
            form = ForgotPasswordNewPasswordForm()
            return render(request, "reset_password_form.html", {'form': form, 'email': user.email})
        else:
            return HttpResponse('Reset password link is invalid!')
    elif request.method == 'POST':
        print("test1...")
        form = ForgotPasswordNewPasswordForm(request.POST)
        if form.is_valid():
            print('test2')
            email = request.POST['email']
            new_password = form.cleaned_data.get('new_password')
            new_password_repeat = form.cleaned_data.get('confirm_password')
            if new_password == new_password_repeat:
                User = get_user_model()
                u = User.objects.get(email=email)
                if account_activation_token.check_token(u, token):
                    print("saving...")
                    u.set_password(new_password)
                    u.save()
                else:
                    return render(request, "reset_password_form.html",
                                  {'form': form, 'err': 'Token is not valid.'})
                return render(request, "login.html", {'info': 'Your password has been changed.'})
            else:
                return render(request, "reset_password_form.html", {'form': form, 'err': 'Hasła muszą być takie same.'})
        else:
            form = ForgotPasswordNewPasswordForm(request.POST)
            email = request.POST['email']
            print(email)
            return render(request, "reset_password_form.html", {'form': form, 'email': email})


class ForgottenPasswordReset(View):
    def post(self, request):
        form = ForgotPasswordNewPasswordForm(request.POST)
        print(form)
        # if form.is_valid():
        #     # print(form)
        #     email = request.POST['email']
        #     new_password = form.cleaned_data.get('new_password')
        #     new_password_repeat = form.cleaned_data.get('confirm_password')
        #     if new_password == new_password_repeat:
        #         u = User.objects.get(email=email)
        #         u.set_password(new_password)
        #         u.save()
        #         return render(request, "login.html", {'info': 'Your password has been changed.'})
        #     else:
        #         return render(request, "reset_password_form.html", {'form': form, 'err': 'Passwords must be the same.'})



