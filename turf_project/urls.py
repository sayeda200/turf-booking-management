from django.contrib import admin
from django.urls import path, include

from booking import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('booking.urls')),
    path('payment/<int:slot_id>/', views.payment_view),
    path('confirm-payment/<int:slot_id>/', views.confirm_payment),
    path('receipt/<int:slot_id>/', views.receipt, name='receipt'),
    path('payments/', views.payment_history, name='payments'), # ✅ THIS IS IMPORTANT
]