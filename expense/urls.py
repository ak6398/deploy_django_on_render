from django.contrib import admin
from django.urls import path
from .views import *


urlpatterns = [
    path('signup/',signup,name='signup'),
    path('login/',login,name='login'),
    path('add_expense/',add_expense,name='add-expense'),
    path('manage_expense/<int:user_id>/',manage_expense,name='manage_expense'),
    # To update or delete a specific expense by its ID
    path('update_expense/<int:expense_id>/', expense_detail, name='expense_detail'),
    path('delete_expense/<int:expense_id>/', delete_expense, name='delete_expense'),
]