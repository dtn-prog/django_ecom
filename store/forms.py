from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model
from django.db import transaction
from django.core.exceptions import ValidationError
from store.models import Contact

User = get_user_model()

class CustomerUserCreationForm(UserCreationForm):
    username = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'Username', 'class':'form-control'}))
    first_name = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'First Name', 'class':'form-control'}))
    last_name = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'Last Name', 'class':'form-control'}))
    email = forms.EmailField(widget=forms.EmailInput(attrs={'placeholder': 'Email Address', 'class':'form-control'}))
    phone = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'Phone Number', 'class':'form-control','type':'tel'}))
    password1 = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder': 'Password', 'class':'form-control'}))
    password2 = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder': 'Retype Password', 'class':'form-control'}))
   
    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'phone', 'password1', 'password2')
        
    def clean_email(self):
        email = self.cleaned_data.get('email')
        #print(f"Checking email: {email}")  
        existing_user = User.objects.filter(email=email).first()
        if existing_user:
            #print(f"Existing user found: active={existing_user.is_active}")  
            if existing_user.is_active:
                raise ValidationError("email đã có người dùng")
        return email
           
    def clean(self):
        cleaned_data = super().clean()
        for field, errors in self.errors.items():
            print(f"Validation error in {field}: {', '.join(errors)}")
        return cleaned_data
   
    @transaction.atomic
    def save(self, commit=True):
        email = self.cleaned_data['email']
        existing_user = User.objects.filter(email=email).first()
        
        print(f"In save method: email={email}, existing_user={existing_user}") 
       
        if existing_user and not existing_user.is_active:
            print('Converting guest user to active user')
            existing_user.username = self.cleaned_data['username']
            existing_user.phone = self.cleaned_data['phone']
            existing_user.first_name = self.cleaned_data['first_name']
            existing_user.last_name = self.cleaned_data['last_name']
            existing_user.set_password(self.cleaned_data['password1'])
            existing_user.is_active = True
            if commit:
                existing_user.save()
            return existing_user
        else:
            print('Creating new user')
            return super().save(commit=commit)
        

class ContactForm(forms.ModelForm):
    full_name = forms.CharField(
        label='họ và tên',
        widget=forms.TextInput(
            attrs={'placeholder': 'Họ Và Tên',
                   'class':'form-control form-control-lg'}
            ) )

    phone = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'số điện thoại', 'class':'form-control form-control-lg','type':'tel'}))
    email = forms.EmailField(
        widget=forms.EmailInput(
            attrs={'placeholder': 'email', 
                   'class':'form-control form-control-lg'}
            ))
    message = forms.CharField(widget=forms.Textarea(attrs={'placeholder': 'nội dung', 'class':'form-control form-control-lg',}))
    
    
    class Meta:
        model = Contact
        fields = '__all__'
        