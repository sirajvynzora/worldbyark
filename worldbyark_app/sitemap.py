from django.contrib.sitemaps import Sitemap
from django.urls import reverse

from .models import Blog, TourPackage, Destination


class StaticViewSitemap(Sitemap):
    protocol = "https"
    changefreq = "weekly"
    priority = 1.0

    def items(self):
        return [
            "home",
            "about",
            "packages",
            "destinations",
            "blogs",
            "gallery",
            "contact",
        ]

    def location(self, item):
        return reverse(item)


class BlogSitemap(Sitemap):
    priority = 0.8
    changefreq = "weekly"

    def items(self):
        return Blog.objects.all()

    def location(self, obj):
        return reverse("blog_detail", kwargs={"slug": obj.slug})


class TourPackageSitemap(Sitemap):
    priority = 0.9
    changefreq = "monthly"

    def items(self):
        return TourPackage.objects.all()

    def location(self, obj):
        return reverse("package_detail", kwargs={"slug": obj.slug})


class DestinationSitemap(Sitemap):
    priority = 0.7
    changefreq = "monthly"

    def items(self):
        return Destination.objects.all()

    def location(self, obj):
        return reverse("destination_detail", kwargs={"slug": obj.slug})


# Aliases for backward compatibility with project urls.py
CampingPackageSitemap = TourPackageSitemap
ActivitySitemap = DestinationSitemap
