from django.db import models
from django.conf import settings
from django.urls import reverse
from django_countries.fields import CountryField

CATEGORY = (
    ('S','Sport'),
    ('O','Outwere'),
    ('T','Tshirt'),
)

LABELS = (
    ('P','primary'),
    ('S','secondary'),
    ('D','danger'),
)


#  item detail
class Item(models.Model):
    title = models.CharField(max_length=50)
    image = models.ImageField(upload_to='media')
    discription = models.TextField()
    slug = models.SlugField()
    price = models.FloatField()
    category = models.CharField(choices= CATEGORY,max_length=1)
    discount = models.FloatField()
    label = models.CharField(choices=LABELS,max_length=1)


    def get_product_url(self):
        return reverse('core:product',kwargs={
            'slug' : self.slug
        })

    def get_actual_price(self):
        if self.discount:
            return self.price - self.discount

    def get_add_cart_url(self):
        return reverse('core:add_cart',kwargs={
            'slug':self.slug
        })
            

    def get_remove_one_cart_url(self):
        return reverse('core:remove_one_cart',kwargs={
            'slug':self.slug
        })

    def get_remove_cart(self):
        return reverse('core:remove_cart',kwargs={
            'slug': self.slug
        })

    
# create a order item 
class OrderItem(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete= models.CASCADE)
    item = models.ForeignKey(Item,on_delete=models.CASCADE)
    ordered = models.BooleanField(default=False)
    quantity = models.IntegerField(default=1)


    def get_total_price(self):
        total = 0
        if self.item.get_actual_price():
            total += (self.item.get_actual_price() * self.quantity)
            return total
        total += self.quantity * self.item.price
        return total

    def get_total_discount(self):
        return self.item.discount * self.quantity

  

    


# items wich user selected
class Order(models.Model):
    ref_code = models.CharField(max_length=20,null=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE)
    items = models.ManyToManyField(OrderItem)
    order_date = models.DateField(auto_now=True)
    ordered_date  = models.DateTimeField()
    ordered = models.BooleanField(default=False)
    # adding more about user more information so i can use this on one page 
    billing_address = models.ForeignKey(
        'Address', related_name='billing_address',on_delete=models.SET_NULL, blank=True ,null=True 
        )
    shipping_address = models.ForeignKey(
        'Address', related_name='shipping_address', on_delete=models.SET_NULL, blank=True ,null=True 
    )
    # shipping_address = models.ForeignKey(
    #     'Address',related_name='billing_address',on_delete=models.SET_NULL,blank=True ,null=True 
    #     )
    payment = models.ForeignKey(
        'Payment',on_delete=models.SET_NULL,blank=True ,null=True 
    )
    cupon = models.ForeignKey(
        'Cupon' , on_delete=models.SET_NULL, blank=True ,null=True
    )
    item_delivered = models.BooleanField(default=False)
    ''' we have allready order as a foreign key in refund form so can't make refund as a foriegn key '''
    refund_requseted = models.BooleanField(default=False)
    refund_granted = models.BooleanField(default=False)



    def __str__(self):
        return self.user.username

  

    def get_all_product_price(self):
        total = 0
        if self.cupon:
            for order_item in self.items.all():
                total += order_item.get_total_price()   

            if self.cupon.amount < total:
                total -= self.cupon.amount
            return total
        for order_item in self.items.all():
            total += order_item.get_total_price()
        return total



PAYMENT_CHOICE = (
    ('P',  'paypal'),
    ('S' , 'stripe')
)

ADDRESS_CHOICES = (
    ('S','Shipping'),
    ('B','Billing')
)



# we have handle here multiple address biling and shipping

class Address(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    street_address = models.CharField(max_length=100)
    apartment_address = models.CharField(max_length=100)
    country = CountryField(multiple=False)
    zip = models.CharField(max_length=6)
    address_type = models.CharField(max_length=1,choices=ADDRESS_CHOICES)
    default = models.BooleanField(default=False)

    def __str__(self):
        return self.user.username

    class Meta:
        verbose_name_plural = 'Addresses'

    
    # show custom name in table  


# ''' after delete user the payment not delete '''
class Payment(models.Model):
    stripe_charge_id  = models.CharField(max_length=50)
    user = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.SET_NULL,null=True, blank=True)
    amount = models.FloatField()
    timestamp = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.user.username




class Cupon(models.Model):
    cupon_code = models.CharField(max_length=15)
    amount = models.FloatField( null=True, blank=True)



class Refund(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    ref_code = models.CharField(max_length=20)
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    email = models.EmailField()
    resion  = models.CharField(max_length=50)
    accepeted = models.BooleanField(default=False)


    def __str__(self):
        return self.user.username
        









