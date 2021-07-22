# Create your views here.
import datetime
import math
import operator
import time

import requests
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import send_mail
from django.db.models import Q
from django.http import Http404, HttpResponse, JsonResponse
from django.shortcuts import render, redirect
from django.template.loader import render_to_string
from django.utils.decorators import method_decorator
from django.utils.encoding import force_text, force_bytes
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
# Create your views here.
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from haversine import haversine, Unit
from twilio.rest import Client as TwilioClient

from EmployeeList.forms import LoginForm, UserRegistrationForm, InvestigatorForm, ClientForm, UserUpdateForm, \
    CustomerForm
from EmployeeList.models import Client, PrivateInvestigator, Customer, BookedInvestigator, Notification, Message, \
    InvestigatorBlockEvent
from .token import account_activation_token


class HomeView(View):
    def get(self, request):
        if request.user.is_authenticated:
            if request.session['user_type'] == 'investigator':
                return redirect('investigator_profile')
            else:
                return redirect('client_profile')
        return render(request, 'index.html')


class LoginView(View):
    def get(self, request):
        if request.user.is_authenticated:
            if request.session['user_type'] == 'investigator':
                return redirect('investigator_profile')
        return render(request, 'auth/login.html', {"form": LoginForm})

    def post(self, request):
        username = request.POST['username']
        password = request.POST['password']
        auth = authenticate(request, username=username, password=password)
        if auth:
            if request.path == '/employee/login/':
                try:
                    user = Client.objects.get(user__username=username)
                    request.session['user_type'] = 'client'
                    login(request, auth)
                    self.request.session['notification'] = Notification.objects.filter(user=self.request.user,
                                                                                       seen=False).count()
                    self.request.session['inbox'] = Message.objects.filter(receiver=self.request.user,
                                                                           seen=False).count()
                    if request.GET.get('next'):
                        return redirect(request.GET.get('next'))
                    return redirect('client_profile')
                except:
                    pass
            else:
                try:
                    user = PrivateInvestigator.objects.get(user__username=username)
                    request.session['user_type'] = 'investigator'
                    login(request, auth)
                    self.request.session['notification'] = Notification.objects.filter(user=self.request.user,
                                                                                       seen=False).count()
                    self.request.session['inbox'] = Message.objects.filter(receiver=self.request.user,
                                                                           seen=False).count()
                    if request.GET.get('next'):
                        return redirect(request.GET.get('next'))
                    return redirect('investigator_profile')
                except:
                    pass
        messages.error(request, "Invalid username or password!")
        if request.path == '/employee/login/':
            return redirect('client_login')
        else:
            return redirect('investigator_login')


def logoutView(request):
    logout(request)
    return redirect('home')


class RegistrationView(View):
    def get(self, request):
        context = {'form': UserRegistrationForm}
        if request.path == '/investigator/register/':
            context['userForm'] = InvestigatorForm
        else:
            context['userForm'] = ClientForm
        return render(request, 'auth/registration.html', context)

    def post(self, request):
        form = UserRegistrationForm(request.POST)
        if request.path == '/investigator/register/':
            userForm = InvestigatorForm(request.POST)
        else:
            if request.POST['secret_code'] != '853216':
                messages.error(request, 'Invalid secret code.')
                return redirect('client_registration')
            userForm = ClientForm(request.POST)
        if form.is_valid() and userForm.is_valid():
            new_user = User.objects.create_user(**form.cleaned_data)
            new_user.is_active = False
            new_user.save()
            userFormInstance = userForm.save(commit=False)
            userFormInstance.user = new_user
            userFormInstance.save()

            current_site = get_current_site(request)
            mail_subject = 'PIs: Activate your account.'
            message = render_to_string('mail_confirmation_message.html', {
                'user': new_user,
                'domain': current_site.domain,
                'uid': urlsafe_base64_encode(force_bytes(new_user.pk)),
                'token': account_activation_token.make_token(new_user)
            })
            to_email = form.cleaned_data.get('email')
            to_list = [to_email]
            from_email = settings.EMAIL_HOST_USER
            send_mail(mail_subject, message, from_email, to_list, fail_silently=True)
            messages.success(request, 'Account is created successfully. Check email to activate your account.')
            if request.path == '/investigator/register/':
                return redirect('investigator_login')
            else:
                return redirect('client_login')
        else:
            messages.error(request, form.errors)
            if request.path == '/investigator/register/':
                return redirect('investigator_registration')
            else:
                return redirect('client_registration')


class ActivateAccount(View):
    def get(self, request, uid, token):
        try:
            id = force_text(urlsafe_base64_decode(uid))
            user = User.objects.get(pk=id)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            user = None

        if user is not None and account_activation_token.check_token(user, token):
            user.is_active = True
            user.save()
            messages.success(request, 'Account is activated, you can login now')
            try:
                Client.objects.get(user__username=user.username)
                return redirect('client_login')
            except:
                return redirect('investigator_login')
        else:
            # invalid link
            return HttpResponse("<h1>Invalid activation link</h1>")


class PIProfile(View):
    def get(self, request):
        pi = PrivateInvestigator.objects.get(user__username=request.user.username)
        return render(request, 'pi_profile.html', {'pi': pi})


class ProfileUpdate(View):
    def get(self, request):
        if request.session['user_type'] == 'investigator':
            if request.path == '/investigator/profile/update/':
                pass
            else:
                return redirect('investigator_profile_update')
        else:
            if request.path == '/investigator/profile/update/':
                return redirect('client_profile_update')

        instance = User.objects.get(username=request.user.username)
        userForm = UserUpdateForm(instance=instance)
        if request.session['user_type'] == 'investigator':
            instance = PrivateInvestigator.objects.get(user__username=request.user.username)
            form = InvestigatorForm(instance=instance)
        else:
            instance = Client.objects.get(user__username=request.user.username)
            form = ClientForm(instance=instance)
        return render(request, 'update_profile.html', {"form": form, "form2": userForm})

    def post(self, request):
        instance = User.objects.get(username=request.user.username)
        userForm = UserUpdateForm(request.POST, instance=instance)

        if request.session['user_type'] == 'investigator':
            u = PrivateInvestigator.objects.get(user__username=request.user.username)
            form = InvestigatorForm(request.POST, instance=u)
        else:
            u = Client.objects.get(user__username=request.user.username)
            form = ClientForm(request.POST, instance=u)
        if userForm.is_valid() and form.is_valid():
            userForm.save()
            form.save()
            messages.success(request, 'Profile is updated successfully')
        else:
            messages.error(request, 'Profile is not updated')
        if request.session['user_type'] == 'investigator':
            return redirect('investigator_profile_update')
        else:
            return redirect('client_profile_update')


class ClientProfile(View):
    def get(self, request):
        client = Client.objects.get(user__username=request.user.username)
        return render(request, 'client_profile.html', {'pi': client})


class Search(View):
    def get(self, request):
        if request.GET.get('customer_id') is None or request.GET.get('customer_id') == '':
            try:
                customers = Customer.objects.filter(added_by__user__id=request.user.id)
            except:
                return redirect('search')
        else:
            customers = None
        if request.GET.get('customer_id'):
            try:
                customer = Customer.objects.get(id=request.GET.get('customer_id'))
                input_text = customer.address.place
            except:
                return redirect('search')
        else:
            customer = None
            input_text = ''
        return render(request, 'search.html', {'customers': customers, 'customer': customer, 'input_text': input_text})

    def post(self, request):
        p = request.POST['address']
        response = requests.get(
            'https://maps.googleapis.com/maps/api/geocode/json?address=' + p + '&key=' + settings.PLACES_MAPS_API_KEY)
        if response.status_code == 200:
            response_json = response.json()
            lat = response_json['results'][0]['geometry']['location']['lat']
            lng = response_json['results'][0]['geometry']['location']['lng']
        cid = request.GET.get('customer_id')
        if cid:
            customer = Customer.objects.get(id=cid)
        else:
            raise Http404('Invalid Customer ID')
        if customer:
            cCoordinate = customer.address
        else:
            czip = None
        me = Client.objects.get(user__username=request.user.username)
        inv = PrivateInvestigator.objects.filter(country=me.country, available=True)

        for i in inv:
            # print(cCoordinate.latitude, cCoordinate.longitude)
            i.client_distance = haversine((i.address.latitude, i.address.longitude),
                                          (me.address.latitude, me.address.longitude), unit=Unit.MILES)
            i.client_travel_time = self.estimatedTravelTime(i.client_distance)
            i.customer_distance = haversine((i.address.latitude, i.address.longitude),
                                            (cCoordinate.latitude, cCoordinate.longitude), unit=Unit.MILES)
            i.customer_travel_time = self.estimatedTravelTime(i.customer_distance)
            i.input_distance = haversine((i.address.latitude, i.address.longitude), (lat, lng), unit=Unit.MILES)
            i.input_travel_time = self.estimatedTravelTime(i.input_distance)
        sortedInvByDistance = sorted(inv, key=operator.attrgetter('customer_distance'))
        finalResult = []
        for s in sortedInvByDistance:
            if not math.isnan(s.customer_distance):
                finalResult.append(s)
        return render(request, 'search.html', {'pis': finalResult, 'input_text': p})

    def estimatedTravelTime(self, distance):
        if (distance * 2) > 59:
            s = ''
            if math.floor((distance * 2) / 60) > 1:
                s = s + 's'
            return str(math.floor((distance * 2) / 60)) + 'hour' + s + ' ' + str(
                math.ceil((distance * 2) % 60)) + 'minutes'
        else:
            if math.ceil(distance * 2) > 1:
                return str(math.ceil(distance * 2)) + 'minutes'
            else:
                return str(math.ceil(distance * 2)) + 'minute'


class CustomerView(View):
    def get(self, request):
        if request.session['user_type'] == 'client':
            customers = Customer.objects.filter(added_by__user=request.user)
            return render(request, 'customer.html', {"customers": customers})
        else:
            return HttpResponse('<h1>You are not authorized to access this page.</h1>')


class AddCustomerView(View):
    def get(self, request):
        if request.session['user_type'] == 'client':
            return render(request, 'add_customer.html', {'form': CustomerForm()})
        else:
            return HttpResponse('<h1>You are not authorized to access this page.</h1>')

    def post(self, request):
        form = CustomerForm(request.POST)
        if form.is_valid():
            instance = form.save(commit=False)
            cl = Client.objects.get(user=request.user)
            instance.added_by = cl
            instance.save()
            messages.success(request, 'Customer is added successfully!')
            return redirect('customer_add')
        else:
            messages.error(request, form.errors)
            return redirect('customer_add')


def DeleteCustomerView(request, id):
    try:
        if request.session['user_type'] == 'client':
            customer = Customer.objects.get(id=id)
            customer.delete()
        else:
            return HttpResponse('<h1>You are not authorized to access this page.</h1>')
    except:
        pass
    return redirect('customer')


class CustomerUpdateView(View):
    def get(self, request, id):
        try:
            if request.session['user_type'] == 'client':
                customer = Customer.objects.get(id=id)
                form = CustomerForm(instance=customer)
                return render(request, 'add_customer.html', {'form': form})
            else:
                return HttpResponse('<h1>You are not authorized to access this page.</h1>')
        except:
            raise Http404('Customer not found')

    def post(self, request, id):
        try:
            customer = Customer.objects.get(id=id)
            form = CustomerForm(request.POST, instance=customer)
            if form.is_valid():
                form.save()
                messages.success(request, 'Customer is updated')
            else:
                messages.error(request, 'Customer is not updated')
            return redirect('customer_update', id)
        except:
            raise Http404('Customer not found')


class BookInvestigator(View):
    def get(self, request):
        book = BookedInvestigator.objects.filter(customer__added_by__user_id=request.user.id)
        return render(request, 'book_investigator.html', {'bookingData': book})

    def post(self, request):
        customer = request.POST['customer_id']
        investigator = request.POST['investigator_id']
        t = BookedInvestigator.objects.create(customer_id=customer, investigator_id=investigator)
        t.save()
        inv = PrivateInvestigator.objects.get(id=investigator)
        inv.available = False
        inv.save()
        Notification.objects.create(user=inv.user, sender=self.request.user, type="booked")
        message_to_broadcast = "Client available: Call the office so that we can brief you on this case."
        twilio_client = TwilioClient(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
        try:
            twilio_client.messages.create(to=inv.phone_number, from_=settings.TWILIO_NUMBER, body=message_to_broadcast)
        except:
            print('Unable to send message to ' + inv.phone_number)
        return redirect('booked_investigator')


def deleteBookingInfo(request, id):
    try:
        booking = BookedInvestigator.objects.get(id=id)
        inv = PrivateInvestigator.objects.get(id=booking.investigator.id)
        inv.available = True
        inv.save()
        Notification.objects.create(user=inv.user, sender=request.user, type='unbooked')
        booking.delete()
    except:
        pass
    return redirect('booked_investigator')


class NotificationView(View):
    def get(self, request):
        notifications = Notification.objects.filter(user=self.request.user).order_by("-notify_at")
        return render(request, 'notification.html', {"notifications": notifications})


class NotificationResponse(View):
    def get(self, request, id):
        try:
            notification = Notification.objects.get(user=self.request.user, id=id)
            notification.seen = True
            notification.save()
            self.request.session['notification'] = self.request.session['notification'] - 1
            return redirect('notification')
        except:
            return redirect('notification')


class InboxBase(View):
    def get(self, request):
        inbox = Message.objects.filter(receiver=self.request.user).order_by('-message_at').first()
        inbox2 = Message.objects.filter(sender=self.request.user).order_by('-message_at').first()
        if inbox2 is None and inbox is None:
            return render(request, 'inbox_base.html')
        else:
            if inbox2:
                return redirect('inbox', inbox2.receiver.username)
            else:
                return redirect('inbox', inbox.sender.username)


class Inbox(View):
    def get(self, request, username):
        u = User.objects.filter(username=username).first()
        if u is None:
            return redirect('home')
        if self.request.session['inbox'] and self.request.session['inbox'] > 0:
            message = Message.objects.filter(receiver=self.request.user, sender__username=username)
            if message.count() > 0:
                c = 0
                for m in message:
                    if not m.seen:
                        c = c + 1
                        m.seen = True
                        m.save()
                self.request.session['inbox'] = self.request.session['inbox'] - c
        contact = Message.objects.filter(
            Q(receiver=self.request.user) | Q(sender__username=self.request.user.username)).order_by('-message_at')
        l = []
        data = []
        for c in contact:
            if c.sender == self.request.user:
                if l.count(c.receiver.username) == 0:
                    l.append(c.receiver.username)
                    data.append(c)
            elif c.receiver == self.request.user:
                if l.count(c.sender.username) == 0:
                    l.append(c.sender.username)
                    data.append(c)

        message = Message.objects.filter(Q(receiver=self.request.user, sender__username=username) |
                                         Q(receiver__username=username,
                                           sender__username=self.request.user.username)).order_by('message_at')
        return render(request, 'inbox.html',
                      {"messages": message, "histories": data, 'current_user': username, 'user': u})

    def post(self, request, username):
        message = request.POST['inbox']
        message = ' '.join(message.split())
        if len(message) == 0:
            return redirect('inbox', username)
        try:
            Message.objects.create(sender=self.request.user, receiver=User.objects.get(username=username), text=message)
        except:
            pass
        return redirect('inbox', username)


@method_decorator(csrf_exempt, name='dispatch')
class Calender(View):
    def get(self, request):
        events = InvestigatorBlockEvent.objects.filter(investigator__user=self.request.user)
        return render(request, 'calendar.html', {"events": events})

    def post(self, request):
        inv = PrivateInvestigator.objects.get(user_id=self.request.user.id)
        InvestigatorBlockEvent.objects.create(investigator=inv, date=request.POST['date'],
                                              title=request.POST['title'])
        data = {'status': 'Saved successfully'}
        return JsonResponse(data)


class RemoveEvent(View):
    def get(self, request, id):
        try:
            d = InvestigatorBlockEvent.objects.get(id=id)
            d.delete()
        except:
            pass
        return redirect('investigator_calender_block')
