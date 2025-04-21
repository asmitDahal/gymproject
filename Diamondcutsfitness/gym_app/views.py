from django.shortcuts import render,redirect
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth import authenticate,login,logout
# from gym_app.models import Contact,MembershipPlan,Trainer,Enrollment,Gallery,Attendance
# Create your views here.
def Home(request):
    return render(request,"index.html")