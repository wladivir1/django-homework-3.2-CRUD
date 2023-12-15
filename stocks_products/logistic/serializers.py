from rest_framework import serializers
from django.core.validators import MinValueValidator

from .models import Product, Stock, StockProduct


class ProductSerializer(serializers.ModelSerializer):
    # настройте сериализатор для продукта
     
    class Meta:
        model = Product
        fields = ['id', 'title', 'description']    


class ProductPositionSerializer(serializers.ModelSerializer):
    # настройте сериализатор для позиции продукта на складе
    product = serializers.PrimaryKeyRelatedField(queryset=Product.objects.all())
     
    class Meta:
        model = StockProduct
        fields = ['product', 'quantity', 'price']
    
        
class StockSerializer(serializers.ModelSerializer):
    positions = ProductPositionSerializer(many=True)
    
    class Meta:
        model = Stock
        fields = ['id', 'address', 'positions']
    

    # настройте сериализатор для склада
    def create(self, validated_data):
        # достаем связанные данные для других таблиц
        positions = validated_data.pop('positions')   
        # создаем склад по его параметрам
        stock = super().create(validated_data)
        
        for position in positions:
            StockProduct.objects.create(stock=stock, **position)
        
        return stock

    def update(self, instance, validated_data):
        # достаем связанные данные для других таблиц
        positions = validated_data.pop('positions')
        # обновляем склад по его параметрам
        stock = super().update(instance, validated_data)
       
        for position in positions:
            StockProduct.objects.update_or_create(
                                                  stock=stock, 
                                                  product=position['product'], 
                                                  defaults=position
                                                  )

        return stock
    
    