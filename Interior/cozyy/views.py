from django.shortcuts import render, redirect
from django.core.mail import send_mail
from django.conf import settings

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