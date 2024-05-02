from django.urls import path
from payapp.views import *
from .views import *
from django.contrib.auth.views import *
# from .views import start_thrift_server

urlpatterns = [
    path('', home_page, name='home_page'),
    path('login/', LoginView.as_view(template_name='login.html'), name='login'),
    path('logout/', logout, name='logout'),
    path('signup/', signup, name='signup'),
    path('account/', account, name='account'),

    path('deposit/', DepositView.as_view(), name='deposit'),
    path('withdraw/', WithdrawView.as_view(), name='withdraw'),
    path('send_money/', send_money, name='send_money'),
    path('deposit/account/', ProfileView.as_view(), name='deposit_account'),

    path('initiate_payment_request/', initiate_payment_request, name='initiate_payment_request'),
    path('view_requests/', view_requests, name='view_requests'),
    path('accept_payment_request/<int:request_id>/', accept_payment_request, name='accept_payment_request'),
    path('decline_payment_request/<int:request_id>/', decline_payment_request, name='decline_payment_request'),
    path('transaction_history', transaction_history, name='transaction_history'),
    path('convert_currency', convert_currency, name='convert_currency'),

]
# start_thrift_server()