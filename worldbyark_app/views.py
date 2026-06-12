from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models.functions import Lower
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from dateutil.relativedelta import relativedelta

from .forms import BlogForm, ContactForm, TestimonialForm, GalleryImageForm, CategoryForm, TourPackageForm, DestinationForm
from .models import Blog, Category, ContactMessage, GalleryImage, Testimonial, TourPackage, Destination


# ==========================================
# FRONTEND VIEWS
# ==========================================

def home(request):
    packages = TourPackage.objects.all().order_by("-created_at")[:6]
    testimonials = Testimonial.objects.all()[:8]
    destinations = Destination.objects.all().order_by("-created_at")[:8]
    latest_blogs = Blog.objects.all().order_by("-created_at")[:6]
    return render(request, 'frontend/index.html', {
        "packages": packages,
        "testimonials": testimonials,
        "destinations": destinations,
        "latest_blogs": latest_blogs,
    })


def about(request):
    testimonials = Testimonial.objects.all()[:8]
    destinations = Destination.objects.all().order_by("-created_at")[:8]
    return render(request, 'frontend/about.html', {
        "testimonials": testimonials,
        "destinations": destinations,
    })


def packages(request):
    packages_qs = TourPackage.objects.all().order_by("-created_at")
    paginator = Paginator(packages_qs, 9)
    page_number = request.GET.get("page")
    packages_page = paginator.get_page(page_number)
    return render(request, 'frontend/packages.html', {"packages": packages_page})


def package_detail(request, slug):
    package = get_object_or_404(TourPackage, slug=slug)
    related_packages = TourPackage.objects.exclude(slug=slug).order_by("-created_at")[:4]
    return render(request, 'frontend/package-detail.html', {
        "package": package,
        "related_packages": related_packages,
    })


def destinations(request):
    destinations_qs = Destination.objects.all().order_by("-created_at")
    paginator = Paginator(destinations_qs, 9)
    page_number = request.GET.get("page")
    destinations_page = paginator.get_page(page_number)
    packages_qs = TourPackage.objects.all().order_by("-created_at")[:8]
    return render(request, 'frontend/destinations.html', {
        "destinations": destinations_page,
        "packages": packages_qs,
    })


def destination_detail(request, slug):
    destination = get_object_or_404(Destination, slug=slug)
    related_destinations = Destination.objects.exclude(slug=slug).order_by("-created_at")[:4]
    return render(request, 'frontend/destination-detail.html', {
        "destination": destination,
        "related_destinations": related_destinations,
    })


def blogs(request):
    blogs_qs = Blog.objects.all().order_by("-created_at")
    paginator = Paginator(blogs_qs, 9)
    page_number = request.GET.get("page")
    blogs_page = paginator.get_page(page_number)
    return render(request, 'frontend/blogs.html', {
        "blogs": blogs_page,
        "recent_blogs": Blog.objects.order_by("-created_at")[:3],
        "latest_blogs": Blog.objects.order_by("-created_at")[:6],
    })


def blog_detail(request, slug):
    blog = get_object_or_404(Blog, slug=slug)
    recent_blogs = Blog.objects.exclude(slug=slug).order_by("-created_at")[:4]
    return render(request, 'frontend/blog-detail.html', {
        "blog": blog,
        "recent_blogs": recent_blogs,
    })


def gallery(request):
    categories = Category.objects.prefetch_related("images").all()
    all_images = GalleryImage.objects.all().order_by("-uploaded_at")
    return render(request, 'frontend/gallery.html', {
        "categories": categories,
        "all_images": all_images,
    })


def contact(request):
    if request.method == "POST":
        form = ContactForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Your message has been sent. We will get back to you soon.")
            return redirect("contact")
        messages.error(request, "Please check the form and try again.")
    else:
        form = ContactForm()
    return render(request, 'frontend/contact.html', {"form": form})


def page_not_found(request, exception):
    return render(request, 'frontend/404.html', status=404)


# ==========================================
# ADMIN AUTH
# ==========================================

def admin_login(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        if not username or not password:
            messages.error(request, "Both fields are required.")
            return render(request, "authenticate/login.html")
        user = authenticate(request, username=username, password=password)
        if user is not None and user.is_staff:
            login(request, user)
            messages.success(request, f"Welcome back, {user.username}!")
            return redirect("admin_dashboard")
        messages.error(request, "Invalid credentials or unauthorized access.")
    return render(request, "authenticate/login.html")


@login_required(login_url="admin_login")
def admin_logout(request):
    logout(request)
    messages.success(request, "You have been logged out.")
    return redirect("admin_login")


# ==========================================
# ADMIN DASHBOARD
# ==========================================

@login_required(login_url="admin_login")
def admin_dashboard(request):
    now = timezone.now()
    month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

    stats = {
        'total_blogs': Blog.objects.count(),
        'blogs_this_month': Blog.objects.filter(created_at__gte=month_start).count(),
        'total_packages': TourPackage.objects.count(),
        'total_destinations': Destination.objects.count(),
        'total_contacts': ContactMessage.objects.count(),
        'total_gallery': GalleryImage.objects.count(),
    }

    recent_blogs = Blog.objects.all().order_by('-created_at')[:4]
    recent_contacts = ContactMessage.objects.all().order_by('-created_at')[:4]
    recent_packages = TourPackage.objects.all().order_by('-created_at')[:4]
    recent_destinations = Destination.objects.all().order_by('-created_at')[:4]

    month_labels = []
    blogs_counts = []
    contacts_counts = []

    for i in range(5, -1, -1):
        target_month = now - relativedelta(months=i)
        month_labels.append(target_month.strftime('%b'))
        blogs_counts.append(Blog.objects.filter(
            created_at__year=target_month.year,
            created_at__month=target_month.month
        ).count())
        contacts_counts.append(ContactMessage.objects.filter(
            created_at__year=target_month.year,
            created_at__month=target_month.month
        ).count())

    service_labels = []
    service_counts = []
    for category in Category.objects.all()[:6]:
        service_labels.append(category.name)
        service_counts.append(category.images.count())
    if not service_labels:
        service_labels = ['No Data']
        service_counts = [1]

    return render(request, "admin_pages/dashboard.html", {
        'stats': stats,
        'recent_blogs': recent_blogs,
        'recent_contacts': recent_contacts,
        'recent_packages': recent_packages,
        'recent_destinations': recent_destinations,
        'month_labels': month_labels,
        'blogs_counts': blogs_counts,
        'contacts_counts': contacts_counts,
        'service_labels': service_labels,
        'service_counts': service_counts,
    })


# ==========================================
# BLOGS (ADMIN)
# ==========================================

@login_required(login_url="admin_login")
def admin_blog_list(request):
    blogs_qs = Blog.objects.all().order_by("-created_at")
    paginator = Paginator(blogs_qs, 6)
    blogs = paginator.get_page(request.GET.get("page"))
    return render(request, "admin_pages/blog_list.html", {"blogs": blogs})


@login_required(login_url="admin_login")
def blog_create(request):
    form = BlogForm(request.POST or None, request.FILES or None)
    if form.is_valid():
        form.save()
        messages.success(request, "Blog post created!")
        return redirect("admin_blog_list")
    return render(request, "admin_pages/create_blog.html", {"form": form})


@login_required(login_url="admin_login")
def blog_update(request, pk):
    blog = get_object_or_404(Blog, pk=pk)
    form = BlogForm(request.POST or None, request.FILES or None, instance=blog)
    if form.is_valid():
        form.save()
        messages.success(request, "Blog updated!")
        return redirect("admin_blog_list")
    return render(request, "admin_pages/create_blog.html", {"form": form, "blog": blog})


@login_required(login_url="admin_login")
def blog_delete(request, pk):
    blog = get_object_or_404(Blog, pk=pk)
    if request.method == "POST":
        blog.delete()
        messages.success(request, "Blog deleted!")
    return redirect("admin_blog_list")


# ==========================================
# TOUR PACKAGES (ADMIN)
# ==========================================

@login_required(login_url="admin_login")
def admin_package_list(request):
    packages_qs = TourPackage.objects.all().order_by("-created_at")
    packages = Paginator(packages_qs, 10).get_page(request.GET.get("page"))
    return render(request, "admin_pages/package_list.html", {"packages": packages})


@login_required(login_url="admin_login")
def package_create(request):
    form = TourPackageForm(request.POST or None, request.FILES or None)
    if form.is_valid():
        form.save()
        messages.success(request, "Tour Package created successfully!")
        return redirect("admin_package_list")
    return render(request, "admin_pages/create_package.html", {"form": form})


@login_required(login_url="admin_login")
def package_update(request, pk):
    package = get_object_or_404(TourPackage, pk=pk)
    form = TourPackageForm(request.POST or None, request.FILES or None, instance=package)
    if form.is_valid():
        form.save()
        messages.success(request, "Tour Package updated successfully!")
        return redirect("admin_package_list")
    return render(request, "admin_pages/create_package.html", {"form": form, "package": package})


@login_required(login_url="admin_login")
def package_delete(request, pk):
    package = get_object_or_404(TourPackage, pk=pk)
    if request.method == "POST":
        package.delete()
        messages.success(request, "Tour Package deleted successfully!")
    return redirect("admin_package_list")


# ==========================================
# DESTINATIONS (ADMIN)
# ==========================================

@login_required(login_url="admin_login")
def admin_destination_list(request):
    destinations_qs = Destination.objects.all().order_by("-created_at")
    destinations = Paginator(destinations_qs, 10).get_page(request.GET.get("page"))
    return render(request, "admin_pages/destination_list.html", {"destinations": destinations})


@login_required(login_url="admin_login")
def destination_create(request):
    form = DestinationForm(request.POST or None, request.FILES or None)
    if form.is_valid():
        form.save()
        messages.success(request, "Destination created successfully!")
        return redirect("admin_destination_list")
    return render(request, "admin_pages/create_destination.html", {"form": form})


@login_required(login_url="admin_login")
def destination_update(request, pk):
    destination = get_object_or_404(Destination, pk=pk)
    form = DestinationForm(request.POST or None, request.FILES or None, instance=destination)
    if form.is_valid():
        form.save()
        messages.success(request, "Destination updated successfully!")
        return redirect("admin_destination_list")
    return render(request, "admin_pages/create_destination.html", {"form": form, "destination": destination})


@login_required(login_url="admin_login")
def destination_delete(request, pk):
    destination = get_object_or_404(Destination, pk=pk)
    if request.method == "POST":
        destination.delete()
        messages.success(request, "Destination deleted successfully!")
    return redirect("admin_destination_list")


# ==========================================
# GALLERY (ADMIN)
# ==========================================

@login_required(login_url="admin_login")
def gallery_images(request):
    categories = Category.objects.all().prefetch_related("images")
    category_pages = {}
    for category in categories:
        images_qs = category.images.all().order_by("-uploaded_at")
        paginator = Paginator(images_qs, 8)
        page_number = request.GET.get(f"page_{category.id}", 1)
        try:
            page_obj = paginator.page(page_number)
        except PageNotAnInteger:
            page_obj = paginator.page(1)
        except EmptyPage:
            page_obj = paginator.page(paginator.num_pages)
        category_pages[category.id] = page_obj

    return render(
        request, "admin_pages/image_list.html",
        {"categories": categories, "category_pages": category_pages},
    )


@login_required(login_url="admin_login")
def add_image(request):
    categories = Category.objects.all()
    if request.method == "POST":
        category_id = request.POST.get("category")
        category = Category.objects.get(id=category_id)
        files = request.FILES.getlist("images")
        for file in files:
            GalleryImage.objects.create(
                category=category,
                title=file.name,
                image=file,
            )
        messages.success(request, "Images uploaded successfully!")
        return redirect("list_image")

    return render(request, "admin_pages/add_image.html", {"categories": categories})


@login_required(login_url="admin_login")
def delete_image(request, image_id):
    image = get_object_or_404(GalleryImage, id=image_id)
    if request.method == "POST":
        image.delete()
        messages.success(request, "Image deleted successfully!")
    return redirect("list_image")


# ==========================================
# CATEGORIES (ADMIN)
# ==========================================

@login_required(login_url="admin_login")
def category_list(request):
    categories = Category.objects.all().order_by(Lower("name"))
    return render(request, "admin_pages/category_list.html", {"categories": categories})


@login_required(login_url="admin_login")
def add_category(request):
    form = CategoryForm(request.POST or None)
    if form.is_valid():
        form.save()
        messages.success(request, "Category added!")
        return redirect("category_list")
    return render(request, "admin_pages/add_category.html", {"form": form})


@login_required(login_url="admin_login")
def update_category(request, pk):
    category = get_object_or_404(Category, pk=pk)
    form = CategoryForm(request.POST or None, instance=category)
    if form.is_valid():
        form.save()
        messages.success(request, "Category updated!")
        return redirect("category_list")
    return render(request, "admin_pages/add_category.html", {"form": form, "category": category})


@login_required(login_url="admin_login")
def delete_category(request, pk):
    category = get_object_or_404(Category, pk=pk)
    if request.method == "POST":
        category.delete()
        messages.success(request, "Category deleted!")
    return redirect("category_list")


# ==========================================
# TESTIMONIALS (ADMIN)
# ==========================================

@login_required(login_url="admin_login")
def testimonial_list(request):
    testimonials = Paginator(Testimonial.objects.all().order_by("-created_at"), 10).get_page(request.GET.get("page"))
    return render(request, "admin_pages/review_list.html", {"testimonials": testimonials})


@login_required(login_url="admin_login")
def testimonial_create(request):
    form = TestimonialForm(request.POST or None, request.FILES or None)
    if form.is_valid():
        form.save()
        messages.success(request, "Testimonial added!")
        return redirect("review_list")
    return render(request, "admin_pages/create_review.html", {"form": form})


@login_required(login_url="admin_login")
def testimonial_update(request, pk):
    testimonial = get_object_or_404(Testimonial, pk=pk)
    form = TestimonialForm(request.POST or None, request.FILES or None, instance=testimonial)
    if form.is_valid():
        form.save()
        messages.success(request, "Testimonial updated!")
        return redirect("review_list")
    return render(request, "admin_pages/create_review.html", {"form": form, "testimonial": testimonial})


@login_required(login_url="admin_login")
def testimonial_delete(request, pk):
    testimonial = get_object_or_404(Testimonial, pk=pk)
    if request.method == "POST":
        testimonial.delete()
        messages.success(request, "Testimonial deleted!")
    return redirect("review_list")


# ==========================================
# CONTACTS (ADMIN)
# ==========================================

@login_required(login_url="admin_login")
def view_contacts(request):
    contacts = Paginator(ContactMessage.objects.all().order_by("-created_at"), 10).get_page(request.GET.get("page"))
    return render(request, "admin_pages/view_contacts.html", {"contacts": contacts})


@login_required(login_url="admin_login")
def delete_contact(request, pk):
    contact = get_object_or_404(ContactMessage, pk=pk)
    if request.method == "POST":
        contact.delete()
        messages.success(request, "Contact deleted!")
    return redirect("view_contacts")
