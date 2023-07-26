from django.db import models
from django.conf import settings
import datetime

class Category(models.Model):
    name = models.CharField(max_length=64)

    def __str__(self):
        return self.name
class Institution(models.Model):
    institution_choices = [
        (1, 'fundacja'),
        (2, 'organizacja pozarządowa'),
        (3, 'zbiórka lokalna'),
    ]
    name = models.CharField(max_length=64)
    description = models.TextField()
    type = models.IntegerField(choices=institution_choices, default=1)
    categories = models.ManyToManyField(Category)

    @classmethod
    def count_all_donated(cls):
        count = 0
        institutions = Institution.objects.all()
        for institution in institutions:
            if institution.donation.exists():
                count += 1
        return count

    def has_been_donated(self):
        if self.donation.exists():
            return True
        return False

    def __str__(self):
        return self.name


class Donation(models.Model):
    # supported =
    quantity = models.IntegerField(default=1)
    categories = models.ManyToManyField(Category)
    institution = models.ForeignKey(Institution, on_delete=models.CASCADE, related_name='donation')
    address = models.CharField()
    phone_number = models.CharField()
    city = models.CharField(max_length=64)
    zip_code = models.CharField(max_length=15)
    pick_up_date = models.DateField()
    pick_up_time = models.TimeField()
    pick_up_comment = models.TextField()
    picked_up = models.BooleanField(default=False)
    picked_up_date = models.DateField(null=True, blank=True, default='2000-01-01')
    picked_up_time = models.TimeField(null=True, blank=True, default='00:00')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True)

    # def __init__(self, *args, **kwargs):
    #     super(Donation, self).save()
    #
    # def save(self, *args, **kwargs):
    #     if not self.pk:  # object is being created, thus no primary key field yet
    #         print("before " + self.institution.supported)
    #         self.institution.supported = True
    #         self.institution.save()
    #         print("after " + self.institution.supported)
    #     super(Donation, self).save(*args, **kwargs)
    #
    # def delete(self):
    #     Donation.donations_count -= self.quantity
    #     super(Donation, self).delete()

    @classmethod
    def count_all(cls):
        count = 0
        donations = Donation.objects.all()
        for donation in donations:
            count += donation.quantity
        return count

    def __str__(self):
        return f"{self.institution} [{self.quantity}]"
