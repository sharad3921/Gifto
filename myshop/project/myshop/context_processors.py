from django.conf import settings

def wishlist_count(request):
    """Provide `wishlist_count` for templates (number of items in user's wishlist)."""
    try:
        if request.user.is_authenticated:
            from shop.models import Wishlist
            count = Wishlist.objects.filter(user=request.user).count()
        else:
            count = 0
    except Exception:
        count = 0
    return { 'wishlist_count': count }
