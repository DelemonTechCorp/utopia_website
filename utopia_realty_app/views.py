from django.shortcuts import render,redirect
from utopia_realty_app.models import *
from django.db.models import Count
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404
from django.utils.safestring import mark_safe
import markdown
from django.db.models import Q
import requests
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
# Create your views here.

def base(request):
    return render(request,'base.html')


def index(request):
    view_all = request.GET.get('view') == 'all'

    if view_all:
        # Ignore filters and load all
        properties_qs = Property.objects.all().order_by('-updated_at')
        status_id = ''
        city_id = ''
    else:
        # Apply filters normally
        status_id = request.GET.get('status', '').strip()
        city_id = request.GET.get('city', '').strip()
        properties_qs = Property.objects.all().order_by('-updated_at')
        if status_id:
            properties_qs = properties_qs.filter(property_status_id=status_id)
        if city_id:
            properties_qs = properties_qs.filter(city_id=city_id)

    filtered_count = properties_qs.count()
    properties = properties_qs if view_all else properties_qs[:8]

    status_counts = PropertyStatus.objects.annotate(count=Count('properties'))
    city_counts = City.objects.annotate(count=Count('properties'))

    selected_status = PropertyStatus.objects.filter(id=status_id).first() if status_id else None
    selected_city = City.objects.filter(id=city_id).first() if city_id else None

    context = {
        'properties': properties,
        'filtered_count': filtered_count,
        'status_counts': status_counts,
        'city_counts': city_counts,
        'selected_status': selected_status,
        'selected_city': selected_city,
        'view_all': view_all
    }

    return render(request, 'main/index.html', context)

from django.db.models import Q
from django.core.paginator import Paginator
from .models import Property, City, PropertyType, PropertyStatus, Developer

from django.shortcuts import render
from django.core.paginator import Paginator
from .models import Property, City, Developer, PropertyType, PropertyStatus

def properties(request):
    property_list = Property.objects.all()

    # Read filters from request.GET
    location_id = request.GET.get('location')
    price_range = request.GET.get('price_range')
    property_type_id = request.GET.get('property_type')
    property_status_id = request.GET.get('property_status')
    property_name = request.GET.get('property_name') 
    developer_name = request.GET.get('developer')

    # Apply filters
    if location_id:
        property_list = property_list.filter(city_id=location_id)

    if price_range:
        try:
            if '-' in price_range:
                parts = price_range.split('-')
                min_price = int(parts[0]) if parts[0] else 0
                max_price = int(parts[1]) if parts[1] else None

                if max_price:
                    property_list = property_list.filter(low_price__gte=min_price, low_price__lte=max_price)
                else:
                    property_list = property_list.filter(low_price__gte=min_price)
        except ValueError:
            pass



    if property_type_id:
        property_list = property_list.filter(property_type_id=property_type_id)

    if property_status_id:
        property_list = property_list.filter(property_status_id=property_status_id)

    if property_name:
        property_list = property_list.filter(title__icontains=property_name)

    if developer_name:
        property_list = property_list.filter(developer__name__icontains=developer_name)

    # Pagination
    paginator = Paginator(property_list, 8)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # Filter data for form
    locations = City.objects.all().order_by('name')
    property_types = PropertyType.objects.all().order_by('name')
    property_statuses = PropertyStatus.objects.all().order_by('name')
    properties_all = Property.objects.all().order_by('title')  # For property name dropdown
    developers = Developer.objects.all().order_by('name')

    context = {
        'page_obj': page_obj,
        'locations': locations,
        'property_types': property_types,
        'property_statuses': property_statuses,
        'properties': properties_all,
        'developers': developers,
    }

    return render(request, 'main/properties.html', context)

def propertyDetailView(request, pk):
    prop = get_object_or_404(Property.objects.prefetch_related('facilities','property_images','payment_plans__values'), external_id=pk)
       # Fallback: use the first apartment for bedrooms and size
    apartments = prop.grouped_apartments.all().order_by('min_price')
    first_apartment = apartments.first()

    context = {
        'prop': prop,
        'first_bedroom': first_apartment.rooms if first_apartment else None,
        'size': first_apartment.min_area if first_apartment else None,
        'price': prop.low_price  # Use price directly from Property table
    }

    return render(request, 'main/property_detail.html', context)


def about(request):
    return render(request,'main/about.html')

@csrf_exempt  # Optional if you're not using CSRF token
def save_contact_only(request):
    if request.method == "POST":
        Contact.objects.create(
            name=request.POST.get("name"),
            phone=request.POST.get("phone"),
            email=request.POST.get("email"),
            message=request.POST.get("message"),
            origin=request.POST.get("origin")
        )
        return JsonResponse({"status": "success"})
    return JsonResponse({"status": "error"}, status=400)

def contact(request):
    return render(request, 'main/contact.html')
# def contact(request):
#     if request.method == "POST":
#         name = request.POST.get("name")
#         phone = request.POST.get("phone")
#         email = request.POST.get("email")
#         message = request.POST.get("message")
#         origin = request.POST.get("origin")

#         Contact.objects.create(
#             name=name,
#             phone=phone,
#             email=email,
#             message=message,
#             origin=origin
#         )

#         return redirect("thankyou")  

#     return render(request,'main/contact.html')

def buy_sell(request):
    return render(request,'main/buy_sell.html')

def short_rental(request):
    return render(request,'main/short_rental.html')

def property_management(request):
    return render(request,'main/property_management.html')

def rental_lease(request):
    return render(request,'main/rent_lease.html')

def residential(request):
    return render(request,'main/residential.html')

def offplan(request):
    return render(request,'main/offplan.html')

def global_property(request):
    return render(request,'main/global.html')

def sales_support(request):
    return render(request,'main/sales_support.html')

def financial(request):
    return render(request,'main/financial.html')

@csrf_exempt  
def save_inquiry_only(request):
    if request.method == "POST":
        Inquiry.objects.create(
            fullname=request.POST.get("fullname"),
            phone=request.POST.get("tel"),
            email=request.POST.get("email"),
            interest=request.POST.get("interest"),
            property_type=request.POST.get("property_type"),
            budget=request.POST.get("budget"),
            message=request.POST.get("message"),
            origin=request.POST.get("origin")

        )
        return JsonResponse({"status": "success"})
    return JsonResponse({"status": "error"}, status=400)

def inquiry(request):
    return render(request, "main/inquiry.html")
   
def thankyou(request):
    return render(request,'main/thankyou.html')

def review(request):
    return render(request,'main/review.html')

def blog_list(request):
    featured_post = BlogPost.objects.order_by('-created_at').first()
    posts_list = BlogPost.objects.exclude(id=featured_post.id) if featured_post else BlogPost.objects.all()
    paginator = Paginator(posts_list, 13)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'featured_post': featured_post,
        'posts': page_obj,    
        'page_obj': page_obj,
    }

    return render(request, 'main/blog.html', context)
def blog_detail(request, slug):
    blog = get_object_or_404(BlogPost, slug=slug)
    related_posts = BlogPost.objects.exclude(id=blog.id)[:3]  
    md = markdown.Markdown(extensions=['toc', 'fenced_code'])
    html_content = md.convert(blog.content)
    toc = md.toc

    context = {
        'blog': blog,
        'content': mark_safe(html_content),
        'toc': mark_safe(toc),
        'meta_title': blog.meta_title,
        'meta_description': blog.meta_description,
        'related_posts': related_posts
    }

    return render(request, 'main/blog-detail.html', context)
