from django.db import models
from django.contrib.auth.models import User
from django.conf import settings
CustomUser = settings.AUTH_USER_MODEL
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.models import *
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils.translation import gettext_lazy as _


class Transaction(models.Model):
    TRANSACTION_TYPES = [
        ('DEPOSIT', 'Deposit'),
        ('WITHDRAWAL', 'Withdrawal'),
        ('TRANSFER', 'Transfer'),
    ]

    sender = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='sent')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    # currency = models.ForeignKey(Currency, on_delete=models.CASCADE)
    receiver = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='received', null=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    transaction_type = models.CharField(max_length=20, choices=TRANSACTION_TYPES)

    deposit_source = models.CharField(max_length=50, blank=True, null=True)
    deposit_method = models.CharField(max_length=50, blank=True, null=True)
    withdrawal_method = models.CharField(max_length=50, blank=True, null=True)

    transfer_note = models.TextField(blank=True, null=True)

    def __str__(self):
        if self.transaction_type == 'DEPOSIT':
            return f"{self.sender} deposited {self.amount}"
        elif self.transaction_type == 'WITHDRAWAL':
            return f"{self.sender} withdrew {self.amount}"
        elif self.transaction_type == 'TRANSFER':
            return f"{self.sender} transferred {self.amount} to {self.receiver.email}"
        else:
            return f"Unknown transaction type: {self.transaction_type}"
    

class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("You must enter the Email field")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superusers must have staff status enabled.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superusers must have super user status enabled.")

        return self.create_user(email, password, **extra_fields)



class CustomUser(AbstractUser):
    CURRENCY_CHOICES = [
        ('GBP(£)', 'British Pound'),
        ('USD($)', 'US Dollar'),
        ('EUR(€)', 'Euro'),
    ]
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=30, blank=True)
    last_name = models.CharField(max_length=30, blank=True)
    currency = models.CharField(max_length=15, choices=CURRENCY_CHOICES, null=True)
    date_of_birth = models.DateField(null=True, blank=True)
    total_balance = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)
    

    groups = models.ManyToManyField(Group, related_name="customuser_groups", blank=True, verbose_name=_("user group"))
    user_permissions = models.ManyToManyField(Permission, related_name="customuser_permissions", blank=True, verbose_name=_("user permission"))

    objects = CustomUserManager()

    class Meta:
        permissions = [("can_view_dashboard", "Can view dashboard")]

class CustomUserGroups(models.Model):
    customuser = models.ForeignKey("CustomUser", on_delete=models.CASCADE, related_name="user_groups")
    group = models.ForeignKey(Group, on_delete=models.CASCADE)

class CustomUserUserPermissions(models.Model):
    customuser = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='custom_user_permissions')
    permission = models.ForeignKey(Permission, on_delete=models.CASCADE)


class Account(models.Model):
    user = models.CharField(max_length=150)  # Assuming the maximum length of the user identifier
    total_balance = models.DecimalField(max_digits=10, decimal_places=2, default=1000)

    def __str__(self):
        return f"Account for {self.user}"


@receiver(post_save, sender=CustomUser)
def create_account_for_new_user(sender, instance, created, **kwargs):
    if created:
        Account.objects.create(user=instance)


class PaymentRequest(models.Model):
    requester = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='payment_sent')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    recipient = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='payment_received')
    description = models.CharField(max_length=100)
    is_accepted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Payment Request from {self.requester.username} to {self.recipient.username}"


