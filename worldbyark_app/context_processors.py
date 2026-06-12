from __future__ import annotations
from typing import Any
from django.conf import settings
from .models import TourPackage


def google_reviews(request) -> dict[str, Any]:
    rating = getattr(settings, "GOOGLE_REVIEW_RATING", 0.0)
    count = getattr(settings, "GOOGLE_REVIEW_COUNT", 0)
    url = getattr(settings, "GOOGLE_REVIEW_URL", "")
    return {
        "google_review_rating": rating,
        "google_review_count": count,
        "google_review_url": url,
    }


def footer_packages(request) -> dict[str, Any]:
    packages = TourPackage.objects.only("name", "slug").order_by("-created_at")[:5]
    return {"footer_packages": packages}

from .models import Destination

def nav_destinations(request) -> dict[str, Any]:
    destinations = Destination.objects.only("name", "slug").order_by("name")
    return {"nav_destinations": destinations}
