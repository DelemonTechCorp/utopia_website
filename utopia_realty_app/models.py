from django.db import models

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