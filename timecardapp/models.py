from django.db import models
from django.contrib.auth.models import User

# User = settings.AUTH_USER_MODEL

class TimeCards(models.Model):
    entry_date  = models.DateField(auto_now=False, auto_now_add=False)
    time_in     = models.TimeField(auto_now=False, auto_now_add=False)
    time_out    = models.TimeField(auto_now=False, auto_now_add=False)
    break_time  = models.TimeField(auto_now=False, auto_now_add=False, null=True)
    total_time  = models.TimeField(auto_now=False, auto_now_add=False, null=True)
    pay         = models.FloatField(null=True)
    user        = models.ForeignKey(User, default=1, on_delete=models.PROTECT)

    class Meta:
        ordering = ['-entry_date']


class Wages(models.Model):
    increase_date = models.DateField(auto_now=False, auto_now_add=False)
    last_date = models.DateField(auto_now=False, auto_now_add=False)
    wage = models.FloatField()
    user = models.ForeignKey(User, default=1, on_delete=models.CASCADE)
    def __str__(self):
        return str(self.increase_date)
        
    class Meta:
        ordering = ['-increase_date']

class Settings(models.Model):
    break_type = models.TextField(max_length=20)
    break_duration = models.IntegerField(default=0)
    round_time = models.IntegerField(default=15)
    user = models.ForeignKey(User, default=1, on_delete=models.CASCADE)
    def __str__(self):
        return str(self.break_type)