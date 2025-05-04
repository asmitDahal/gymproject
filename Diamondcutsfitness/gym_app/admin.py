from django.contrib import admin
from gym_app.models import Contact,MembershipPlan,Enrollment,Trainer,Gallery,Attendance, Service

# Register your models here.
admin.site.register(Contact)
admin.site.register(MembershipPlan)
admin.site.register(Enrollment)
admin.site.register(Trainer)
admin.site.register(Gallery)
admin.site.register(Attendance)
admin.site.register(Service)