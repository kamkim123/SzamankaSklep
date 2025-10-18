
from .cart import Cart

def cart_counts(request):
    return {"cart_items": len(Cart(request))}