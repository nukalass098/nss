from django.contrib import admin
from django.urls import path
from .import views

urlpatterns = [
    path('', views.home, name='home'),
    path('newentry', views.daybook, name='newentry'),
    path('daybook', views.table, name='daybook'),
    path('paper', views.paper, name='bill'),
    path('bills', views.bills, name='bills'),
    path('delete', views.delete, name='delete'),
    path('add', views.add, name='add'),
    path('transactions', views.transactions, name='transactions'),
    path('accounts', views.accounts, name='accounts'),
    path('acc_search', views.acc_search, name='acc_search'),
    path('print_all', views.print_all, name='print_all'),
    path('pending', views.pending, name='pending'),
    path('paper_bill', views.paper_bill, name='paper_bill'),
    path('delete_pay', views.delete_pay, name='delete_pay'),
    path('client_bill', views.client_bill, name='client_bill'),
    path('advance', views.advance, name = 'advance'),
    path('acc_statement', views.acc_statement, name='acc_statement'),
    path('submit', views.submit, name='submit'),
    path('summary', views.summary, name = 'summary'),
    path('bills_given', views.bills_given, name = 'bills_given'),
    path('delete_bill', views.delete_bill, name = 'delete_bill'),
    path('check', views.check, name='check'),
    path('balance', views.balance, name='balance'),
    path('balance_list', views.balance_list, name='balance_list'),
    path('balance_delete', views.balance_delete, name='balance_list')
]
