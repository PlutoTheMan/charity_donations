"""
URL configuration for charity_donations project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from app.views import LandingPage, Login, Register, AddDonation, Logout, ConfirmDonation,\
    UserView, MarkDonationAsDone, UserSettings, ChangePersonalData, ChangePassword, get_institution_page, activate, \
    ForgotPassword, RequestForgotPassword, reset_password, ForgottenPasswordReset

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', LandingPage.as_view(), name="home"),
    path('get_institution_page/<int:page>', get_institution_page, name="get_institution_page"),
    path('user/<str:name>', UserView.as_view(), name="user"),
    path('settings/edit_personal_data', ChangePersonalData.as_view(), name="edit_personal_data"),
    path('settings/edit_password', ChangePassword.as_view(), name="edit_password"),
    path('settings', UserSettings.as_view(), name="settings"),
    path('login', Login.as_view(), name="login"),
    path('logout', Logout.as_view(), name="logout"),
    path('register', Register.as_view(), name="register"),
    path('add_donation', AddDonation.as_view(), name="donate"),
    path('donate_confirmation', ConfirmDonation.as_view(), name="donate_confirm"),
    path('mark_donation/<str:_id>', MarkDonationAsDone.as_view(), name="mark_donation"),
    path('activate/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/', activate,
         name='activate'),
    path('reset_password/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/', reset_password,
         name='form_request_forgot_password'),
    path('forgot_password', ForgotPassword.as_view(), name="forgot_password"),
    path('request_forgot_password', RequestForgotPassword.as_view(), name="request_forgot_password"),
    path('forgotten_password_reset', ForgottenPasswordReset.as_view(), name="forgotten_password_reset"),
]
