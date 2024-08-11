from django.shortcuts import redirect, render, get_object_or_404
from accounts.forms import UserProfileForm
from accounts.models import UserProfile
from menu.forms import CategoryForm, FoodItemsForm
from menu.models import Category, FoodItems
from vendor.forms import VendorForm
from vendor.models import Vendor
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from accounts.views import chek_role_vendor
from django.template.defaultfilters import slugify


def get_vendor(request):
    vendor = Vendor.objects.get(user=request.user)
    return vendor

@login_required(login_url = 'login')
@user_passes_test(chek_role_vendor)
def vprofile(request):
    profile = get_object_or_404(UserProfile, user=request.user)
    vendor = get_object_or_404(Vendor, user=request.user)

    if request.method == 'POST':
        print("POST data:", request.POST)
        print("FILES data:", request.FILES)

        profile_form = UserProfileForm(request.POST, request.FILES, instance=profile)
        vendor_form = VendorForm(request.POST, request.FILES, instance=vendor)

        if profile_form.is_valid() and vendor_form.is_valid():
            profile_form.save()
            vendor_form.save()
            messages.success(request, "Settings updated")
            return redirect('vprofile')
        else:
            print(profile_form.errors)
            print(vendor_form.errors)
    else:
        profile_form = UserProfileForm(instance=profile)
        vendor_form = VendorForm(instance=vendor)
    
    context = {
        'profile_form': profile_form,
        'vendor_form': vendor_form,
        'profile': profile,
        'vendor': vendor,
    }
    return render(request, 'vendor/vprofile.html', context)

@login_required(login_url = 'login')
@user_passes_test(chek_role_vendor)
def menu_builder(request):
    vendor = get_vendor(request)
    categories = Category.objects.filter(vendor=vendor).order_by('created_at')
    context = {
        'categories': categories,
    }
    return render(request, 'vendor/menu_builder.html', context)
    
@login_required(login_url = 'login')
@user_passes_test(chek_role_vendor)
def fooditems_by_category(request, pk=None):
    vendor = get_vendor(request)
    category = get_object_or_404(Category, pk=pk)
    fooditems = FoodItems.objects.filter(category=category, vendor=vendor)
    # for i in fooditems:
    #     print(i.food_title)
    context = {
        'fooditems': fooditems,
        'category': category,
    }
    return render(request, 'vendor/fooditems_by_category.html', context)

@login_required(login_url = 'login')
@user_passes_test(chek_role_vendor)
def add_category(request):
    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            category_name = form.cleaned_data['category_name'] # getting values from the form
            category = form.save(commit=False)
            category.vendor = get_vendor(request)
            category.slug = slugify(category_name)

            form.save()
            messages.success(request, "Category added")
            return redirect('menu_builder')
    else:
        form = CategoryForm()
    context = {
        'form': form,
    }
    return render(request, 'vendor/add_category.html', context)

@login_required(login_url = 'login')
@user_passes_test(chek_role_vendor)
def edit_category(request, pk=None):
    category = get_object_or_404(Category, pk=pk)
    if request.method == 'POST':
        form = CategoryForm(request.POST, instance=category)
        if form.is_valid():
            category_name = form.cleaned_data['category_name'] # getting values from the form
            category = form.save(commit=False)
            category.vendor = get_vendor(request)
            category.slug = slugify(category_name)

            form.save()
            messages.success(request, "Category updated successfully!")
            return redirect('menu_builder')
    else:
        form = CategoryForm(instance=category)

        
    context = {
        'form': form,
        'category': category,
    }
    return render(request, 'vendor/edit_category.html', context)

@login_required(login_url = 'login')
@user_passes_test(chek_role_vendor)
def delete_category(request, pk=None):
    category = get_object_or_404(Category, pk=pk)
    category.delete()
    messages.success(request, "Category deleted successfully!")
    return redirect('menu_builder')

@login_required(login_url = 'login')
@user_passes_test(chek_role_vendor)
def add_food(request):
    if request.method == 'POST':
        form = FoodItemsForm(request.POST, request.FILES)
        if form.is_valid():
            foodtitle = form.cleaned_data['food_title']  # Getting values from the form
            food = form.save(commit=False)  # Create the form instance but don't save to DB yet
            food.vendor = get_vendor(request)  # Set the vendor
            food.slug = slugify(foodtitle)  # Generate slug

            food.save()  # Save the food item to the database
            messages.success(request, "Food Item added successfully")
            return redirect('fooditems_by_category', food.category.id)
    else:
        form = FoodItemsForm()  # Create an empty form instance
        # modify the form to fetch the category of current vendor
        form.fields['category'].queryset = Category.objects.filter(vendor=get_vendor(request))
    context = {
        'form': form,
    }
    return render(request, 'vendor/add_food.html', context)

@login_required(login_url = 'login')
@user_passes_test(chek_role_vendor)
def edit_food(request, pk=None):
    food = get_object_or_404(FoodItems, pk=pk)
    if request.method == 'POST':
        form = FoodItemsForm(request.POST, request.FILES, instance=food)
        if form.is_valid():
            foodtitle = form.cleaned_data['food_title']  # getting values from the form
            
            food = form.save(commit=False)
            food.vendor = get_vendor(request)
            food.slug = slugify(foodtitle)

            form.save()
            messages.success(request, "FoodItem updated successfully!")
            return redirect('fooditems_by_category', food.category.id)
        else:
            print(form.errors)
    else:
        form = FoodItemsForm(instance=food)
        form.fields['category'].queryset = Category.objects.filter(vendor=get_vendor(request))

    context = {
        'form': form,
        'food': food,
    }
    return render(request, 'vendor/edit_food.html', context)

@login_required(login_url = 'login')
@user_passes_test(chek_role_vendor)
def delete_food(request, pk=None):
    food = get_object_or_404(FoodItems, pk=pk)
    food.delete()
    messages.success(request, "FoodItem deleted successfully!")
    return redirect('fooditems_by_category', food.category.id)