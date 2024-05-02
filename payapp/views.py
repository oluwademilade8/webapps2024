from django.shortcuts import render
from django.contrib.auth.models import User
from .models import Transaction
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import *
from django.views.generic.edit import CreateView
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils.decorators import method_decorator
from .models import *
from .forms import *
from .forms import *
from .utils import get_current_timestamp
import os
from django.core.wsgi import get_wsgi_application
from django.contrib import messages
from django.urls import reverse
from django.db.models import Sum
from django import forms
from django.db import transaction
import logging
from decimal import Decimal
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404

# Create your views here.

@login_required
def account(request):
    user = request.user
    sent_transactions = Transaction.objects.filter(sender=user)
    account = Account.objects.get(user=user)
    received_transactions = Transaction.objects.filter(receiver=user)
    return render(request, 'account.html', {'user': user, 'account': account, 'sent_transactions': sent_transactions, 'received_transactions': received_transactions})

@login_required
def send_money(request):
    if request.method == 'POST':
        form = TransactionForm(request.POST)
        user = request.user
        if form.is_valid():
            transaction = form.save(commit=False)
            account = Account.objects.get(user=user)
            if transaction.amount > account.total_balance:
                messages.error(request, 'Insufficient balance. Please check your balance.')
                return redirect('send_money')

            transaction.sender = request.user
            transaction.balance_after_transaction = account.total_balance - transaction.amount
            transaction.receiver = form.cleaned_data['receiver_email']
            
            if transaction.amount > 0:
                transaction.transaction_type = 'Deposit'
            elif transaction.amount < 0:
                transaction.transaction_type = 'Withdrawal'
            else:
                transaction.transaction_type = 'Transfer'
            
            transaction.save()

            account.total_balance = transaction.balance_after_transaction
            request.user.account.save()

            transaction.receiver.account.total_balance += transaction.amount
            transaction.receiver.account.save()

            messages.success(request, f'Transaction successful! Your money has been transferred. ${transaction.amount}')

            return redirect('send_money')

    else:
        form = TransactionForm()

    return render(request, 'send_money.html', {'form': form})

class DepositForm(forms.Form):
    amount = forms.DecimalField(label='Amount', min_value=0, required=True)

@method_decorator(login_required, name='dispatch')
class DepositView(View):
    template_name = 'deposit.html'

    def get(self, request):
        form = DepositForm()
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        form = DepositForm(request.POST)
        if form.is_valid():
            amount = form.cleaned_data['amount']

            if amount > 0:
                account.total_balance += amount
                request.user.account.save()

                Transaction.objects.create(
                    sender=request.user,
                    receiver=None,
                    amount=amount 
                )

                return redirect('account')

        return render(request, self.template_name, {'form': form})

logger = logging.getLogger(__name__)

class WithdrawView(View):
    template_name = 'withdraw.html'

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name)

    @transaction.atomic
    def post(self, request, *args, **kwargs):
        amount = request.POST.get('amount')

        try:
            amount = Decimal(amount)
            if amount <= 0:
                raise ValueError("Withdrawal amount must be greater than zero.")

            user = request.user
            account = Account.objects.select_for_update().get(user=user)

            if account.total_balance >= amount:
                
                account.total_balance -= amount
                account.save()

                messages.success(request, f'Withdrawal of ${amount} successful!')
                return redirect('withdraw')
            
            else:
                messages.error(request, 'Insufficient funds for withdrawal.')
        except ValueError as e:
            logger.error(f"Invalid withdrawal amount: {e}")
            messages.error(request, 'Invalid withdrawal amount. Please enter a valid positive number.')
        except Account.DoesNotExist:
            
            logger.error("User account not found.")
            messages.error(request, 'User account not found. Please contact support.')
        except Exception as e:
            
            logger.exception("An unexpected error occurred during withdrawal.")
            messages.error(request, 'An unexpected error occurred. Please try again later.')

        return render(request, self.template_name, {'messages': messages.get_messages(request)})

class ProfileView(LoginRequiredMixin, View):
    template_name = 'account.html'

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name)


@login_required
def initiate_payment_request(request):
    if request.method == 'POST':
        form = PaymentRequestForm(request.POST)
        if form.is_valid():
            payment_request = form.save(commit=False)
            payment_request.requester = request.user
            payment_request.save()
            messages.success(request, 'Payment request created successfully.')
            return redirect('initiate_payment_request')
        else:
            messages.error(request, 'Invalid form data. Please correct the errors.')
    else:
        form = PaymentRequestForm()

    current_timestamp = get_current_timestamp()
    print(f"The current timestamp is: {current_timestamp}")

    return render(request, 'request_money.html', {'form': form})

@login_required
def view_requests(request):
    payment_requests = PaymentRequest.objects.filter(recipient=request.user).order_by('-id')
    return render(request, 'view_request.html', {'payment_requests': payment_requests})

@login_required
def accept_payment_request(request, request_id):
    print("Id is", request_id)
    payment_request = get_object_or_404(PaymentRequest, id=request_id)
    print(payment_request)
    print(payment_request.requester)
    print(payment_request.recipient)
    requester = Account.objects.get(user=payment_request.requester)
    recipient = Account.objects.get(user=payment_request.recipient)
    if not payment_request.is_accepted:
        if payment_request.amount > recipient.total_balance:
            messages.error(request, 'Insufficient balance. Please check your balance.')
            return redirect('view_requests')

        payment_request.is_accepted = True
        payment_request.save()

        recipient.total_balance -= payment_request.amount
        recipient.save()
        print(requester)
        requester.total_balance += payment_request.amount
        requester.save()

        payment_request.delete()

        messages.success(request, 'Payment request accepted successfully.')
    else:
        payment_request.delete()
        messages.error(request, 'Payment request has already been accepted.')

    current_timestamp = get_current_timestamp()
    print(f"The current timestamp is: {current_timestamp}")

    return redirect('view_requests')
@login_required
def decline_payment_request(request, request_id):
    payment_request = get_object_or_404(PaymentRequest, id=request_id)

    if payment_request.is_accepted:
        messages.error(request, 'Cannot decline an already accepted payment request.')
    else:
        payment_request.delete()
        messages.success(request, 'Payment request declined successfully.')

    return redirect('view_requests')



# def transaction_history(request):
#     if request.user.is_authenticated:
#         transactions = Transaction.objects.filter(sender=request.user)
#         return render(request, 'transaction_history.html', {'transactions': transactions})
#     else:
#         pass


@login_required
def transaction_history(request):
    user = request.user
    sent_transactions = Transaction.objects.filter(sender=user)
    received_transactions = Transaction.objects.filter(receiver=user)
    transactions = sent_transactions | received_transactions
    return render(request, 'transaction_history.html', {'transactions': transactions})


from decimal import Decimal
def convert_currency(request):
    if request.method == 'POST':
        new_currency = request.POST.get('new_currency')
        user = request.user

        # Conversion rates
        GBP_to_USD_rate = Decimal('1.25')
        GBP_to_EUR_rate = Decimal('1.17')
        USD_to_EUR_rate = Decimal('0.93')

        # Get user's account
        account = Account.objects.get(user=user)
        initial_amount = account.total_balance
        old_currency = user.currency

        # Perform currency conversion
        if new_currency == old_currency:
            converted_amount = initial_amount
        elif old_currency == 'GBP(£)':
            if new_currency == 'USD($)':
                converted_amount = initial_amount * GBP_to_USD_rate
            elif new_currency == 'EUR(€)':
                converted_amount = initial_amount * GBP_to_EUR_rate
        elif old_currency == 'USD($)':
            if new_currency == 'GBP(£)':
                converted_amount = initial_amount / GBP_to_USD_rate
            elif new_currency == 'EUR(€)':
                converted_amount = initial_amount * USD_to_EUR_rate
        elif old_currency == 'EUR(€)':
            if new_currency == 'USD($)':
                converted_amount = initial_amount / USD_to_EUR_rate
            elif new_currency == 'GBP(£)':
                converted_amount = initial_amount / GBP_to_EUR_rate
        else:
            messages.error(request, 'Unsupported currency selected.')
            return redirect('convert_currency')

        # Update user's account and currency
        account.total_balance = converted_amount
        account.save()
        user.currency = new_currency
        user.save()

        messages.success(request, 'Currency conversion successful.')
        return redirect('account')

    else:
        user = request.user
        return render(request, 'convert_currency.html', {'user': user})



