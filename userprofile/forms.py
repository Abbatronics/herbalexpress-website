from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm, SetPasswordForm
from django.contrib.auth import get_user_model
from captcha.fields import ReCaptchaField
from captcha.widgets import ReCaptchaV2Checkbox
from .models import Userprofile
from django.contrib.auth.models import User



class UserRegistrationForm(UserCreationForm): 
    email = forms.EmailField(help_text='A valid email address, please ', required=True)


    class Meta:
        model = get_user_model()
        fields = ['first_name', 'last_name', 'username', 'email', 'password1', 'password2' ]     
    
    def save(self, commit=True):
        user = super(UserRegistrationForm, self).save(commit=False)
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
            
        return user  

class UserLoginForm(AuthenticationForm):
    username = forms.CharField(label='Email or Username')
    captcha = ReCaptchaField(widget=ReCaptchaV2Checkbox())

        

class UserUpdateForm(forms.ModelForm): 
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'username', 'email']

    def __init__(self, *args, **kwargs):
        super(UserUpdateForm, self).__init__(*args, **kwargs)

        for fieldname in ['first_name', 'last_name', 'username', 'email']:
            self.fields[fieldname].help_text = None

 
class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = Userprofile
        fields = ['image']


class SetPasswordForm(SetPasswordForm):
    class Meta:
        model = get_user_model()
        fields = ['new_password1', 'new_password2']


