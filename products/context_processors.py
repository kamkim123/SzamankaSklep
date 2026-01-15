from .views import get_categories_for_navbar

def navbar_categories(request):
    return {
        "categories": get_categories_for_navbar()
    }
