from django.urls import include, path
from . import views


urlpatterns = [
    path("order/list/", views.order_list, name="order-list"),
    path("order/zav-list/", views.order_list, name="order-zav-list"),
    path("order/create/", views.order_create, name="order-create"),
    path("order/<int:order_id>/view/", views.order_view, name="order-view"),
    path("order/<int:client_id>/add/", views.add_order, name="add-order"),
    
    path("add/driver/", views.take_driver, name="take-driver"),
    path("give/zav-sklad/", views.give_zav_sklad, name="give-zav-sklad"),
    
    
    path("payment/list/", views.payment_list, name="payment-list"),
    path("payment/create/", views.payment_create, name="payment-create"),
    path("payment/<int:payment_id>/edit/", views.payment_edit, name="payment-edit"),
    
    path("driver/order/active/list/", views.driver_order_list, name="driver-order-list"),
    # path("driver/completed/order/list/", views.driver_completed_order_list, name="driver-completed-order-list"),
    
    
    # path("order/<int:order_id>/invoice/", views.order_invoice, name="order-invoice"),
    path("order/<int:order_id>/invoice-chek/", views.order_invoice_chek, name="order-invoice-chek"),
    path("order/<int:order_id>/complete/", views.complate_order, name="order-complate"),
    path("order/<int:order_id>/change-price/", views.order_change_price, name="order-change-price"),
    
    path("order/payment-history/", views.order_payment_history, name="order-payment-history"),
    
    
]