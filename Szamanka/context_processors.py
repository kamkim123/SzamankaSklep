# core/context_processors.py  (albo inna Twoja appka „core”/„common”)
from django.db.models import Count
from products.models import Product

def categories_ctx(request):
    categories = (
        Product.objects
        .values('product_type')
        .annotate(count=Count('id'))
        .order_by('product_type')
    )
    selected = request.GET.get('type', '')
    return {'categories': categories, 'selected': selected}


