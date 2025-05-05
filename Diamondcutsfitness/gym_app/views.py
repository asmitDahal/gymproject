from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from gym_app.models import Contact, MembershipPlan, Trainer, Enrollment, Gallery, Attendance, Service

# Extra imports for email verification
from django.contrib.sites.shortcuts import get_current_site
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.template.loader import render_to_string
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.conf import settings
from django.http import HttpResponse
from django.utils import timezone
from .models import EmailOTP

# Create your views here.
def Home(request):
    return render(request,"index.html")

def gallery(request):
    posts=Gallery.objects.all()
    context={"posts":posts}
    return render(request,"gallery.html",context)


def attendance(request):
    if not request.user.is_authenticated:
        messages.warning(request,"Please Login and Try Again")
        return redirect('/login')
    SelectTrainer=Trainer.objects.all()
    context={"SelectTrainer":SelectTrainer}
    if request.method=="POST":
        phonenumber=request.POST.get('PhoneNumber')
        Login=request.POST.get('logintime')
        Logout=request.POST.get('loginout')
        SelectWorkout=request.POST.get('workout')
        TrainedBy=request.POST.get('trainer')
        query=Attendance(phonenumber=phonenumber,Login=Login,Logout=Logout,SelectWorkout=SelectWorkout,TrainedBy=TrainedBy)
        query.save()
        messages.warning(request,"Attendace Applied Success")
        return redirect('/attendance')
    return render(request,"attendance.html",context)

def profile(request):
    if not request.user.is_authenticated:
        messages.warning(request,"Please Login and Try Again")
        return redirect('/login')
    user_phone=request.user
    posts=Enrollment.objects.filter(PhoneNumber=user_phone)
    attendance=Attendance.objects.filter(phonenumber=user_phone)
    print(posts)
    context={"posts":posts,"attendance":attendance}
    return render(request,"profile.html",context)

import random
from django.core.mail import send_mail
from .models import EmailOTP

def generate_otp():
    return str(random.randint(100000, 999999))

def signup(request):
    if request.method == "POST":
        username = request.POST.get('usernumber')
        email = request.POST.get('email')
        pass1 = request.POST.get('pass1')
        pass2 = request.POST.get('pass2')

        if len(username) != 10:
            messages.info(request, "Phone Number Must be 10 Digits")
            return redirect('/signup')

        if pass1 != pass2:
            messages.info(request, "Password is not Matching")
            return redirect('/signup')

        if User.objects.filter(username=username).exists():
            messages.warning(request, "Phone Number is Taken")
            return redirect('/signup')

        if User.objects.filter(email=email).exists():
            messages.warning(request, "Email is Taken")
            return redirect('/signup')

        # Create inactive user
        myuser = User.objects.create_user(username=username, email=email, password=pass1)
        myuser.is_active = False
        myuser.save()
        request.session['email'] = email  # Required for resend_otp

        # Generate and save OTP
        otp = generate_otp()
        EmailOTP.objects.create(user=myuser, otp=otp)

        # Send OTP via email
        send_mail(
                    'Your OTP for Gym Registration',
                    f'Hi {username}, your OTP is: {otp}',
                    settings.EMAIL_HOST_USER,  # ✅ Use the actual authenticated email
                    [email],
                    fail_silently=False,
                )
        # Store user ID in session for verification
        request.session['pending_user'] = myuser.id
        messages.success(request, "OTP sent to your email. Please verify.")
        return redirect('verify_otp')  # Make sure this URL exists

    return render(request, 'signup.html')


# verify otp
def verify_otp(request):
    user_id = request.session.get('pending_user')
    if not user_id:
        return redirect('/signup')

    user = User.objects.get(id=user_id)
    if request.method == "POST":
        entered_otp = request.POST.get('otp')
        otp_obj = EmailOTP.objects.filter(user=user).latest('created_at')


        if otp_obj and otp_obj.otp == entered_otp:
            user.is_active = True
            user.save()
            otp_obj.delete()
            messages.success(request, "Your account has been verified. You can now log in.")
            return redirect('/login')
        else:
            messages.error(request, "Invalid OTP. Try again.")

    return render(request, 'verify_otp.html')


#resend_otp

def resend_otp(request):
    if 'email' not in request.session:
        messages.error(request, "Session expired. Please signup again.")
        return redirect('signup')

    email = request.session['email']
    otp = str(random.randint(100000, 999999))

    try:
        user = User.objects.get(email=email)
    except User.DoesNotExist:
        messages.error(request, "User not found. Please sign up again.")
        return redirect('signup')

    # Save or update the OTP in EmailOTP model
    otp_obj, created = EmailOTP.objects.get_or_create(user=user)
    otp_obj.otp = otp
    otp_obj.created_at = timezone.now()
    otp_obj.save()

    # Email content
    subject = "Your OTP for Account Verification"
    message = f"Dear User,\n\nYour new OTP for verification is: {otp}\n\nThank you."
    from_email = 'youremail@example.com'  # Replace with actual email

    try:
        send_mail(subject, message, settings.EMAIL_HOST_USER, [email])
        messages.success(request, "OTP has been resent to your email.")
    except:
        messages.error(request, "Failed to send OTP. Try again later.")

    return redirect('verify_otp')


def handlelogin(request):
    # Clear any previously stored messages
    list(messages.get_messages(request))  # this clears queued messages

    if request.method == "POST":
        username = request.POST.get('usernumber')
        pass1 = request.POST.get('pass1')
        myuser = authenticate(username=username, password=pass1)

        if myuser is not None:
            login(request, myuser)
            messages.success(request, "Login Successful")
            return redirect('/')
        else:
            messages.error(request, "Invalid Credentials")
            return redirect('/login')

    return render(request, "handlelogin.html")


def handleLogout(request):
    # Clear any previously stored messages (e.g., from login)
    list(messages.get_messages(request))

    logout(request)
    messages.success(request, "Logout Success")
    return redirect('/login')

def contact(request):
    if request.method=="POST":
        name=request.POST.get('fullname')
        email=request.POST.get('email')
        number=request.POST.get('num')
        desc=request.POST.get('desc')
        myquery=Contact(name=name,email=email,phonenumber=number,description=desc)
        myquery.save()       
        messages.info(request,"Thanks for Contacting us we will get back you soon")
        return redirect('/contact')
        
    return render(request,"contact.html")


def enroll(request):
    if not request.user.is_authenticated:
        messages.warning(request,"Please Login and Try Again")
        return redirect('/login')

    Membership=MembershipPlan.objects.all()
    SelectTrainer=Trainer.objects.all()
    context={"Membership":Membership,"SelectTrainer":SelectTrainer}
    if request.method=="POST":
        FullName=request.POST.get('FullName')
        email=request.POST.get('email')
        gender=request.POST.get('gender')
        PhoneNumber=request.POST.get('PhoneNumber')
        DOB=request.POST.get('DOB')
        member=request.POST.get('member')
        trainer=request.POST.get('trainer')
        reference=request.POST.get('reference')
        address=request.POST.get('address')
        query=Enrollment(FullName=FullName,Email=email,Gender=gender,PhoneNumber=PhoneNumber,DOB=DOB,SelectMembershipplan=member,SelectTrainer=trainer,Reference=reference,Address=address)
        query.save()
        messages.success(request,"Thanks For Enrollment")
        return redirect('/join')



    return render(request,"enroll.html",context)


# email authentication

from django.contrib.auth import get_user_model
from django.utils.encoding import force_str

def activate(request, uidb64, token):
    User = get_user_model()
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except:
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()
        return HttpResponse('Thank you for your email confirmation. You can now login.')
    else:
        return HttpResponse('Activation link is invalid!')


def service(request):
    services = Service.objects.all()
    return render(request, 'service.html', {'services': services})