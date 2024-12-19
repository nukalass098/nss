from math import ceil
from django.shortcuts import render,redirect
from app.models import Accounts, Person, Transactions, Pending
from django.contrib.auth.decorators import login_required

@login_required
def home(request):
    return render(request, 'index.html')

@login_required
def daybook(request):
    farmers = Accounts.objects.filter(type = 'FARMER')
    farmers = [farmer.name for farmer in farmers]
    clients = Accounts.objects.filter(type = 'SALE')
    clients = [client.name for client in clients]
    data = {'farmers' : farmers, 'sales' : clients}
    if request.method == 'POST':

        fname = request.POST.get('farmer_name')
        cname = request.POST.get('client_name')
        qnt = int(request.POST.get('quantity'))
        price = int(request.POST.get('price'))
        date = request.POST.get('date')
        tot = qnt*price
        if fname not in farmers or cname not in clients:
            return render(request, 'error.html', {'error':'Name not registered'})
        e = Person(fname = fname, cname = cname, qnt = qnt, price = price,tot = tot , date=date)
        e.save()
        c_has = Transactions.objects.filter(name = cname, type = 'SALE', date = date)
        if not c_has:
            c = Transactions(name = cname, type = 'SALE', date = date, out_amt = tot)
            current = Accounts.objects.get(name=cname)
            current.balance = current.balance + tot
            print(current.balance)
            c.save()
            print(str(c.name) + ' ' + str(c.out_amt))
            current.save()
        else:
            c = Transactions.objects.get(name = cname, type = 'SALE', date = date)
            c .out_amt = c.out_amt + tot
            current = Accounts.objects.get(name=cname)
            current.balance = current.balance + tot
            print(current.balance)
            c.save()
            print(str(c.name) + ' ' + str(c.out_amt))
            current.save()
        
        has = Pending.objects.filter(name=fname, date=date)
        if not has:
            ele = Pending(name = fname, date = date)
            ele.save()
        return redirect('/newentry')
    else:
        return render(request, 'day_book.html', data)

@login_required
def table(request):
    farmers = Accounts.objects.filter(type = 'FARMER')
    farmers = [farmer.name for farmer in farmers]
    data = list(Person.objects.all())[::-1]
    if request.method == 'POST':
        name = request.POST.get('name')
        date = request.POST.get('date')
        if date and name:
            data = list(Person.objects.filter(fname = name, date=date))[::-1]
        elif not date and name:
            data = list(Person.objects.filter(fname = name))[::-1]
        elif not name and date:
            data = list(Person.objects.filter(date = date))[::-1]
        else:
            data = data
    return render(request, 'table.html', {'data':data, 'farmers' :farmers})

@login_required
def paper(request):
    if (request.method == 'POST'):
        name = request.POST.get('name')
        date = request.POST.get('date')
        if name == None and date == None:
            id = request.POST.get('id')
            records = Pending.objects.get(id=id)
            name = records.name
            date = records.date
        if name == '' or date == '':
            return render(request, 'error.html', {'error':'Enter Valid Details'})
        bill_data = Person.objects.filter(fname = name, date = date)
        if not bill_data:
            return render(request, 'error.html', {'error':'Record Not Found'})
        name = name.upper()
        try:
            ad = Transactions.objects.get(name=name, date=date, ad = 'True')
            ad = ad.out_amt
        except:
            ad = 0
        extra = {'name':name,'date':date,'sum':0,'lot':0, 'comm':0, 'others':10, 'advance':ad,'sub_tot':0, 'net':0}

        for record in bill_data:
            extra['sum'] += record.qnt * record.price
            extra['lot'] += record.qnt

        extra['comm'] = ceil(extra['sum'] * 0.1)
        extra['sub_tot'] = (extra['comm']+extra['advance']+extra['others'])
        extra['net'] = extra['sum'] - extra['sub_tot']
        added = Transactions.objects.filter(name=name, date=date, in_amt = extra['net'])
        if not added:
            current = Accounts.objects.get(name=name)
            current.balance = current.balance + extra['net']
            e = Transactions(name=name, date=date, in_amt = extra['net'], type='FARMER')
            current.save()
            e.save()
        data = {
            'bill': bill_data,
            'extra': extra,
        }
        return render(request, 'paper.html', data)
    else:
        return render(request, 'bills.html')

@login_required
def bills(request):
    farmers = Accounts.objects.filter(type = 'FARMER')
    farmers = [farmer.name for farmer in farmers]
    data = {'farmers' : farmers}
    return render(request, 'bills.html', data)

@login_required
def delete(request):
    if request.method == 'POST':
        id = request.POST.get('id')
        tup = Person.objects.get(id=id)
        try:
            e = Transactions.objects.get(name = tup.cname, date = tup.date, type='SALE', in_amt = 'NULL')
            e.out_amt = e.out_amt - tup.tot
            e.save()
            current = Accounts.objects.get(name=tup.cname)
            current.balance = current.balance - tup.tot
            current.save()
        except:
            pass
        tup.delete()
        return redirect('/bills')
    return render(request, 'index.html')

@login_required
def sales(request):
    return render(request, 'sales.html')

@login_required
def add(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        type = request.POST.get('type')
        e = Accounts(name = name,type = type, balance = 0)
        e.save()
        return redirect('add')
    else:
        return render(request, 'add.html')

@login_required
def transactions(request):
    farmers = Accounts.objects.filter(type = 'FARMER')
    farmers = [farmer.name for farmer in farmers]
    clients = Accounts.objects.filter(type = 'SALE')
    clients = [client.name for client in clients]
    farmers = farmers + clients
    data = {'farmers' : farmers}
    if request.method == 'POST':
        name = request.POST.get('name')
        if name not in farmers:
            return render(request, 'error.html', {'error':'Name not registered'})
        date = request.POST.get('date')
        out_amt = int(request.POST.get('amount'))
        is_ad = request.POST.get('ad_check')
        type = request.POST.get('type')
        ad= 'True' if is_ad == 'on' else 'False';
        data1 = Transactions.objects.filter(name=name, date=date, ad=ad, type=type, out_amt = out_amt)
        if type == 'SALE':
            data1 = Transactions.objects.filter(name=name, date=date, ad=ad, type=type, in_amt = out_amt)
        if not data1:
            if type == 'SALE':
                e = Transactions(name=name, date=date,in_amt = out_amt, ad=ad, type=type)
                e.save()
            else:
                e = Transactions(name=name, date=date,out_amt = out_amt, ad=ad, type=type)
                e.save()
            
            current = Accounts.objects.get(name=name)
            current.balance = current.balance - out_amt
            current.save()
            return redirect('transactions')
        else:
            if type == 'SALE':
                data1 = Transactions.objects.get(name=name, date=date, ad=ad, type=type, in_amt = out_amt)
            else:
                data1 = Transactions.objects.get(name=name, date=date, ad=ad, type=type, out_amt = out_amt)
            text = 'Record Already Entered' + "   id : " + str(data1.id)
            return render(request, 'error.html', {'error':text})
    return render(request, 'transactions.html', data)

@login_required
def accounts(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        type = request.POST.get('type')
        transactions = list(Transactions.objects.filter(name = name, type=type))[::-1]
        acc = Accounts.objects.get(name = name, type=type)
        return render(request, 'accounts.html', {'data':transactions, 'acc':acc})
    else:
        return render(request, 'acc_search.html')

@login_required
def acc_search(request):
    farmers = Accounts.objects.filter(type = 'FARMER')
    farmers = [farmer.name for farmer in farmers]
    data = {'farmers' : farmers}
    return render(request, 'acc_search.html')

@login_required
def print_all(request):
    if request.method == 'POST':
        date = request.POST.get('date')
        eles = Person.objects.filter(date=date)
        eles = list(eles)
        lis = []
        for ele in eles:
            lis.append(ele.cname)
        date = '-'.join(date.split('-')[::-1])
        return render(request, 'print_all.html', {'data':set(lis), 'date':date})
    return render(request, 'print_all.html', {'data':{}, 'date':''})

@login_required
def pending(request):
    farmers = Accounts.objects.filter(type = 'FARMER')
    farmers = [farmer.name for farmer in farmers]
    data = list(Pending.objects.all())
    if request.method == 'POST':
        name = request.POST.get('name')
        if name: 
            data = list(Pending.objects.filter(name=name))
    return render(request, 'pending.html', {'data':data, 'farmers':farmers})


@login_required
def paper_bill(request):
    if (request.method == 'POST'):
        name = request.POST.get('name')
        date = request.POST.get('date')
        if name == None and date == None:
            id = request.POST.get('id')
            records = Pending.objects.get(id=id)
            name = records.name
            date = records.date
            records.delete()
        if name == '' or date == '':
            return render(request, 'error.html', {'error':'Enter Valid Details'})
        bill_data = Person.objects.filter(fname = name, date = date)
        if not bill_data:
            return render(request, 'error.html', {'error':'Record Not Found'})
        name = name.upper()
        try:
            ad = Transactions.objects.get(name=name, date=date, ad = 'True')
            ad = ad.out_amt
        except:
            ad = 0
        extra = {'name':name,'date':date,'sum':0,'lot':0, 'comm':0, 'others':10, 'advance':ad,'sub_tot':0, 'net':0}

        for record in bill_data:
            extra['sum'] += record.qnt * record.price
            extra['lot'] += record.qnt

        extra['comm'] = ceil(extra['sum'] * 0.1)
        extra['sub_tot'] = (extra['comm']+extra['advance']+extra['others'])
        extra['net'] = extra['sum'] - extra['sub_tot']
        added = Transactions.objects.filter(name=name, date=date, in_amt = extra['net'])
        if not added:
            current = Accounts.objects.get(name=name, type='FARMER')
            current.balance = current.balance + extra['net']
            e = Transactions(name=name, date=date, in_amt = (extra['net']-add-10), type='FARMER')
            current.save()
            e.save()
        data = {
            'bill': bill_data,
            'extra': extra,
        }
        return render(request, 'paper_bill.html', data)
    else:
        return render(request, 'pending.html')


@login_required
def delete_pay(request):
    if request.method == 'POST':
        id = request.POST.get('id')
        tran = Transactions.objects.get(id = id)
        if tran.type == 'SALE':
            current = Accounts.objects.get(name=tran.name)
            current.balance = current.balance - tran.out_amt
            current.save()
        else:
            current = Accounts.objects.get(name=tran.name)
            current.balance = current.balance - tran.out_amt
            current.save()
        tran.delete()
        return redirect('transactions')
    return render('transactions')