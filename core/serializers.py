from rest_framework import serializers
from .models import Category, Product, Order, OrderItem, Cart, CartItem
from django.contrib.auth.models import User


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'slug']

class ProductSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)

    class Meta:
        model = Product
        fields = [
            'id', 'name', 'slug', 'description', 'price',
            'stock', 'image', 'is_available', 'category', 'category_name'
        ]
        extra_kwargs = {
            'category': {'write_only': True}
        }

class OrderItemSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)

    class Meta:
        model = OrderItem
        fields = ['id', 'product', 'price', 'quantity']


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    user = serializers.StringRelatedField() # Hiển thị username

    class Meta:
        model = Order
        fields = [
            'id', 'user', 'first_name', 'last_name', 'email', 'address',
            'postal_code', 'city', 'created_at', 'paid', 'total_price', 'items'
        ]
        

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, style={'input_type': 'password'})
    
    class Meta:
        model = User
        fields = ('username', 'password', 'email', 'first_name', 'last_name')

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', '')
        )
        user.set_password(validated_data['password'])
        user.save()
        return user
    
    
class CreateOrderItemSerializer(serializers.ModelSerializer):
    product_id = serializers.IntegerField()

    class Meta:
        model = OrderItem
        fields = ['product_id', 'quantity']

# Serializer cho việc tạo đơn hàng chính
class CreateOrderSerializer(serializers.ModelSerializer):
    items = CreateOrderItemSerializer(many=True)

    class Meta:
        model = Order
        fields = [
            'first_name', 'last_name', 'email', 'address',
            'postal_code', 'city', 'items'
        ]

    def create(self, validated_data):
        from django.db import transaction
        
        items_data = validated_data.pop('items')
        
        with transaction.atomic():
            order = Order.objects.create(**validated_data)
            
            total_price = 0
            for item_data in items_data:
                product = Product.objects.get(id=item_data['product_id'])
                quantity = item_data['quantity']

                if product.stock < quantity:
                    raise serializers.ValidationError(f"Sản phẩm '{product.name}' không đủ số lượng tồn kho.")

                item = OrderItem.objects.create(
                    order=order,
                    product=product,
                    price=product.price,
                    quantity=quantity
                )
                
                total_price += item.get_cost()
                product.stock -= quantity
                product.save()

            order.total_price = total_price
            order.save()
            
        return order
    
    
class CartItemSerializer(serializers.ModelSerializer):
    product = ProductSerializer()

    class Meta:
        model = CartItem
        fields = ['id', 'product', 'quantity', 'added_at', 'get_cost']

class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True, read_only=True)
    total = serializers.SerializerMethodField()

    class Meta:
        model = Cart
        fields = ['id', 'user', 'created_at', 'items', 'total']

    def get_total(self, obj):
        return sum(item.get_cost() for item in obj.items.all())