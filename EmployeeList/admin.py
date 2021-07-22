from django.contrib import admin

# Register your models here.
from EmployeeList.models import PrivateInvestigator, Client, Customer, BookedInvestigator, Notification, Message, \
    InvestigatorBlockEvent

admin.site.register(PrivateInvestigator)
admin.site.register(Client)
admin.site.register(Customer)
admin.site.register(BookedInvestigator)
admin.site.register(Notification)
admin.site.register(Message)
admin.site.register(InvestigatorBlockEvent)
