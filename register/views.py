from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout as auth_logout
from django.contrib.auth import *
from payapp.models import *
from payapp.forms import *
import os
from django.core.wsgi import get_wsgi_application
from django.contrib import messages
application = get_wsgi_application()
from django.contrib.auth import login
from decimal import Decimal



def home_page(request):
    return render(request, 'home_page.html')


def signup(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            currency = form.cleaned_data['currency']

            baseline_amount_gbp = Decimal('1000')
            GBP_to_USD_rate = Decimal('1.25')
            GBP_to_EUR_rate = Decimal('1.17')
            USD_to_EUR_rate = Decimal('0.93')

            if currency == 'GBP(£)':
                initial_amount = baseline_amount_gbp
            elif currency == 'USD($)':
                initial_amount = baseline_amount_gbp * GBP_to_USD_rate
            elif currency == 'EUR(€)':
                initial_amount = baseline_amount_gbp * GBP_to_EUR_rate
            else:
                messages.error(request, 'Incorrect currency selected')
                return redirect('signup')

            user.save()  # Save the user

            # Create a new account with the user identifier
            account = Account.objects.create(user=user.username, total_balance=initial_amount)

            # Optionally, you can associate the account with the user
            # user.account = account
            # user.save()

            # Log in the user
            login(request, user)

            messages.success(request, 'Registration successful. You are now logged in.')
            return redirect('login')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field.capitalize()}: {error}")
    else:
        form = CustomUserCreationForm()

    return render(request, 'signup.html', {'form': form})

# import threading
# import time
# import sys
# sys.path.append('gen-py')

# from thrift.transport import TSocket
# from thrift.transport import TTransport
# from thrift.protocol import TBinaryProtocol
# from thrift.server import TServer

# import importlib.util
# spec = importlib.util.spec_from_file_location("TimestampService", "gen-py/TimestampService.py")
# TimestampService = importlib.util.module_from_spec(spec)
# spec.loader.exec_module(TimestampService)


# class TimestampHandler:
#     def getCurrentTimestamp(self):
#         return time.ctime()


# def run_thrift_server():
#     handler = TimestampHandler()
#     processor = getattr(TimestampService, "TimestampService").Processor(handler)
#     transport = TSocket.TServerSocket('localhost', 10000)
#     tfactory = TTransport.TBufferedTransportFactory()
#     pfactory = TBinaryProtocol.TBinaryProtocolFactory()

#     server = TServer.TThreadPoolServer(processor, transport, tfactory, pfactory)
#     print("Starting Thrift server...")
#     server.serve()


# def start_thrift_server():
#     thread = threading.Thread(target=run_thrift_server)
#     thread.daemon = True
#     thread.start()



def logout(request):
    auth_logout(request)
    return redirect('/')