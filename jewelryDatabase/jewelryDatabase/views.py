from pyexpat.errors import messages
from django.shortcuts import redirect, render
from django.urls import reverse
from django.contrib.auth import authenticate, login
from django.http import HttpResponse
from django.template import loader
from django.db import connection

# Home Page
def index(request):
    print(request.user)
    return render(request, 'index.html')

# Retrieves list of customers
def customerlist(request):
    template = loader.get_template('customerlist.html')
    with connection.cursor() as cursor:
        cursor.execute(
            "SELECT ID, FirstName, LastName, Email FROM Person WHERE Customer = 1")
        row = cursor.fetchall()
        context = {
            'row': row,
        }
    return HttpResponse(template.render(context, request))

# Add customer function, render webpage when url is accessed, when form is POSTED insert into Person Table as a customer
def addCustomer(request):
    if request.method == 'POST':
        firstname = request.POST.get('firstname', None)
        lastname = request.POST.get('lastname', None)
        email = request.POST.get('email', None)
        customer = 1
        with connection.cursor() as cursor:
            cursor.execute("INSERT INTO Person (FirstName, LastName, Email, Customer) VALUES (%s, %s, %s, %s)",
                           (firstname, lastname, email, customer))
            return redirect('/customerlist')
    return render(request, 'customers/addcustomer.html')

# View Employee table function, only accessible to managers.
def findemployee(request):
    if not request.user.is_superuser:
        return redirect('/')

    template = loader.get_template('findemployee.html')
    with connection.cursor() as cursor:
        cursor.execute(
            """SELECT Employee.StoreID, Employee.PersonID, Employee.ESSN, Person.FirstName, Person.LastName, Person.Email
            FROM Employee, Person WHERE Employee.PersonID = ID ORDER BY Employee.PersonID""")
        row = cursor.fetchall()
        context = {
            'row': row,
        }
    return HttpResponse(template.render(context, request))

# Purchase history query through mulitple joins from various table and render result on webpage
def purchaseHistory(request):
    template = loader.get_template('purchase.html')
    with connection.cursor() as cursor:
        cursor.execute(
            """SELECT P.FirstName, P.LastName, P.Email, P.RecieptID, P.Price, P.PaymentTender, P.Warranty, P.PaymentDate, P.TimeOfPay, P.StoreID, P.PersonID, PI.ItemID, PI.ItemBarcode, PS.ServiceID
                FROM (SELECT Person.FirstName, Person.LastName, Person.Email, Purchase.RecieptID, Purchase.Price, Purchase.PaymentTender, Purchase.Warranty, Purchase.PaymentDate, Purchase.TimeOfPay, Purchase.StoreID, Purchase.PersonID
                FROM Purchase JOIN Person ON Person.ID = Purchase.PersonID) AS P LEFT OUTER JOIN PurchaseService AS PS ON PS.RecieptID = P.RecieptID LEFT OUTER JOIN PurchaseItem AS PI ON P.RecieptID = PI.RecieptID GROUP BY P.RecieptID, P.PersonID""")
        row = cursor.fetchall()
        context = {
            'row': row,
        }
    return HttpResponse(template.render(context, request))

# Add new purchase function, render webpage when url is accessed, when form is POSTED insert into Purchase Table with form values passed as string value.
def addpurchase(request):
    if request.method == 'POST':
        recieptID = request.POST.get('recieptID', None)
        price = request.POST.get('price', None)
        warranty = request.POST.get('warranty', None)
        paymentTender = request.POST.get('paymentTender', None)
        store = request.POST.get('storeID', None)
        person = request.POST.get('personID', None)
        with connection.cursor() as cursor:
            date = cursor.execute("SELECT DATE('now')")
            cursor.execute(
                "INSERT INTO Purchase (RecieptID, Price, PaymentTender, Warranty, PaymentDate, TimeOfPay, StoreID, PersonID) VALUES (%s, %s, %s, %s, DATE('now'), TIME(), %s, %s)", (recieptID, price, paymentTender, warranty, store, person))
            return redirect('/purchase')
    return render(request, 'purchase/addPurchase.html')

# Render all items that have inventory & store located where it is sold on page when accessed
def items(request):
    template = loader.get_template('items.html')
    with connection.cursor() as cursor:
        cursor.execute(
            "SELECT Item.ItemID, Item.Barcode, Item.Weight, Item.Price, Item.Type, SoldAt.StoreID, SoldAt.Stock FROM Item, SoldAt WHERE SoldAt.ItemID = Item.ItemID")
        row = cursor.fetchall()
        context = {
            'row': row,
        }
    return HttpResponse(template.render(context, request))

# When user searches for an item type, redirect to new lookup page where all items of that type are queried and displayed
def filterItem(request):
    searchWord = request.POST.get('system', None)
    template = loader.get_template('items/lookup.html')
    with connection.cursor() as cursor:
        cursor.execute(
            "SELECT Item.ItemID, Item.Barcode, Item.Weight, Item.Price, Item.Type, SoldAt.StoreID, SoldAt.Stock FROM Item, SoldAt WHERE SoldAt.ItemID = Item.ItemID AND Item.Type = %s", [searchWord])
        row = cursor.fetchall()
        context = {
            'row': row,
        }
    return HttpResponse(template.render(context, request))

# Page only accessible to managers, query all listed suppliers in the databse with a listed id, name, email, areacode, phone number
def supplier(request):
    if not request.user.is_superuser:
        return redirect('/')
    else:
        template = loader.get_template('supplier.html')
        with connection.cursor() as cursor:
            cursor.execute("SELECT Supplier.SupplierID, Supplier.SupplierName, Supplier.SupplierEmail, SupplierPhone.AreaCode, SupplierPhone.PhoneNo FROM Supplier JOIN SupplierPhone ON Supplier.SupplierID = SupplierPhone.SupplierID")
            row = cursor.fetchall()
            context = {
                'row': row,
            }
        return HttpResponse(template.render(context, request))

# Page only accessible to managers, grabs supplierID from user form and passes into deletion query as a string argument and redirect to supplier page
# Render webpage otherwise if there is no POST request.
def deleteSupplier(request):
    if not request.user.is_superuser:
        return redirect('/')
        
    if request.method == 'POST':
        supplierID = request.POST.get('deletesupplier', None)
        with connection.cursor() as cursor:
            cursor.execute(
                "DELETE FROM Supplier WHERE SupplierID = %s", [supplierID])
            return redirect('/supplier')
    return render(request, 'suppliers/deletesupplier.html')

# Render store location page 
def store(request):
    template = loader.get_template('store.html')
    with connection.cursor() as cursor:
        cursor.execute("SELECT * FROM Store, StorePhone WHERE Store.StoreID = StorePhone.StoreID")
        row = cursor.fetchall()
        context = {
            'row': row,
        }
    return HttpResponse(template.render(context, request))

# Render raw inventory page via outerjoins from tables containing Metals/Gems
def rawInventory(request):
    template = loader.get_template('rawInventory.html')
    with connection.cursor() as cursor:
        cursor.execute("""SELECT S.SupplierID, S.SupplierName, M.BatchNo, M.MetalType, M.Quantity, M.Price, M.Karat, G.CertificateNo, G.GemType, G.Carat, G.Cut, G.Price FROM
        (SELECT * FROM Supplier, Supplies WHERE Supplier.SupplierID = Supplies.SupplierID) AS S 
        LEFT OUTER JOIN Metals AS M ON M.BatchNo = S.BatchNo 
        LEFT OUTER JOIN Gems AS G ON G.CertificateNo = S.CertificateNo""")
        row = cursor.fetchall()
        context = {
            'row': row,
        }
    return HttpResponse(template.render(context, request))

# Page accessible to managers only, grab employee information from user form and insert into the person table if form is POSTED. After insertion into Person table, the newly generated Key/ID is obtained
# and the rest of the required user arguments are inserted into the Employee table. 
def addEmployee(request):
    if not request.user.is_superuser:
        return redirect('/')
    if request.method == 'POST':
        firstname = request.POST.get('firstname', None)
        lastname = request.POST.get('lastname', None)
        email = request.POST.get('email', None)
        storeid = request.POST.get('storeid', None)
        ssn = request.POST.get('ssn', None)
        with connection.cursor() as cursor:
            cursor.execute(
                "INSERT INTO Person (FirstName, LastName, Email, Customer) Values (%s, %s, %s, %s)", (firstname, lastname, email, 0)
            )
            cursor.execute("SELECT ID FROM Person WHERE Person.Email = %s", [email])
            val = cursor.fetchone()
            output = int (val[0])
            cursor.execute("INSERT INTO Employee (StoreID, PersonID, ESSN) Values (%s, %s, %s)", (storeid, output, ssn))
            return redirect('/findemployee')    
    return render(request,'employees/addemployee.html')

# Page accessible to managers only, removes PersonID from Employee based on the user input argument and updates the Person table by setting the deleted employee as a customer
def deleteEmployee(request):
    if not request.user.is_superuser:
        return redirect('/')
    if request.method == 'POST':
        id = request.POST.get('personid', None)
        with connection.cursor() as cursor:
            cursor.execute("DELETE FROM Employee WHERE Employee.PersonID = %s", [id])
            cursor.execute("UPDATE Person SET Customer = 1 WHERE ID = %s", [id])
            return redirect('/findemployee')
    return render(request, 'employees/deleteEmployee.html')

# If form is POSTED, Update Person table based on the inputted user key and the newly inputted email address. Otherwise render webpage.
def updateEmail(request):
    if request.method == 'POST':
        id = request.POST.get('id')
        email = request.POST.get('email')
        with connection.cursor() as cursor:
            cursor.execute("UPDATE Person SET Email = %s WHERE ID = %s", (email,id))
            return redirect('/customerlist')
    return render(request, 'customers/updateemail.html')

# Page accessible to superusers only. If form is posted update Person table with new email address based on id key passed in as user argument. Otherwise render webpage.
def updateEmployeeEmail(request):
    if not request.user.is_superuser:
        return redirect('/')
        
    if request.method == 'POST':
        id = request.POST.get('id')
        email = request.POST.get('email')
        with connection.cursor() as cursor:
            cursor.execute("UPDATE Person SET Email = %s WHERE ID = %s", (email,id))
            return redirect('/findemployee')
    return render(request, 'employees/updateemail.html')

# If user form is POSTED, pass user arguments into INSERT INTO query that inserts a new item into the Item Table. Then retrieve the ItemID of the newly created Item to then
# insert the rest of the user arguments into the SoldAt Table. Otherwise render webpage.
def addItem(request):
    if request.method == 'POST':
        barcode = request.POST.get('barcode', None)
        weight = request.POST.get('weight', None)
        price = request.POST.get('price', None)
        type = request.POST.get('type', None)
        stock = request.POST.get('stock', None)
        store = request.POST.get('store', None)
        with connection.cursor() as cursor:
            cursor.execute(
                "INSERT INTO Item (Barcode, Weight, Price, Type) VALUES (%s, %s, %s, %s)", (barcode, weight, price, type))
            cursor.execute("SELECT ItemID FROM Item WHERE Item.Barcode = %s", [barcode])
            val = cursor.fetchone()
            output = int (val[0])
            cursor.execute("INSERT INTO SoldAt(StoreID, ItemID, ItemBarcode, Stock) VALUES (%s, %s, %s, %s)", (store, output, barcode, stock))
            return redirect('/items')
    return render(request, 'items/additem.html')

# If user form is POSTED, use user arguments to update the SoldAt table where the user inputted ItemID & storeid key is used to set the amount of the item on hand. Otherwise render webpage.
def changeInventory(request):
    if request.method == 'POST':
        itemid = request.POST.get('itemid', None)
        storeid = request.POST.get('storeid', None)
        amount = request.POST.get('amount', None)
        with connection.cursor() as cursor:
            cursor.execute("UPDATE SoldAt SET Stock = %s WHERE StoreID = %s AND ItemID = %s", (amount, storeid, itemid))
            return redirect('/items')
    return render(request, 'items/changeinventory.html')

# def deleteItem(request):
#     if request.method == 'POST':
#         itemid = request.POST.get('deleteitem', None)
#         with connection.cursor() as cursor:
#             cursor.execute("DELETE FROM Item WHERE Item.ItemID = %s", [itemid])
#             return redirect('/items')
#     return render(request, 'items/deleteitem.html')

# Same implementation of addItem but inserts into Supplier Table and then Insert Into SupplierPhone with the rest of the user form inputs. 
def addSupplier(request):
    if not request.user.is_superuser:
        return redirect('/')
    if request.method == 'POST':
        suppliername = request.POST.get('SupplierName', None)
        supplieremail = request.POST.get('SupplierEmail', None)
        areacode = request.POST.get('areacode', None)
        supplierphone = request.POST.get('phonenumber', None)
        with connection.cursor() as cursor: 
            cursor.execute(
                "INSERT INTO Supplier (SupplierName, SupplierEmail) VALUES (%s, %s)", (suppliername, supplieremail)
            )
            cursor.execute("SELECT SupplierID FROM Supplier WHERE Supplier.SupplierEmail = %s", [supplieremail])
            val = cursor.fetchone()
            output = int (val[0])
            cursor.execute("INSERT INTO SupplierPhone(SupplierID, PhoneNo, AreaCode) VALUES (%s, %s, %s)", (output, supplierphone, areacode))
            return redirect('/supplier')
    return render(request, 'suppliers/addsupplier.html')

# If user form is POSTED, use user arguments to insert into the Gems table with the user inputted values. Otherwise rendere webpage.
def addGem(request):
    if request.method == 'POST':
        ID = request.POST.get('ID', None)
        no = request.POST.get('CertificateNo', None)
        type = request.POST.get('GemType', None)
        carat = request.POST.get('Carat', None)
        cut = request.POST.get('Cut', None)
        price = request.POST.get('Price', None)
        with connection.cursor() as cursor:
            cursor.execute(
                "INSERT INTO Gems (CertificateNo, GemType, Carat, Cut, Price) VALUES (%s, %s, %s, %s, %s)", (no, type, carat, cut, price))
            cursor.execute("INSERT INTO Supplies (SupplierID, CertificateNo, BatchNo) VALUES (%s, %s, NULL)", (ID, no))
            return redirect('/rawInventory')
    return render(request, 'rawInventory/addGem.html')

# Same implementation as addGem
def addMetal(request):
    if request.method == 'POST':
        ID = request.POST.get('ID', None)
        no = request.POST.get('CertificateNo', None)
        type = request.POST.get('MetalType', None)
        quantity = request.POST.get('quantity', None)
        karat = request.POST.get('karat', None)
        price = request.POST.get('Price', None)
        with connection.cursor() as cursor:
            cursor.execute(
                "INSERT INTO Metals (BatchNo, MetalType, Quantity, Price, Karat) VALUES (%s, %s, %s, %s, %s)", (no, type, quantity, karat, price))
            cursor.execute("INSERT INTO Supplies (SupplierID, CertificateNo, BatchNo) VALUES (%s, NULL, %s)", (ID, no))
            return redirect('/rawInventory')
    return render(request, 'rawInventory/addMetal.html')

# Render addresses webpage and query all items from PersonAddress table
def address(request):
    template = loader.get_template('addresses.html')
    with connection.cursor() as cursor:
        cursor.execute("SELECT * FROM PersonAddress")
        row = cursor.fetchall()
        context = {
            'row': row,
        }
    return HttpResponse(template.render(context, request))

# Render managers page and queries all store managers from StoreManages table and Manager table to show attributes from both.
def managers(request):
    template = loader.get_template('managers.html')
    with connection.cursor() as cursor:
        cursor.execute("""SELECT P.ID, SM.StoreID, P.FirstName, P.LastName, P.Email, M.MSSN, M.CreditCard
        FROM StoreManages AS SM JOIN Manager AS M ON M.PersonID = SM.ManagerID JOIN Person as P ON M.PersonID = P.ID""")
        row = cursor.fetchall()
        context = {
            'row': row,
        }
    return HttpResponse(template.render(context, request))

# Renders services webpage and queries all item from Service table.
def services(request):
    template = loader.get_template('services.html')
    with connection.cursor() as cursor:
        cursor.execute("SELECT * FROM Service")
        row = cursor.fetchall()
        context = {
            'row': row,
        }
    return HttpResponse(template.render(context, request))