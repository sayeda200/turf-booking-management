from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from datetime import date
from django.shortcuts import render
from httpx import request

import booking
from .models import Slot
import random
from .models import Payment, Booking, Slot

from .models import Turf, Slot, Booking
from .forms import RegisterForm


# 🟢 REGISTER
def register(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('/login/')
    else:
        form = RegisterForm()

    return render(request, 'register.html', {'form': form})


# 🟢 LOGIN
def user_login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']

        user = authenticate(request, username=username, password=password)

        if user:
            login(request, user)
            return redirect('/')
        else:
            return render(request, 'login.html', {'error': 'Invalid credentials'})

    return render(request, 'login.html')


# 🟢 LOGOUT
def user_logout(request):
    logout(request)
    return redirect('/login/')


# 🟢 TURF LIST (SEARCH + DASHBOARD)
@login_required
def turf_list(request):
    turfs = Turf.objects.all()
    return render(request, 'turf_list.html', {'turfs': turfs})
# 🟢 SLOTS
@login_required
def turf_slots(request, turf_id):
    turf = Turf.objects.get(id=turf_id)
    slots = Slot.objects.filter(turf=turf)

    return render(request, 'slots.html', {
        'turf': turf,
        'slots': slots
    })


# 🟢 BOOK SLOT
from datetime import date

@login_required
def book_slot(request, slot_id):
    slot = Slot.objects.get(id=slot_id)

    # ❌ BLOCK PAST DATE
    if slot.date < date.today():
        messages.error(request, "⚠️ Cannot book past dates!")
        return redirect('/')

    if not slot.is_booked:
        slot.is_booked = True
        slot.save()

        Booking.objects.create(
            user=request.user,
            slot=slot
        )

        messages.success(request, "Booking successful 🎉")
    else:
        messages.warning(request, "Slot already booked ❌")

    return redirect('/')

# 🟢 MY BOOKINGS (ONLY TODAY + FUTURE)
@login_required
def my_bookings(request):
    today = date.today()

    bookings = Booking.objects.filter(
        user=request.user,
        slot__date__gte=today
    ).order_by('slot__date')

    return render(request, 'my_bookings.html', {
        'bookings': bookings,
        'today': today
    })


# 🟢 CANCEL BOOKING
from .models import Payment

@login_required
def cancel_booking(request, booking_id):
    booking = Booking.objects.get(id=booking_id)

    slot = booking.slot

    # make slot available again
    slot.is_booked = False
    slot.save()

    # update payment status
    payment = Payment.objects.filter(
        slot=slot,
        user=request.user
    ).last()

    if payment:
        payment.status = "REFUNDED"
        payment.save()

    # instead of delete → mark cancelled
    booking.status = "cancelled"
    booking.save()

    messages.warning(request, "Booking cancelled & amount refunded 💸")

    return redirect('/my-bookings/')

@login_required
def payment_page(request, slot_id):
    slot = Slot.objects.get(id=slot_id)

    return render(request, 'payment.html', {
        'slot': slot
    })

@login_required
def confirm_payment(request, slot_id):
    slot = Slot.objects.get(id=slot_id)

    # ❌ prevent duplicate booking
    if slot.is_booked:
        return redirect('/')

    # 🔥 get price
    sport = slot.turf.name.lower()

    if "cricket" in sport:
        price = 1500
    elif "volley" in sport:
        price = 400
    elif "badminton" in sport:
        price = 600
    elif "football" in sport:
        price = 800
    elif "basket" in sport:
        price = 600
    elif "hockey" in sport:
        price = 400
    else:
        price = 500

    # 🔥 generate transaction id
    txn_id = "TXN" + str(random.randint(100000, 999999))

    print("✅ SAVING PAYMENT...")

    # ✅ SAVE PAYMENT (THIS WAS MISSING)
    Payment.objects.create(
        user=request.user,
        slot=slot,
        amount=price,
        transaction_id=txn_id,
        status="SUCCESS"
    )

    # ✅ mark slot booked
    slot.is_booked = True
    slot.save()

    # ✅ create booking
    Booking.objects.create(
        user=request.user,
        slot=slot
    )

    return redirect(f"/receipt/{slot.id}/")

def receipt(request, slot_id):
    slot = Slot.objects.get(id=slot_id)
    payment = Payment.objects.filter(slot=slot).last()

    return render(request, 'receipt.html', {
        'slot': slot,
        'payment': payment
    })
# ✅ SPORT CONFIG
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import Slot

# ✅ price per hour
SPORT_PRICE = {
    "cricket": 1500,
    "volleyball": 400,
    "badminton": 600,
    "football": 800,
    "basketball": 600,
    "hockey": 400,
}

# ✅ max players allowed (validation)
SPORT_LIMIT = {
    "cricket": 22,
    "volleyball": 12,
    "badminton": 4,
    "football": 22,
    "basketball": 10,
    "hockey": 22,
}

@login_required
def payment_view(request, slot_id):
    slot = Slot.objects.get(id=slot_id)

    sport_name = slot.turf.name.lower()

    # ✅ VERY STRONG MATCHING
    if "cricket" in sport_name:
        price = 1500
        max_players = 22
    elif "volley" in sport_name:
        price = 400
        max_players = 12
    elif "badminton" in sport_name:
        price = 600
        max_players = 4
    elif "football" in sport_name:
        price = 800
        max_players = 22
    elif "basket" in sport_name:
        price = 600
        max_players = 10
    elif "hockey" in sport_name:
        price = 400
        max_players = 22
    else:
        price = 500   # ✅ default fallback
        max_players = 10

    print("SPORT:", sport_name)
    print("PRICE:", price)

    return render(request, "payment.html", {
        "slot": slot,
        "price": price,
        "max_players": max_players,
    })

from .models import Payment

@login_required
def payment_history(request):
    payments = Payment.objects.filter(user=request.user).order_by('-id')

    return render(request, 'payment_history.html', {
        'payments': payments
    })

@login_required
def dashboard(request):
    from django.db.models import Sum, Count
    from django.db.models.functions import TruncDate
    from datetime import date

    total_bookings = Booking.objects.filter(user=request.user).count()

    upcoming = Booking.objects.filter(
        user=request.user,
        slot__date__gte=date.today()
    ).count()

    total_payments = Payment.objects.filter(user=request.user).count()

    total_spent = Payment.objects.filter(
        user=request.user,
        status="SUCCESS"
    ).aggregate(total=Sum('amount'))['total'] or 0

    # ✅ ADD THIS INSIDE FUNCTION
    cancelled = Booking.objects.filter(
        user=request.user,
        status='cancelled'
    ).count()

    refunded_amount = Payment.objects.filter(
        user=request.user,
        status="REFUNDED"
    ).aggregate(total=Sum('amount'))['total'] or 0

    # charts
    bookings_by_date = (
        Booking.objects
        .filter(user=request.user)
        .annotate(day=TruncDate('booked_at'))
        .values('day')
        .annotate(count=Count('id'))
        .order_by('day')
    )

    dates = [str(i['day']) for i in bookings_by_date]
    counts = [i['count'] if i['count'] > 0 else 0 for i in bookings_by_date]

    # ✅ NEW CHART DATA
    confirmed_count = Booking.objects.filter(
        user=request.user,
        status='confirmed'
    ).count()

    turf_names = ["Confirmed", "Cancelled"]
    turf_counts = [confirmed_count, cancelled]

    return render(request, "dashboard.html", {
        "total_bookings": total_bookings,
        "upcoming": upcoming,
        "total_payments": total_payments,
        "total_spent": total_spent,
        "dates": dates,
        "counts": counts,
        "turf_names": turf_names,
        "turf_counts": turf_counts,
        "cancelled": cancelled,
        "refunded_amount": refunded_amount,
    })