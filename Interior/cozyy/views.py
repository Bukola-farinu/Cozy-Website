from django.shortcuts import render, redirect
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth import login as auth_login, logout as auth_logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.mail import EmailMultiAlternatives

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


def send_otp_email(user, code):
    subject = "Your Cozy Designs verification code"
    plain_message = f"Hi {user.username},\n\nYour verification code is: {code}\n\nThis code expires in 10 minutes."

    html_message = f"""
    <div style="font-family: 'Segoe UI', Arial, sans-serif; max-width: 480px; margin: 0 auto; padding: 40px 30px; background-color: #faf8f5;">
        <h2 style="color: #222222; margin-bottom: 10px;">Verify Your Email</h2>
        <p style="color: #555555; font-size: 15px;">Hi {user.username},</p>
        <p style="color: #555555; font-size: 15px;">Use the code below to verify your Cozy Designs account:</p>
        <div style="background-color: #ffffff; border: 1px solid #e0dcd5; border-radius: 8px; padding: 25px; text-align: center; margin: 25px 0;">
            <span style="font-size: 36px; font-weight: 700; letter-spacing: 10px; color: #222222;">{code}</span>
        </div>
        <p style="color: #888888; font-size: 13px;">This code expires in 10 minutes. If you didn't request this, you can safely ignore this email.</p>
        <p style="color: #222222; font-weight: 600; margin-top: 30px;">— Cozy Designs</p>
    </div>
    """

    msg = EmailMultiAlternatives(subject, plain_message, settings.DEFAULT_FROM_EMAIL, [user.email])
    msg.attach_alternative(html_message, "text/html")
    msg.send()

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
            
            
            # send_mail(
                # subject="Verify your email — Cozy Designs",
                # message=f"Hi {user.username},\n\n"
                #         f"Your verification code is: {code}\n\n"
                #         f"This code expires in 10 minutes.\n\n"
                #         f"— Cozy Designs",
                # from_email=settings.DEFAULT_FROM_EMAIL,
                # recipient_list=[user.email],
                # fail_silently=False,
            # )
            send_otp_email(user, code)

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
    
    try:
        profile = Profile.objects.get(user__id=user_id)
    except Profile.DoesNotExist:
        messages.error(request, "Something went wrong. Please sign up again.")
        return redirect("signup")

    if request.method == "POST":
        form = OTPForm(request.POST)
        if form.is_valid():
            code = form.cleaned_data["otp_code"]
            
            if profile.otp_is_valid(code):
                profile.email_verified = True
                profile.otp_code = None
                profile.save()

                user = profile.user
                user.is_active = True
                user.save()

                del request.session["pending_user_id"]
                
                auth_login(request, user)
                messages.success(request, f"Welcome, {user.username}! Your email has been verified.")
                return redirect("home")
            else:
                messages.error(request, "Invalid or expired code. Please try again.")
    else:
        form = OTPForm()
        
    return render(request, "verify_otp.html", {"form": form, "email": profile.user.email})

def resend_otp_view(request):
    user_id = request.session.get("pending_user_id")
    if not user_id:
        messages.error(request, "Session expired. Please sign up again.")
        return redirect("signup")

    try:
        profile = Profile.objects.get(user__id=user_id)
        code = profile.generate_otp()

        
        send_otp_email(profile.user, code)
        
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