from django.urls import path
from .views import category_list, category_detail,product_list, product_detail,review_list, review_detail, products_with_reviews

urlpatterns = [
    path('categories/', category_list),
    path('categories/<int:id>/', category_detail),
    path('products/', product_list),
    path('products/<int:id>/', product_detail),
    path('reviews/', review_list),
    path('reviews/<int:id>/', review_detail),
    path('products/reviews/', products_with_reviews),
]