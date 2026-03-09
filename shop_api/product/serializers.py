from rest_framework import serializers
from .models import Category, Product, Review
from django.db.models import Avg
from rest_framework.exceptions import ValidationError

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = '__all__'


class ReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = '__all__'


class ProductReviewSerializer(serializers.ModelSerializer):
    reviews = ReviewSerializer(many=True, read_only=True)
    rating = serializers.SerializerMethodField()
    class Meta:
        model = Product
        fields = 'id', 'title', 'description', 'price', 'reviews', 'rating'
    def get_rating(self, obj):
        avg = obj.reviews.aggregate(avg_rating=Avg('stars'))['avg_rating']
        return round(avg, 2) if avg else 0
    

class CategoryWithCountSerializer(serializers.ModelSerializer):
    products_count = serializers.IntegerField(read_only=True)
    class Meta:
        model = Category
        fields = ['id', 'name', 'products_count']


class CategoryValidateSerializer(serializers.Serializer):
    name = serializers.CharField(required=True, max_length=100, min_length=2)


class ProductValidateSerializer(serializers.Serializer):
    title = serializers.CharField(required=True, max_length=255, min_length=3)
    description = serializers.CharField(required=False)
    price = serializers.FloatField(required=True, min_value=0)
    category_id = serializers.IntegerField(required=True)

    def validate_category_id(self, category_id):
        try:
            Category.objects.get(id=category_id)
        except Category.DoesNotExist:
            raise ValidationError('Category does not exist!')
        return category_id


class ReviewValidateSerializer(serializers.Serializer):
    text = serializers.CharField(required=True, min_length=1)
    product_id = serializers.IntegerField(required=True)
    stars = serializers.IntegerField(required=True, min_value=1, max_value=5)

    def validate_product_id(self, product_id):
        try:
            Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            raise ValidationError('Product does not exist!')
        return product_id