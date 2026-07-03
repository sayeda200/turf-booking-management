from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),   # ✅ dashboard first

    path('turfs/', views.turf_list, name='turfs'),

    path('register/', views.register),
    path('login/', views.user_login),
    path('logout/', views.user_logout),

    path('slots/<int:turf_id>/', views.turf_slots),
    path('book/<int:slot_id>/', views.book_slot),

    path('my-bookings/', views.my_bookings),
    path('cancel/<int:booking_id>/', views.cancel_booking),

    path('payment/<int:slot_id>/', views.payment_view, name='payment'),
    path('confirm-payment/<int:slot_id>/', views.confirm_payment, name='confirm_payment'),

    path('receipt/<int:slot_id>/', views.receipt, name='receipt'),

    path('payments/', views.payment_history, name='payments'),
]