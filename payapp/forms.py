from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model
from .models import Transaction, CustomUser, PaymentRequest

class TransactionForm(forms.ModelForm):
    receiver_email = forms.EmailField(label='Receiver Email')

    class Meta:
        model = Transaction
        fields = ['receiver_email', 'amount']

    def clean_receiver_email(self):
        receiver_email = self.cleaned_data['receiver_email']
        User = get_user_model()
        try:
            receiver = User.objects.get(email=receiver_email)
        except User.DoesNotExist:
            raise forms.ValidationError('User with this email does not exist.')
        return receiver
    
class CustomUserCreationForm(UserCreationForm):
    currency = forms.ChoiceField(choices=CustomUser.CURRENCY_CHOICES)

    class Meta:
        model = CustomUser
        fields = ('email', 'username', 'first_name', 'last_name', 'password1', 'password2', 'currency')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        self.fields['username'].help_text = 'User with this Email already exists.'
        self.fields['password1'].help_text = ''
        self.fields['password2'].help_text = ''


class DepositForm(forms.Form):
    amount = forms.DecimalField(label='Amount', min_value=0, required=True)

class PaymentRequestForm(forms.ModelForm):
    class Meta:
        model = PaymentRequest
        fields = ['amount', 'description', 'recipient']


class CurrencyConversionForm(forms.Form):
    to_currency = forms.ChoiceField(label='To Currency', choices=CustomUser.CURRENCY_CHOICES)
