from django.contrib import admin
from django.urls import path
from accounts import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('',views.outer_login,name= 'outer_login'),
    path('dashboard/',views.dashboard, name='dashboard'),
    path('masters/users/', views.user_form, name='user_form'),
    path('masters/users/<int:user_id>/toggle/', views.toggle_status, name='toggle_status'),
    path('masters/users/<int:user_id>/reset/', views.reset_password, name='reset_password'),
    path('masters/users/<int:user_id>/edit/', views.edit_user, name='edit_user'),

    path('masters/company-master/',views.company_master, name='company_master'),
    path('toggle-company-status/<int:company_id>/', views.toggle_company_status, name='toggle_company_status'),

    path('masters/dealer-master/',views.dealer_master, name='dealer_master'),
    path('toggle-dealer-status/<int:dealer_id>/', views.toggle_dealer_status, name='toggle_dealer_status'),

    path('masters/tax-master/', views.tax_master, name='tax_master'),
    path('delete-tax/<int:tax_id>/', views.delete_tax, name='delete_tax'),

    path('masters/item-category/', views.item_category, name='item_category'),
    path('masters/item-category/toggle/<int:pk>/', views.toggle_item_category_status, name='toggle_item_category_status'),

    path('masters/item-subcategory/', views.item_subcategory, name='item_subcategory'),
    path('masters/item-subcategory/toggle/<int:pk>/', views.toggle_subcategory_status, name='toggle_subcategory_status'),

    path('masters/item-master/', views.item_master, name='item_master'),
    path('masters/item-master/toggle/<int:pk>/', views.toggle_item_status, name='toggle_item_status'),

    path('create-bill/', views.create_bill, name='create_bill'),

    path('logout',views.logout_view, name='logout'),
]
'''
path('',views.login_view, name='login'),
    path('register',views.register_view, name='register'),
    path('logout',views.logout_view, name='logout'),
'''
if settings.DEBUG: 
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
