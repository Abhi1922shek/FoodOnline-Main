from .models import Cart
from menu.models import FoodItems


def get_cart_counter(request):
    cart_count = 0
    if request.user.is_authenticated:
        try:
            cart_items = Cart.objects.filter(user=request.user)
            if cart_items:
                for cart_item in cart_items:
                    cart_count += cart_item.quantity
        except:
            cart_count = 0
    # Ensure that the function always returns a dictionary
    return {'cart_count': cart_count}


def get_cart_amount(request):
    subtotal = 0
    tax = 0
    total = 0
    if request.user.is_authenticated:
        cart_items = Cart.objects.filter(user=request.user)
        for item in cart_items:
            fooditem = FoodItems.objects.get(pk=item.fooditem.id)
            subtotal += (fooditem.price * item.quantity)
        total = subtotal + tax
    return dict(subtotal=subtotal, tax=tax, total=total)
