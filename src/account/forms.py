from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import authenticate
from django.conf import settings
from account.models import Account
User = settings.AUTH_USER_MODEL


class RegistrationForm(UserCreationForm):
    email = forms.EmailField(max_length=255, help_text="Required. Add a valid email address")

    class Meta:
        model = Account
        fields = ('email', 'username', 'password1', 'password2', )

    def clean_email(self):
        email = self.cleaned_data['email'].lower()
        try:
            account = Account.objects.get(email=email)
        except Account.DoesNotExist:
            return email
        raise forms.ValidationError(f"{email} is already in use")

    def clean_username(self):
        username = self.cleaned_data['username']
        try:
            account = Account.objects.get(username=username)
        except Account.DoesNotExist:
            return username
        raise forms.ValidationError(f"{username} is already in use")


class AccountAuthenticationForm(forms.ModelForm):
    password = forms.CharField(label="Password", widget=forms.PasswordInput)

    class Meta:
        model = Account
        fields = ("email", "password")

    def clean(self):
        if self.is_valid():
            email = self.cleaned_data['email']
            password = self.cleaned_data['password']
            if not authenticate(email=email, password=password):
                raise forms.ValidationError('Invalid Login details')


class AccountUpdateForm(forms.ModelForm):
    class Meta:
        model = Account
        fields = ('username', 'email', 'profile_image', 'hide_email', 'bio', 'link')

    def save(self, commit=True):
        account = super(AccountUpdateForm, self).save(commit=False)
        account.username = self.cleaned_data['username']
        account.email = self.cleaned_data['email'].lower()
        account.profile_image = self.cleaned_data['profile_image']
        account.hide_email = self.cleaned_data['hide_email']
        account.link = self.cleaned_data['link']
        account.bio = self.cleaned_data['bio']
        if commit:
            account.save()
        return account
















