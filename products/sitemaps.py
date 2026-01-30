# products/sitemaps.py
from types import SimpleNamespace

from django.conf import settings
from django.contrib.sitemaps import Sitemap
from django.urls import reverse

from .models import Product


def _forced_site():
    """
    Minimalny obiekt 'site' z polem .domain, bez django.contrib.sites.
    Dzięki temu sitemap zawsze buduje URL-e na jednej domenie (np. www).
    """
    domain = getattr(settings, "SITE_DOMAIN", "www.szamankasklep.pl")
    domain = domain.replace("https://", "").replace("http://", "").strip("/")
    return SimpleNamespace(domain=domain, name=domain)


class StaticViewSitemap(Sitemap):
    protocol = "https"
    changefreq = "monthly"
    priority = 0.6

    def items(self):
        # UWAGA: "products:produkty" u Ciebie zwraca /products/products/
        # (bo masz dwa razy name="produkty" i wygrywa ostatni wpis w urls.py)
        return ["home", "products:produkty", "products:regulamin", "products:private"]

    def location(self, item):
        return reverse(item)

    def get_urls(self, page=1, site=None, protocol=None):
        return super().get_urls(page=page, site=_forced_site(), protocol=self.protocol)


class ProductDetailSitemap(Sitemap):
    protocol = "https"
    changefreq = "weekly"
    priority = 0.8

    def items(self):
        return Product.objects.all()

    def location(self, obj):
        return reverse("products:detail", args=[obj.pk])

    # opcjonalnie (polecam): jeśli masz pole aktualizacji, podmień nazwę pola
    # def lastmod(self, obj):
    #     return obj.updated_at

    def get_urls(self, page=1, site=None, protocol=None):
        return super().get_urls(page=page, site=_forced_site(), protocol=self.protocol)
