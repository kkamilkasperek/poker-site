from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

from app.models import PokerRoom


class RegisterForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ["username", "email", "password1", "password2"]

    def clean_email(self):
        email = self.cleaned_data["email"].lower()
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("Email is already in use.")
        return email

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data["email"]
        if commit:
            user.save()
        return user

class RoomForm(forms.ModelForm):
    class Meta:
        model = PokerRoom
        fields = ["name", "blinds_level", "max_players", "is_private", "password"]
        widgets = {
            "password" : forms.PasswordInput(),
            "is_private" : forms.CheckboxInput(),
        }


    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        is_private = cleaned_data.get("is_private")
        if is_private and not password:
            self.add_error("password", "Password is required for private rooms.")