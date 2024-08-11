from django import forms

from accounts.validators import allowImagesValidator
from .models import Category, FoodItems 

class CategoryForm(forms.ModelForm):

    class Meta:
        model = Category
        fields = ['category_name', 'description']


class FoodItemsForm(forms.ModelForm):
    image = forms.FileField(widget=forms.FileInput(attrs={'class':'btn btn-info w-100'}), validators=[allowImagesValidator])    
    class Meta:
        model = FoodItems
        fields = ['category', 'food_title', 'description', 'price', 'image', 'is_available']        