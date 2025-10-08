import datetime

from django.test import TestCase
from django.utils import timezone

from .models import Product


class ProductModelTests(TestCase):
    def test_was_published_recently_with_future_product(self):
        """
        was_published_recently() returns False for questions whose pub_date
        is in the future.
        """
        time = timezone.now() + datetime.timedelta(days=30)
        future_product = Product(pub_date=time)
        self.assertIs(future_product.was_published_recently(), False)