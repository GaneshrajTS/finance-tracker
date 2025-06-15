from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard_view, name='dashboard'),
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('add/', views.add_transaction_view, name='add_transaction'),
    path('edit/<int:pk>/', views.edit_transaction_view, name='edit_transaction'),
    path('delete/<int:pk>/', views.delete_transaction_view, name='delete_transaction'),
    path('category/add/', views.add_category_view, name='add_category'),
    path('export/excel/', views.export_transactions_excel, name='export_excel'),

]

