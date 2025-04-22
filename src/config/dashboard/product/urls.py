from django.urls import include, path
from . import views

urlpatterns = [
    path("stock/list/", views.product_list, name="product-list"),
    path("stock/create/", views.product_create, name="product-create"),
    path("stock/<int:pk>/edit/", views.product_edit, name="product-edit"),

    path("defect/list/", views.defect_list, name="defect-list"),
    path("defect/<int:pk>/edit/", views.defect_edit, name="defect-edit"),
    path("defect/list/history/", views.defect_list_history, name="defect-list-history"),

    path("type/list/", views.type_list, name="type-list"),
    path("type/create/", views.type_create, name="type-create"),
    path("type/<int:pk>/edit/", views.type_edit, name="type-edit"),

    path("category/list/", views.category_list, name="category-list"),
    path("category/create/", views.category_create, name="category-create"),
    path("category/<int:pk>/edit/", views.category_edit, name="category-edit"),

    path("prepack/list/", views.prepack_product_list, name="prepack-product-list"),
    path("list/", views.production_product_list, name="production-product-list"),
    path("income/list/", views.production_product_income_list, name="production-product-income-list"),
    path("info-list/", views.production_product_info_list, name="production-product-info-list"),
    path("info/create/", views.production_product_info_create, name="production-product-info-create"),
    path("info/<int:pk>/edit/", views.production_product_info_edit, name="production-product-info-edit"),
    path("create/", views.add_production_product, name="add_production_product"),
    
    
    path("accepted/<int:pk>", views.production_product_accepted, name="production-product-accepted"),
    path("cancel/<int:pk>", views.production_product_cancel, name="production-product-cancel"),


    path("add-price/", views.add_price_product, name="add-price-product")


]
