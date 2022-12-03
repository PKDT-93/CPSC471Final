from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.contrib.auth import authenticate, login
from django.http import HttpResponse
from django.template import loader
from .models import Item
from django.db import connection

def index(request):
    print(request.user)
    return render(request, 'index.html')

def customerlist(request):
    template = loader.get_template('customerlist.html')
    with connection.cursor() as cursor:
        cursor.execute("SELECT ID, FirstName, LastName, Email FROM Person WHERE Customer = 1")
        row = cursor.fetchall()
        context = {
            'row': row,
        }
    print(row)
    return HttpResponse(template.render(context, request))


def findemployee(request):
    template = loader.get_template('findemployee.html')
    with connection.cursor() as cursor:
        cursor.execute("SELECT Employee.StoreID, Employee.PersonID, Employee.ESSN, Person.FirstName, Person.LastName, Person.Email FROM Employee, Person WHERE Employee.PersonID = ID")
        row = cursor.fetchall()
        context = {
            'row': row,
        }
    print(row)
    return HttpResponse(template.render(context, request))
    #return render(request, 'findemployee.html')


def items(request):
    template = loader.get_template('items.html')
    with connection.cursor() as cursor:
        cursor.execute("SELECT Item.ItemID, Item.Barcode, Item.Weight, Item.Price, Item.Type, SoldAt.StoreID, SoldAt.Stock FROM Item, SoldAt WHERE Item.ItemID = SoldAt.ItemID")
        row = cursor.fetchall()
        context = {
            'row': row,
        }
    print(row)
    return HttpResponse(template.render(context, request))

def supplier(request): 
    template = loader.get_template('supplier.html')
    with connection.cursor() as cursor:
        cursor.execute("SELECT * FROM Supplier")
        row = cursor.fetchall()
        context = {
            'row': row,
        }
    print(row)
    return HttpResponse(template.render(context, request))


def store(request): 
    template = loader.get_template('store.html')
    with connection.cursor() as cursor:
        cursor.execute("SELECT * FROM Store")
        row = cursor.fetchall()
        context = {
            'row': row,
        }
    print(row)
    return HttpResponse(template.render(context, request))

def rawInventory(request): 
    template = loader.get_template('store.html')
    with connection.cursor() as cursor:
        cursor.execute("SELECT * FROM Gems")
        row = cursor.fetchall()
        context = {
            'row': row,
        }
    print(row)
    return HttpResponse(template.render(context, request))