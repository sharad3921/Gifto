from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django import forms
from .models import UserProfile, shopform, indexshop


class RegisterUserForm(UserCreationForm):
    email = forms.EmailField(widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email address'}))
    first_name = forms.CharField(max_length=50, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'First name'}))
    last_name = forms.CharField(max_length=50, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Last name'}))

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'password1', 'password2')

    def __init__(self, *args, **kwargs):
        super(RegisterUserForm, self).__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'
            if field_name == 'username':
                field.widget.attrs['placeholder'] = 'Choose a username'
            elif field_name == 'password1':
                field.widget.attrs['placeholder'] = 'Create a password'
            elif field_name == 'password2':
                field.widget.attrs['placeholder'] = 'Confirm your password'


class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ('fname', 'lname', 'bio', 'email', 'birthdate', 'contact', 'gender', 'address')
        widgets = {
            'fname':     forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'First name'}),
            'lname':     forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Last name'}),
            'bio':       forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Tell us about yourself'}),
            'email':     forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email'}),
            'birthdate': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'contact':   forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Phone number'}),
            'gender':    forms.Select(attrs={'class': 'form-control'}, choices=[('', 'Select gender'), ('Male', 'Male'), ('Female', 'Female'), ('Other', 'Other')]),
            'address':   forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Your address'}),
        }


class ProductForm(forms.ModelForm):
    """Form for adding/editing shopform products (appears on Shop page)."""
    class Meta:
        model = shopform
        fields = ('Name', 'Price', 'image')
        widgets = {
            'Name':  forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Product name'}),
            'Price': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. 499 or $49.99'}),
            'image': forms.ClearableFileInput(attrs={'class': 'form-control'}),
        }


class FeaturedProductForm(forms.ModelForm):
    """Form for adding/editing indexshop products (appears on Home page)."""
    class Meta:
        model = indexshop
        fields = ('Name', 'Price', 'image')
        widgets = {
            'Name':  forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Product name'}),
            'Price': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. 499 or $49.99'}),
            'image': forms.ClearableFileInput(attrs={'class': 'form-control'}),
        }