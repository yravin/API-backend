from django.db import models

class Category(models.Model) :
    category_name = models.CharField(max_length=200)
    def __str__(self):
        return  self.category_name
#product
class Product(models.Model) :
    product_id = models.AutoField(primary_key=True)
    product_name = models.CharField(max_length=100)
    product_price = models.DecimalField(max_digits=10, decimal_places=2)
    product_stock = models.IntegerField()
    product_status = models.CharField(
    max_length=20,
    choices=[
         ('old_stock', 'ស្តុកចាស់'),
         ('new_stock', 'ស្តុកថ្មី')
    ],
    default='old_stock'
)
    product_image = models.ImageField(upload_to='products/', blank=True, null=True)
    category_name = models.ForeignKey(Category, on_delete= models.CASCADE)
    def __str__(self) :
        return  self.product_name
    #កាត់ស្តុក
    def reduce_stock(self, qty):
        #កាត់ស្តុក product មួយ"""
        #ស្តុកត្រូវតែធំជាងសូន្យ បេីស្តុកតូចជាងសូន្យ codeមិនកាត់ស្តុក
        if qty <= 0:
            raise ValueError("Quantity must be greater than 0")
        #បេីoderលេីសស្តុកនោះនិងError
        if qty > self.product_stock:
            raise ValueError("Not enough stock")
        #Oderត្រឹមត្រូវកាត់ស្តុក រួចSave
        self.product_stock -= qty
        self.save()

class Order(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    order_datetime = models.DateTimeField(auto_now_add=True)
    order_qty = models.IntegerField(default=1)
    order_price = models.DecimalField(max_digits=10, decimal_places=2)  # store price at the time
    def __str__(self):
        return f"Order {self.id} - {self.product.product_name}"
    
    def save(self, *args, **kwargs):
        #Override save method to automatically reduce stock
        if not self.pk:  # Only for new orders
            self.product.reduce_stock(self.order_qty)
        super().save(*args, **kwargs)
    
#គណនាតម្លៃនិងចំនួនoderតាមថ្ងៃ    
def calculate_daily_total():
    # Import inside function to avoid circular import
    from .models import Order  
    from django.db.models import Sum
    from django.db.models.functions import TruncDate

    daily_totals = (
        Order.objects
        .annotate(date=TruncDate('order_date'))
        .values('date')
        .annotate(total_price=Sum('order_price'))
        .order_by('date')
    )
    return daily_totals

