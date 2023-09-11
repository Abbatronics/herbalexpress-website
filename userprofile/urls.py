#from django.contrib.auth import views as auth_views
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from . import views
from django.contrib.auth import views as auth_view
from django.contrib.staticfiles.urls import staticfiles_urlpatterns


urlpatterns = [
    path('signup/', views.signup, name='signup'),
    path('login/', views.custom_login, name='login'),
    path('logout/', views.custom_logout, name='logout'),
    path('activate/<uidb64>/<token>/', views.activate, name='activate'),
    path('password_reset', views.password_reset_request, name='password_reset'),
     path('password_reset_done/', auth_view.PasswordResetDoneView.as_view(template_name='userprofile/password_reset_done.html'),
         name='password_reset_done'),
    path('password_reset_confirm/<uidb64>/<token>/', auth_view.PasswordResetConfirmView.as_view(template_name='userprofile/password_reset_confirm.html'),
         name='password_reset_confirm'),
    path('password_reset_complete/', auth_view.PasswordResetCompleteView.as_view(template_name='userprofile/password_reset_complete.html'),
         name='password_reset_complete'),
    path('profile/', views.profile, name='profile'),
    path('account/', views.account, name='account'),
    path('my_store/', views.my_store, name='my_store'),
    path('my-store/order-detail/<int:pk>/', views.my_store_order_detail, name='my_store_order_detail'),
    path('my-store/add-product/', views.add_product, name='add_product'),
    path('my-store/edit-product/<int:pk>/', views.edit_product, name='edit_product'),
    path('my-store/delete-product/<int:pk>/', views.delete_product, name='delete_product'),
    path('vendors/<int:pk>/', views.vendor_detail, name='vendor_detail'),
]


urlpatterns += staticfiles_urlpatterns()
if settings.DEBUG:
     urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT ) 