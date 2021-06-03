from django.db import models
from django.contrib.auth.admin import User
from datetime import datetime
import random

# Create your models here.
class Product(models.Model):
    name = models.CharField(max_length = 50)
    uniqueCode = models.CharField(max_length=10, unique=True, null=False, default = "")
    price = models.FloatField()
    priceNoDiscount = models.FloatField(default=0.0)
    desc = models.TextField()
    size = models.CharField(max_length=2)
    img = models.ImageField(null=True, blank=True)

    def __str__(self):
        return self.name

    @property
    def imageURL(self):
        try:
            url = self.image.url
        except:
            url = ''
        return url

class Order(models.Model):
	payment_status_choices = (
        (1, 'SUCCESS'),
        (2, 'FAILURE' ),
        (3, 'PENDING'),
    )
	customer = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
	date_ordered = models.DateTimeField(null=False, default = datetime.now())
	complete = models.BooleanField(default=False)
	transaction_id = models.CharField(max_length=100, null=True)
	order_id = models.CharField(unique=True, max_length=100, null=True, blank=True, default=None)
	razorpay_order_id = models.CharField(max_length=500, null=True, blank=True)
	razorpay_payment_id = models.CharField(max_length=500, null=True, blank=True)
	razorpay_signature = models.CharField(max_length=500, null=True, blank=True)
	total_amount = models.FloatField(default=0.0)
	payment_status = models.IntegerField(choices = payment_status_choices, default=3)

	def __str__(self):
		return str(self.id)
		
	@property
	def shipping(self):
		shipping = False
		orderitems = self.orderitem_set.all()
		for i in orderitems:
			if i.product.digital == False:
				shipping = True
		return shipping

	@property
	def get_cart_total(self):
		orderitems = self.orderitem_set.all()
		total = sum([item.get_total for item in orderitems])
		return round(total, 3) 

	@property
	def get_cart_items(self):
		orderitems = self.orderitem_set.all()
		total = sum([item.quantity for item in orderitems])
		return total
	
	def save(self, *args, **kwargs):
		if self.order_id is None and self.date_ordered and self.id:
			self.order_id = 'ODR' + self.transaction_id + str(self.id)
		return super().save(*args, **kwargs)

class OrderItem(models.Model):
	product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True)
	order = models.ForeignKey(Order, on_delete=models.SET_NULL, null=True)
	quantity = models.IntegerField(default=0, null=True, blank=True)
	date_added = models.DateTimeField(auto_now_add=True)
	size = models.CharField(max_length=4, default="M")
	color = models.CharField(max_length=50, default="Yellow")

	@property
	def get_total(self):
		total = self.product.price * self.quantity
		return total

class ShippingAddress(models.Model):
	customer = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
	order = models.ForeignKey(Order, on_delete=models.SET_NULL, null=True)
	address = models.CharField(max_length=200, null=False)
	city = models.CharField(max_length=200, null=False)
	state = models.CharField(max_length=200, null=False)
	zipcode = models.CharField(max_length=200, null=False)
	date_added = models.DateTimeField(null=False)

	def __str__(self):
		return self.address

class AllOrders(models.Model):
	customer = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
	order = models.ForeignKey(Order, on_delete=models.SET_NULL, null=True)
	order_details = models.TextField(null=True, default="")
	shipment = models.ForeignKey(ShippingAddress, on_delete=models.SET_NULL, null=True)
	date_ordered = models.DateTimeField(auto_now_add=True , null=True)
	order_id_unique = models.CharField(max_length = 100 , null=True)
	address = models.CharField(max_length = 100 , null=True)
	city = models.CharField(max_length = 50 , null=True)
	state = models.CharField(max_length = 50 , null=True)
	zipcode = models.CharField(max_length = 50 , null=True)
	total_items = models.IntegerField(null=True)
	total_amount = models.FloatField(null=True)
	razorpay_order_id = models.CharField(max_length = 500 , null=True)
	razorpay_payment_id = models.CharField(max_length = 500 , null=True)

	def __str__(self):
		tempId = str(random.randint(0, 1000))
		return self.customer.username + tempId	+ self.order.date_ordered.strftime('%Y%m%d')