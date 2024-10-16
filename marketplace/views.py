from django.shortcuts import render, get_object_or_404, redirect
from .models import Cart
from menu.models import Category, FoodItems
from vendor.models import Vendor
from django.db.models import Prefetch
from django.http.response import HttpResponse, JsonResponse
from .context_processors import get_cart_amount, get_cart_counter
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.contrib.gis.geos import GEOSGeometry
from django.contrib.gis.measure import D
from django.contrib.gis.db.models.functions import Distance

# Create your views here.
def marketplace(request):
    vendors = Vendor.objects.filter(is_approved=True, user__is_active=True)
    vendor_count = vendors.count()
    context = {
        'vendors': vendors,
        'vendor_count': vendor_count
    }
    return render(request, 'marketplace/listings.html', context)


def vendor_details(request, vendor_slug):
    vendor = get_object_or_404(Vendor, vendor_slug=vendor_slug)
    categories = Category.objects.filter(vendor=vendor).prefetch_related(
        Prefetch(
            'fooditems',
            queryset=FoodItems.objects.filter(is_available=True),
        )
    )
    if request.user.is_authenticated:
        cart_items = Cart.objects.filter(user=request.user)
    else:
        cart_items = None
    context = {
        'vendor': vendor,
        'categories': categories,
        'cart_items': cart_items,
    }
    return render(request, 'marketplace/vendor_details.html', context)


def add_to_cart(request, food_id):
    if request.user.is_authenticated:
        if request.headers.get('x-requested-with') == "XMLHttpRequest":
            # check if the food item exists
            try:
                fooditem = FoodItems.objects.get(id=food_id)

                # check if the user has already added that food to the cart
                try:
                    chkCart = Cart.objects.get(user=request.user, fooditem=fooditem)
                    # Increase the food item quantity
                    chkCart.quantity += 1
                    chkCart.save()
                    return JsonResponse({'status': 'Success', 'message': 'Increased the quantity successfully.', 'cart_counter': get_cart_counter(request), 'qty': chkCart.quantity, 'cart_amount': get_cart_amount(request)})
                except:
                    chkCart = Cart.objects.create(user=request.user, fooditem=fooditem, quantity=1)
                    return JsonResponse({'status': 'Success', 'message': 'Added to cart successfully.', 'cart_counter': get_cart_counter(request), 'qty': chkCart.quantity, 'cart_amount': get_cart_amount(request)})
            except:
                return JsonResponse({'status':'Failed', 'message':'This fooditem does not exist!'})
        else:
            return JsonResponse({'status':'Failed', 'message':'Invalid Request'})
    else:
        return JsonResponse({'status':'login_required', 'message':'Please login to continue'})
        

def decrease_cart(request, food_id):
    # return HttpResponse(food_id)
    # return JsonResponse({'status':'Failed', 'message':'Please login to continue'})
    if request.user.is_authenticated:
        if request.headers.get('x-requested-with') == "XMLHttpRequest":
            # check if the food item exists
            try:
                fooditem = FoodItems.objects.get(id=food_id)

                # check if the user has already added that food to the cart
                try:
                    chkCart = Cart.objects.get(user=request.user, fooditem=fooditem)
                    # decrease the food item quantity
                    if chkCart.quantity > 1:
                        chkCart.quantity -= 1
                        chkCart.save()
                    else:
                        chkCart.delete() 
                        chkCart.quantity = 0
                    return JsonResponse({'status': 'Success', 'cart_counter': get_cart_counter(request), 'qty': chkCart.quantity, 'cart_amount': get_cart_amount(request)})
                except:
                    return JsonResponse({'status': 'Failed', 'message': 'You don not have this item in your cart'})
            except:
                return JsonResponse({'status':'Failed', 'message':'This fooditem does not exist!'})
        else:
            return JsonResponse({'status':'Failed', 'message':'Invalid Request'})
    else:
        return JsonResponse({'status':'login_required', 'message':'Please login to continue'})

@login_required(login_url='login')
def cart(request):
    cart_items = Cart.objects.filter(user=request.user).order_by('created_at')
    context = {
        'cart_items': cart_items,
    }
    return render(request, 'marketplace/cart.html', context)


def delete_cart(request, cart_id):
    if request.user.is_authenticated:
        if request.headers.get('x-requested-with') == "XMLHttpRequest":
            try:
                # check cart item exists
                cart_item = Cart.objects.get(user=request.user, id=cart_id)
                if cart_item:
                    cart_item.delete()
                    return JsonResponse({'status': 'Success', 'message': 'Cart item deleted' ,'cart_counter': get_cart_counter(request), 'cart_amount': get_cart_amount(request)})
            except:
                return JsonResponse({'status': 'Failed', 'message': 'This cart item does not exist!'})
        else:
            return JsonResponse({'status':'Failed', 'message':'Invalid Request'})


def search(request):
    if not 'address' in request.GET:
        return redirect('marketplace') 
    else:
        address = request.GET['address']
        latitude = request.GET['lat']
        longitude = request.GET['lng']
        radius = request.GET['radius']
        keyword = request.GET['keyword']

        # get the ids of the vendors which has food the user is searching
        fetch_vendor_by_fooditems = FoodItems.objects.filter(food_title__icontains=keyword, is_available=True).values_list('vendor', flat=True)

        vendors = Vendor.objects.filter(Q(id__in=fetch_vendor_by_fooditems) | Q(vendor_name__icontains=keyword, is_approved=True, user__is_active=True))

        if latitude and longitude and radius:
            pnt = GEOSGeometry('POINT(%s %s)' % (longitude, latitude))

        vendors = Vendor.objects.filter(Q(id__in=fetch_vendor_by_fooditems) | Q(vendor_name__icontains=keyword, is_approved=True, user__is_active=True),
                                        user_profile__location__distance_lte=(pnt, D(km=radius))).annotate(distance=Distance("user_profile__location", pnt)
                                                                                                        ).order_by("distance")
        for v in vendors:
            v.kms = round(v.distance.km, 1)
        
        vendors_count = vendors.count()
        context = {
            'vendors': vendors,
            'vendors_count': vendors_count,
            'source_location': address,
        }

        return render(request, 'marketplace/listings.html', context)