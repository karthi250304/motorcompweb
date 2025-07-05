from django.db import models

class Company(models.Model):
    name = models.CharField(max_length=100)
    address = models.TextField()
    gst_number = models.CharField(max_length=50)
    company_phone = models.CharField(max_length=10)
    contact_person = models.CharField(max_length=100)
    contact_phone = models.CharField(max_length=10)
    logo = models.ImageField(upload_to='company_logos/')
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name
    
class Dealer(models.Model):
    name = models.CharField(max_length=100)
    address = models.TextField()
    gst_number = models.CharField(max_length=50)
    company_phone = models.CharField(max_length=10)
    contact_person = models.CharField(max_length=100)
    contact_phone = models.CharField(max_length=10)
    logo = models.ImageField(upload_to='dealer_logos/')
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name


class CustomUser(models.Model):
    name =models.CharField(max_length=100)
    phone =models.CharField(max_length=100)
    username =models.CharField(max_length=100, unique=True)
    password =models.CharField(max_length=100)
    is_active =models.BooleanField(default=True)

    def __str__(self):
        return self.username

class Tax(models.Model):
    name = models.CharField(max_length=100)
    cgst = models.DecimalField(max_digits=5, decimal_places=2)
    sgst = models.DecimalField(max_digits=5, decimal_places=2)
    igst = models.DecimalField(max_digits=5, decimal_places=2)
    is_active = models.BooleanField(default=True)

    def total_tax(self):
        return self.cgst + self.sgst + self.igst

    def __str__(self):
        return self.name

class ItemCategory(models.Model):
    name = models.CharField(max_length=100)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name

class ItemSubCategory(models.Model):
    name = models.CharField(max_length=100)
    category = models.ForeignKey(ItemCategory, on_delete=models.CASCADE)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name

class Item(models.Model):
    name = models.CharField(max_length=255)
    code = models.CharField(max_length=50, unique=True)
    brand = models.CharField(max_length=100, blank=True, null=True)  # ← add this
    category = models.ForeignKey(ItemCategory, on_delete=models.CASCADE)
    subcategory = models.ForeignKey(ItemSubCategory, on_delete=models.CASCADE)
    warranty = models.PositiveIntegerField()
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name

from django.db import models
from .models import Item, Tax, Dealer, Company

class Bill(models.Model):
    invoice_number = models.CharField(max_length=20, unique=True)
    date = models.DateField(auto_now_add=True)
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    rate = models.DecimalField(max_digits=10, decimal_places=2)
    tax = models.ForeignKey(Tax, on_delete=models.CASCADE)
    dealer = models.ForeignKey(Dealer, on_delete=models.CASCADE)
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    customer_name = models.CharField(max_length=100)
    customer_address = models.CharField(max_length=200)
    customer_phone = models.CharField(max_length=15)
    billing_address = models.CharField(max_length=200)
    shipping_address = models.CharField(max_length=200)

    def amount(self):
        return self.quantity * self.rate

    def cgst_amount(self):
        return (self.amount() * self.tax.cgst) / 100

    def sgst_amount(self):
        return (self.amount() * self.tax.sgst) / 100

    def igst_amount(self):
        return (self.amount() * self.tax.igst) / 100

    def total(self):
        return self.amount() + self.cgst_amount() + self.sgst_amount() + self.igst_amount()

    def save(self, *args, **kwargs):
        if not self.invoice_number:
            last = Bill.objects.order_by('-id').first()
            if last:
                last_number = int(last.invoice_number.replace("INV", ""))
                self.invoice_number = f"INV{last_number + 1:05d}"
            else:
                self.invoice_number = "INV00001"
        super().save(*args, **kwargs)
