from rest_framework import serializers
from .models import Product, Order 

# ================= Product Serializer =================
class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = '__all__'


# ================= Order Item Serializer =================
class OrderItemSerializer(serializers.Serializer):
    product_id = serializers.IntegerField()
    order_qty = serializers.IntegerField()

    def validate(self, data):
        try:
            product = Product.objects.get(product_id=data['product_id'])
        except Product.DoesNotExist:
            raise serializers.ValidationError("Product not found")

        qty = data['order_qty']

        if qty <= 0:
            raise serializers.ValidationError("Quantity must be greater than 0")

        if qty > product.product_stock:
            raise serializers.ValidationError("Not enough stock available")

        # attach product to use later
        data['product'] = product
        return data

    def create(self, validated_data):
        product = validated_data['product']
        qty     = validated_data['order_qty']

        #  DO NOT REDUCE STOCK HERE
        return Order.objects.create(
            product=product,
            order_qty=qty,
            order_price=product.product_price
        )


# ================= Bulk Order Serializer =================
class BulkOrderSerializer(serializers.Serializer):
    items = OrderItemSerializer(many=True)

    def create(self, validated_data):
        orders = []

        for item in validated_data['items']:
            product = item['product']
            qty     = item['order_qty']

            # Create only order (do NOT reduce stock here)
            orders.append(Order.objects.create(
                product=product,
                order_qty=qty,
                order_price=product.product_price
            ))

        return orders



# ================= Today Order Serializer =================
class TodayOrderSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.product_name')
    product_id = serializers.IntegerField(source='product.product_id')

    class Meta:
        model = Order
        fields = ['id', 'product_id', 'product_name', 'order_qty', 'order_price', 'order_datetime']


# ================= Daily Total Serializer =================
class DailyTotalSerializer(serializers.Serializer):
    date = serializers.DateField()
    total_price = serializers.DecimalField(max_digits=10, decimal_places=2)
    order_count = serializers.IntegerField()
