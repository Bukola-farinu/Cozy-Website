from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import AuthenticationForm

class SignUpForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput, label="Password")
    confirm_password = forms.CharField(widget=forms.PasswordInput, label="Confirm Password")

    class Meta:
        model = User
        fields = ["username", "email"]

    def clean_email(self):
        email = self.cleaned_data.get("email")
        existing = User.objects.filter(email=email).first()
        if existing:
            if existing.profile.email_verified:
                raise forms.ValidationError("An account with this email already exists.")
            else:
                # Unverified leftover — remove it so the user can retry
                existing.delete()
        return email

    def clean_username(self):
        username = self.cleaned_data.get("username")
        existing = User.objects.filter(username=username).first()
        if existing:
            if existing.profile.email_verified:
                raise forms.ValidationError("This username is already taken.")
            else:
                existing.delete()
        return username
    
    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")
        if password and confirm_password and password != confirm_password:
            raise forms.ValidationError("Passwords do not match.")
        return cleaned_data

class OTPForm(forms.Form):
    otp_code = forms.CharField(
        max_length=6,
        min_length=6,
        label="Verification Code",
        widget=forms.TextInput(attrs={"placeholder": "6-digit code", "autocomplete": "off"})
    )

class LoginForm(AuthenticationForm):
    username = forms.CharField(label="Username")
    password = forms.CharField(widget=forms.PasswordInput, label="Password")