from django.shortcuts import render, redirect
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth import login as auth_login, logout as auth_logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from .forms import SignUpForm, LoginForm, OTPForm
from .models import Profile

def Home(request):
    return render(request, 'index.html')

def About(request):
    return render(request, 'About.html')

def Contact(request):
    if request.method == "POST":
        name = request.POST.get("name")
        email = request.POST.get("email")
        project_type = request.POST.get("project-type")
        message = request.POST.get("message")

        # Email 1 — confirmation to the customer
        send_mail(
            subject="We've received your consultation request — Cozy Designs",
            message=f"Hi {name},\n\nThanks for reaching out to Cozy Designs! "
                    f"We've received your request regarding: {project_type}.\n\n"
                    f"Your message:\n{message}\n\n"
                    f"Our team will get back to you within 1-2 business days.\n\n"
                    f"— Cozy Designs",
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[email],
            fail_silently=False,
        )

        # Email 2 — notification to you (the business owner)
        send_mail(
            subject=f"New Consultation Request from {name}",
            message=f"New inquiry received:\n\n"
                    f"Name: {name}\n"
                    f"Email: {email}\n"
                    f"Project Type: {project_type}\n"
                    f"Message:\n{message}",
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=["farinubukola1407@gmail.com"],
            fail_silently=False,
        )

        context = {"success": True, "name": name}
        return render(request, "Contact.html", context)

    return render(request, 'Contact.html')

def Kitchen(request):
    return render(request, 'Kitchen.html')

def Living_room(request):
    return render(request, 'Living_room.html')


def signup_view(request):
    if request.method == "POST":
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data["password"])
            user.is_active = False  # can't log in until verified
            user.save()

            profile = Profile.objects.create(user=user)
            code = profile.generate_otp()
            
            
            send_mail(
                subject="Verify your email — Cozy Designs",
                message=f"Hi {user.username},\n\n"
                        f"Your verification code is: {code}\n\n"
                        f"This code expires in 10 minutes.\n\n"
                        f"— Cozy Designs",
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[user.email],
                fail_silently=False,
            )

            request.session["pending_user_id"] = user.id
            return redirect("verify_otp")
    else:
        form = SignUpForm()

    return render(request, "signup.html", {"form": form})


def verify_email_view(request, token):
    try:
        profile = Profile.objects.get(verification_token=token)
        profile.email_verified = True
        profile.save()

        user = profile.user
        user.is_active = True
        user.save()

        messages.success(request, "Your email has been verified! You can now log in.")
        return redirect("login")
    except Profile.DoesNotExist:
        messages.error(request, "Invalid or expired verification link.")
        return redirect("signup")


def verify_otp_view(request):
    user_id = request.session.get("pending_user_id")
    if not user_id:
        messages.error(request, "Session expired. Please sign up again.")
        return redirect("signup")

    if request.method == "POST":
        form = OTPForm(request.POST)
        if form.is_valid():
            code = form.cleaned_data["otp_code"]
            try:
                profile = Profile.objects.get(user__id=user_id)
            except Profile.DoesNotExist:
                messages.error(request, "Something went wrong. Please sign up again.")
                return redirect("signup")
            if profile.otp_is_valid(code):
                profile.email_verified = True
                profile.otp_code = None
                profile.save()

                user = profile.user
                user.is_active = True
                user.save()

                del request.session["pending_user_id"]
                messages.success(request, "Email verified! You can now log in.")
                return redirect("login")
            else:
                messages.error(request, "Invalid or expired code. Please try again.")
    else:
        form = OTPForm()
        
    return render(request, "verify_otp.html", {"form": form})

def resend_otp_view(request):
    user_id = request.session.get("pending_user_id")
    if not user_id:
        messages.error(request, "Session expired. Please sign up again.")
        return redirect("signup")

    try:
        profile = Profile.objects.get(user__id=user_id)
        code = profile.generate_otp()

        send_mail(
            subject="Your new Cozy Designs verification code",
            message=f"Your new verification code is: {code}\n\nThis code expires in 10 minutes.",
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[profile.user.email],
            fail_silently=False,
        )
        messages.success(request, "A new code has been sent to your email.")
    except Profile.DoesNotExist:
        messages.error(request, "Something went wrong. Please sign up again.")

    return redirect("verify_otp")

def login_view(request):
    if request.method == "POST":
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()

            try:
                if not user.profile.email_verified:
                    messages.error(request, "Please verify your email before logging in.")
                    return render(request, "login.html", {"form": form})
            except Profile.DoesNotExist:
                pass  # in case a user exists without a profile somehow

            auth_login(request, user)
            return redirect("home")
        else:
            messages.error(request, "Invalid username or password.")
    else:
        form = LoginForm()

    return render(request, "login.html", {"form": form})


def logout_view(request):
    auth_logout(request)
    return redirect("home")