from django.contrib.sitemaps import Sitemap
from django.urls import reverse
from .models import Product  # <- dopasuj nazwę modelu jeśli inna


class StaticViewSitemap(Sitemap):
    priority = 0.6
    changefreq = "monthly"

    def items(self):
        return ["home", "products:produkty", "products:regulamin", "products:private"]

    def location(self, item):
        return reverse(item)


class ProductDetailSitemap(Sitemap):
    priority = 0.8
    changefreq = "weekly"

    def items(self):
        return Product.objects.all()

    def location(self, obj):
        return reverse("products:detail", args=[obj.pk])

    # opcjonalnie, jeśli masz pole updated_at / updated / modified:
    # def lastmod(self, obj):
    #     return obj.updated_at
