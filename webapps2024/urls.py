from django.contrib import admin
from django.urls import path, include


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('register.urls')),
    path('account/', include('register.urls')),
    path('signup/', include('register.urls')),
    path('logout/', include('register.urls')),
    path('login/', include('register.urls')),
    path('deposit/', include('register.urls')),
    path('withdraw/', include('register.urls')),

    path('initiate_payment_request/', include('register.urls')),
    path('view_requests/', include('register.urls')),
    path('request_money/', include('register.urls')),
    path('accept_payment_request/<int:pk>/', include('register.urls')),
    path('decline_payment_request/<int:pk>/', include('register.urls')),
    path('transaction_history', include('register.urls')),
    path('convert_currency', include('register.urls')),
]
