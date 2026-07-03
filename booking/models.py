from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings
from django.core.exceptions import ValidationError
from django.utils import timezone


# ================= USER =================
class User(AbstractUser):
    ROLE_CHOICES = (
        ('user', 'User'),
        ('admin', 'Admin'),
    )
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='user')

    def __str__(self):
        return self.username


# ================= TURF =================
class Turf(models.Model):
    SPORT_CHOICES = (
        ('cricket', 'Cricket'),
        ('football', 'Football'),
        ('badminton', 'Badminton'),
        ('volleyball', 'Volleyball'),
        ('basketball', 'Basketball'),
        ('hockey', 'Hockey'),
    )

    name = models.CharField(max_length=100)
    location = models.CharField(max_length=100)

    # ✅ Proper design (sport belongs to turf)
    type = models.CharField(max_length=20, choices=SPORT_CHOICES, default='cricket')

    # ✅ Admin-controlled pricing
    price = models.IntegerField(default=0)
    max_players = models.IntegerField(default=10)

    image = models.URLField(blank=True, null=True)

    def __str__(self):
        return self.name


# ================= SLOT =================
class Slot(models.Model):
    turf = models.ForeignKey(Turf, on_delete=models.CASCADE)
    date = models.DateField()
    time = models.CharField(max_length=50)
    is_booked = models.BooleanField(default=False)

    def clean(self):
        if self.date < timezone.now().date():
            raise ValidationError({
                'date': 'Past dates are not allowed.'
            })

    def __str__(self):
        return f"{self.turf.name} - {self.date} - {self.time}"


# ================= BOOKING =================
class Booking(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    slot = models.ForeignKey(Slot, on_delete=models.CASCADE)
    booked_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(
    max_length=20,
    choices=[
        ('confirmed', 'Confirmed'),
        ('cancelled', 'Cancelled'),
    ],
    default='confirmed'
)

    def __str__(self):
        return f"{self.user} booked {self.slot}"


# ================= PAYMENT =================
class Payment(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    slot = models.ForeignKey(Slot, on_delete=models.CASCADE)
    amount = models.IntegerField()
    transaction_id = models.CharField(max_length=100)

    status = models.CharField(
        max_length=20,
        choices=[
            ("SUCCESS", "Success"),
            ("REFUNDED", "Refunded")
        ],
        default="SUCCESS"
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user} - {self.transaction_id}"