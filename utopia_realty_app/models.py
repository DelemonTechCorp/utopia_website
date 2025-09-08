from django.db import models
from django.utils.text import slugify
# Create your models here.

class City(models.Model):
    name = models.CharField(max_length=255,null=True,blank=True)
    
    def __str__(self):
        return self.name

class District(models.Model):
    name = models.CharField(max_length=255,null=True,blank=True)
    city = models.ForeignKey(City,on_delete=models.CASCADE,related_name='districts',null=True,blank=True)
    
    def __str__(self):
        return self.name
    
class Developer(models.Model):
    name = models.CharField(max_length=255,null=True,blank=True)
    
    def __str__(self):
        return self.name
    
class PropertyType(models.Model):
    name = models.CharField(max_length=255,null=True,blank=True)
    
    def __str__(self):
        return self.name
    
class PropertyStatus(models.Model):
    name = models.CharField(max_length=255,null=True,blank=True)
    
    def __str__(self):
        return self.name
    
class SalesStatus(models.Model):
    name = models.CharField(max_length=155,null=True,blank=True)
    
    def __str__(self):
        return self.name
    
class Facility(models.Model):
    id = models.BigIntegerField(primary_key=True,blank=True)
    name = models.CharField(max_length=255,null=True,blank=True)
    
    def __str__(self):
        return self.name

class Property(models.Model):
    external_id = models.BigIntegerField(primary_key=True)
    title = models.CharField(max_length=255,null=True,blank=True)
    description = models.TextField(null=True,blank=True)
    cover = models.URLField(null=True,blank=True)
    address = models.CharField(max_length=255,null=True,blank=True)
    delivery_date = models.DateField(null=True,blank=True)
    low_price = models.BigIntegerField(null=True,blank=True)
    min_area = models.IntegerField(null=True,blank=True)
    payment_plan = models.BooleanField(default=False)
    post_delivery = models.BooleanField(default=False)
    payment_minimum_down_payment = models.PositiveIntegerField(null=True,blank=True)  
    guarantee_rental_guarantee = models.BooleanField(default=False)
    guarantee_rental_guarantee_value = models.PositiveIntegerField(null=True,blank=True)  
    down_payment = models.PositiveIntegerField(null=True,blank=True)  
    updated_at = models.DateTimeField(null=True,blank=True)
    city = models.ForeignKey(City,on_delete=models.CASCADE,related_name='properties')
    district = models.ForeignKey(District,on_delete=models.CASCADE,related_name='properties')
    developer = models.ForeignKey(Developer,on_delete=models.CASCADE,related_name='properties')
    property_type =  models.ForeignKey(PropertyType,on_delete=models.CASCADE,related_name='properties')
    property_status = models.ForeignKey(PropertyStatus,on_delete=models.CASCADE,related_name='properties')
    sales_status = models.ForeignKey(SalesStatus,on_delete=models.CASCADE,related_name='properties')
    facilities = models.ManyToManyField(Facility, related_name='properties')
    
    
class PropertyFacility(models.Model):
    property_id = models.ForeignKey(Property,on_delete=models.CASCADE)
    facility_id = models.ForeignKey(Facility,on_delete=models.CASCADE)
    
class PropertyImages(models.Model):
    property = models.ForeignKey(Property,on_delete=models.CASCADE,related_name='property_images')
    image = models.URLField()
        
class GroupedApartment(models.Model):
    property = models.ForeignKey(Property, related_name='grouped_apartments', on_delete=models.CASCADE)
    unit_type = models.CharField(max_length=255, null=True, blank=True)
    rooms = models.CharField(max_length=255,null=True,blank=True)
    min_price = models.PositiveIntegerField(null=True,blank=True)
    min_area = models.PositiveIntegerField(null=True,blank=True)

    def __str__(self):
        return self.unit_type

class PaymentPlan(models.Model):
    id = models.BigIntegerField(primary_key=True,blank=True)  
    property = models.ForeignKey(Property, related_name='payment_plans', on_delete=models.CASCADE)
    name = models.CharField(max_length=255,null=True,blank=True)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.name} ({self.property})"


class PaymentPlanValue(models.Model):
    id = models.BigIntegerField(primary_key=True,blank=True)  
    payment_plan = models.ForeignKey(PaymentPlan, related_name='values', on_delete=models.CASCADE)
    name = models.CharField(max_length=255,null=True,blank=True)
    value = models.CharField(max_length=20,null=True,blank=True) 

    def __str__(self):
        return f"{self.name}: {self.value}"
    
class Inquiry(models.Model):
    fullname = models.CharField(max_length=255, null=True)
    phone = models.CharField(max_length=20, null=True)
    email = models.EmailField(null=True)
    interest = models.CharField(max_length=100, null=True)
    property_type = models.CharField(max_length=100, null=True)
    budget = models.CharField(max_length=100, null=True)
    message = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    origin = models.CharField(max_length=255, blank=True)
    

    def __str__(self):
        return f"Inquiry from {self.fullname}"
    

class Contact(models.Model):
    name = models.CharField(max_length=255, null=True)
    phone = models.CharField(max_length=30, null=True)
    email = models.CharField(max_length=255, null=True)
    message = models.TextField(null=True)
    origin = models.CharField(max_length=255, blank=True)
    
    def __str__(self):
        return self.name

class Newsletter(models.Model):
    email = models.EmailField(unique=True)
    subscribed_at = models.DateTimeField(auto_now_add=True)
    origin = models.CharField(max_length=255, blank=True)

    def __str__(self):
        return self.email 

class PropertyContact(models.Model):
    name = models.CharField(max_length=255)
    email = models.EmailField()
    phone = models.CharField(max_length=20, blank=True)
    message = models.TextField(blank=True)
    origin = models.CharField(max_length=255, blank=True)
    submitted_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Inquiry from {self.name} - {self.email}"

class BlogPost(models.Model):   
    title = models.CharField(max_length=255)
    slug = models.SlugField(unique=True, blank=True)

    description = models.TextField(
        max_length=300,
        help_text="Brief intro or preview text."
    )
    
    content = models.TextField(
        help_text="Use markdown. Use ### for subheadings (for TOC)."
    )

    image = models.ImageField(
        upload_to='blog_images/',
        help_text="Main image for this blog post."
    )

    # ✅ Meta fields for SEO
    meta_title = models.CharField(
        max_length=60,
        help_text="SEO title (max ~60 characters)."
    )
    meta_description = models.CharField(
        max_length=160,
        help_text="SEO meta description (max ~160 characters)."
    )

    created_at = models.DateField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        from django.urls import reverse
        return reverse("blog_detail", kwargs={"slug": self.slug})
