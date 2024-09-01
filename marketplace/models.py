from django.db import models
from accounts.models import User
from menu.models import FoodItems

# Create your models here.
class Cart(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    fooditem = models.ForeignKey(FoodItems, on_delete=models.CASCADE)
    quantity = models.PositiveBigIntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateField(auto_now=True)
    
    def __unicode__(self):
        return self.user