"""EmployeeSearch URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
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
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.auth.decorators import login_required
from django.urls import path

from EmployeeList import views
from django.contrib.auth import views as auth_views
urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.HomeView.as_view(), name='home'),
    path('investigator/login/', views.LoginView.as_view(), name='investigator_login'),
    path('employee/login/', views.LoginView.as_view(), name='client_login'),
    path('investigator/register/', views.RegistrationView.as_view(), name='investigator_registration'),
    path('employee/register/', views.RegistrationView.as_view(), name='client_registration'),
    path('activate/<uid>/<token>/', views.ActivateAccount.as_view(), name='activate_account'),
    path('investigator/profile/', login_required(login_url='/investigator/login/')(views.PIProfile.as_view()), name='investigator_profile'),
    path('employee/profile/', login_required(login_url='/employee/login/')(views.ClientProfile.as_view()), name='client_profile'),
    path('investigator/profile/update/', login_required(login_url='/investigator/login/')(views.ProfileUpdate.as_view()), name='investigator_profile_update'),
    path('employee/profile/update/', login_required(login_url='/investigator/login/')(views.ProfileUpdate.as_view()), name='client_profile_update'),
    path('investigator/block/', login_required(login_url='/investigator/login/')(views.Calender.as_view()), name='investigator_calender_block'),
    path('investigator/block/delete/<id>/', login_required(login_url='/investigator/login/')(views.RemoveEvent.as_view()), name='investigator_block_remove'),
    path('customer/', login_required(login_url='/employee/login/')(views.CustomerView.as_view()), name='customer'),
    path('customer/add/', login_required(login_url='/employee/login/')(views.AddCustomerView.as_view()), name='customer_add'),
    path('customer/delete/<int:id>/', login_required(login_url='/employee/login/')(views.DeleteCustomerView), name='customer_delete'),
    path('customer/update/<int:id>/', login_required(login_url='/employee/login/')(views.CustomerUpdateView.as_view()), name='customer_update'),
    path('booked_investigator/', login_required(login_url='/employee/login/')(views.BookInvestigator.as_view()), name='booked_investigator'),
    path('booked_investigator/delete/<int:id>/', login_required(login_url='/employee/login/')(views.deleteBookingInfo), name='booked_investigator_delete'),
    path('search/', login_required(login_url='/employee/login/')(views.Search.as_view()), name='search'),
    path('notification/', login_required(login_url='/')(views.NotificationView.as_view()), name='notification'),
    path('notification/<id>/', login_required(login_url='/')(views.NotificationResponse.as_view()), name='notification_response'),
    path('inbox/', login_required(login_url='/')(views.InboxBase.as_view()), name='inbox_base'),
    path('inbox/<username>/', login_required(login_url='/')(views.Inbox.as_view()), name='inbox'),
    path('logout/', views.logoutView, name='logout'),


    path('reset_password/', auth_views.PasswordResetView.as_view(template_name='auth/password_reset_view.html'), name="reset_password"),
    path('reset_password_sent/', auth_views.PasswordResetDoneView.as_view(template_name='auth/password_reset_sent.html'), name="password_reset_done"),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(template_name='auth/password_reset_confirm.html'), name="password_reset_confirm"),
    path('reset_password_complete/', auth_views.PasswordResetCompleteView.as_view(template_name='auth/password_reset_complete.html'), name="password_reset_complete")
]+static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)