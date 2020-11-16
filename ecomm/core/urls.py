from django.urls import path
from . import views
app_name = 'core'
urlpatterns = [
    path('',views.Home.as_view(),name="home"),
    path('product_detail/<slug>/',views.ItemDetailView.as_view(),name='product'),
    path('add_cart/<slug>/',views.add_cart,name="add_cart"),
    path('remove_one_cart/<slug>/',views.remove_one_cart,name="remove_one_cart"),
    path('detailed_summary',views.DetailedMinxin.as_view(),name="detailed_summary"),
    path('remove_cart/<slug>/',views.remove_cart,name="remove_cart"),
    path('checkout/' ,views.CheckoutView.as_view(),name="checkout"),
    path('payment/<payment_method>/' ,views.PaymentView.as_view(),name="payment"),
    path('cupon/',views.cupon,name="cupon"),
    path('refund/' ,views.RefundView.as_view(),name="refund"),
    path('dashbord' ,views.user_dashboard,name="dashbord"),
    path('search/' ,views.search_item,name="search"),

    # path('search/' ,views.SearchView.as_view() ,name="search"),


]

