from django.urls import path
from .import views
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    path('base', views.base, name='base'),
    path('', views.index, name='index'),
    path('about', views.about, name='about'),
    path('contact', views.contact, name='contact'),
    path('buy_sell', views.buy_sell, name='buy_sell'),
    path('short_rental', views.short_rental, name='short_rental'),
    path('property_management', views.property_management, name='property_management'),
    path('rent_lease', views.rental_lease, name='rent_lease'),
    path('residential', views.residential, name='residential'),
    path('offplan', views.offplan, name='offplan'),
    path('global_property', views.global_property, name='global_property'),
    path('sales_support', views.sales_support, name='sales_support'),
    path('financial', views.financial, name='financial'),
    path('inquiry', views.inquiry, name='inquiry'),
    path('thankyou', views.thankyou, name='thankyou'),
    path('review', views.review, name='review'),
    path('blog', views.blog_list, name='blog'),
    path('blog/<slug:slug>/', views.blog_detail, name='blog_detail'),
    path('property_list',views.properties,name='property_list'),
    path('property_detail/<int:pk>/', views.propertyDetailView, name='property_detail'),

    
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
