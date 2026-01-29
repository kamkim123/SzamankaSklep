# products/sitemaps.py
from django.contrib.sitemaps import Sitemap
from django.urls import reverse
from .models import Product

class StaticViewSitemap(Sitemap):
    protocol = "https"   # <--- TU
    changefreq = "monthly"
    priority = 0.6

    def items(self):
        return ["home", "products:produkty", "products:regulamin", "products:private"]

    def location(self, item):
        return reverse(item)


class ProductDetailSitemap(Sitemap):
    protocol = "https"   # <--- I TU
    changefreq = "weekly"
    priority = 0.8

    def items(self):
        return Product.objects.all()

    def location(self, obj):
        return reverse("products:detail", args=[obj.pk])
