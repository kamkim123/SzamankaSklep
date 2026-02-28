from django.contrib import admin
from django.urls import path, include
from django.views.generic import TemplateView
from orders.models import Order
from products.sitemaps import StaticViewSitemap, ProductDetailSitemap
from products import views
from django.contrib.sitemaps.views import sitemap
from django.urls import path
from django.views.generic import RedirectView
from django.templatetags.static import static
from django.urls import path
from django.http import FileResponse
from django.contrib.staticfiles.storage import staticfiles_storage
from django.conf import settings
from django.conf.urls.static import static



def favicon(request):
    return FileResponse(
        staticfiles_storage.open("products/favicons/favicon.ico"),
        content_type="image/x-icon"
    )

sitemaps = {
    "static": StaticViewSitemap,
    "products": ProductDetailSitemap,
}

urlpatterns = [
    path("", views.IndexView.as_view(), name="home"),
    path("admin/", admin.site.urls),
    path("", include(("orders.urls", "orders"), namespace="orders")),
    path("u/", include(("users.urls", "users"), namespace="users")),
    path("accounts/", include("allauth.urls")),  # to dodaje ~30 endpointów allauth
    path("products/", include(("products.urls", "products"), namespace="products")),
    path("epaka/login/", views.epaka_login, name="epaka_login"),
    path("epaka/callback/", views.epaka_callback, name="epaka_callback"),
    path("epaka/profile/", views.epaka_profile_view, name="epaka_profile"),
    path("newsletter/", include(("newsletter.urls", "newsletter"), namespace="newsletter")),

    path(
        "robots.txt",
        TemplateView.as_view(template_name="robots.txt", content_type="text/plain; charset=utf-8"),
        name="robots_txt",
    ),

    path("favicon.ico", favicon),


]

urlpatterns += [
    path("sitemap.xml", sitemap, {"sitemaps": sitemaps}, name="sitemap"),

]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

