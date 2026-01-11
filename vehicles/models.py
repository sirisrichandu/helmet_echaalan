from django.db import models

class Vehicle(models.Model):
    vehicle_number = models.CharField(max_length=15, unique=True)
    owner_name = models.CharField(max_length=100)
    owner_phone = models.CharField(max_length=15)
    owner_address = models.TextField()
    vehicle_type = models.CharField(max_length=50)

    def __str__(self):
        return self.vehicle_number
