from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .models import Product,Order
from .serializers import ProductSerializer, BulkOrderSerializer
from django.utils import timezone
from django.db.models import Sum
from django.db  import transaction
from collections import defaultdict
# ================= Product List =================
@api_view(['GET', 'POST'])
def product_list(request):
    #=============ទាញ  dataទាំងអស់===============
    if request.method == 'GET':
        products = Product.objects.all()
        serializer = ProductSerializer(products, many=True)
        return Response(serializer.data)
    # ===============បន្ថែម Data=============
    elif request.method == 'POST':
        serializer = ProductSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        print(serializer.errors)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# ================= Product Detail =================
@api_view(['GET', 'PUT', 'DELETE'])
#================រក id  product=====================
def product_detail(request, pk):
    try:
        product = Product.objects.get(pk=pk)
    except Product.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)
#=====================ទាញ dta តាម id=====================
    if request.method == 'GET':
        serializer = ProductSerializer(product)
        return Response(serializer.data)
#======================== Update data=====================
    elif request.method == 'PUT':
        serializer = ProductSerializer(product, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        print(serializer.errors)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
#===============================delete  data====================
    elif request.method == 'DELETE':
        product.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

# ================= Make Order សម្រាប់គណនាចំនួនOder and  តម្លៃ និង កាត់ស្តុក=================
@api_view(['POST'])
@transaction.atomic
def make_order(request):
    serializer = BulkOrderSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    items = serializer.validated_data['items']

    # --------  Group duplicated product items --------
    grouped = defaultdict(int)
    for item in items:
        grouped[item['product'].product_id] += item['order_qty']

    # --------  Reduce stock only once per product --------
    for product_id, total_qty in grouped.items():
        product = Product.objects.select_for_update().get(product_id=product_id)

        if product.product_stock < total_qty:
            return Response(
                {"message": f"Not enough stock for {product.product_name}"},
                status=status.HTTP_400_BAD_REQUEST
            )

        product.product_stock -= total_qty
        product.save()

    # --------  Now create orders (no stock update here) --------
    orders = serializer.save()

    # --------  Response --------
    resp = []
    for o in orders:
        resp.append({
            "order_id": o.id,
            "product": o.product.product_name,
            "qty": o.order_qty,
            "price": o.order_price,
            "stock_left": o.product.product_stock
        })

    return Response({
        "message": "Order successful",
        "orders": resp
    })
@api_view(['GET'])
def today_orders(request):
    today = timezone.now().date()
    
    # ប្រើ order_datetime__date ដើម្បី filter តាមថ្ងៃ
    orders = Order.objects.filter(order_datetime__date=today)
    
    # គណនាតម្លៃសរុប
    total_price = orders.aggregate(total=Sum('order_price'))['total'] or 0
    
    # Serialize orders
    order_data = []
    for order in orders:
        order_data.append({
            'id': order.id,
            'product_id': order.product.product_id,
            'product_name': order.product.product_name,
            'order_qty': order.order_qty,
            'order_price': str(order.order_price),
            'order_datetime': order.order_datetime
        })
    
    return Response({
        'date': today,
        'total_price': total_price,
        'orders': order_data,
        'order_count': orders.count()
    })