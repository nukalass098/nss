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
        has = Pending.objects.filter(name = fname, date = date, pending = True)
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
def advance(request):
    farmers = Accounts.objects.filter(type = 'FARMER')
    farmers = [farmer.name for farmer in farmers]
    clients = Accounts.objects.filter(type = 'SALE')
    clients = [client.name for client in clients]
    farmers = farmers + clients
    if request.method == 'POST':
        name = request.POST.get('name')
        date = request.POST.get('date')
        if date and name:
            data = list(Transactions.objects.filter(name = name, date=date, ad = true, type = 'FARMER'))[::-1]
        elif not date and name:
            data = list(Person.objects.filter(name = name, ad = True, type = 'FARMER'))[::-1]
        elif not name and date:
            data = list(Person.objects.filter(date = date, ad = true, type = 'FARMER'))[::-1]
        else:
            data = data
    return render(request, 'advance.html', {'data':data, 'farmers' :farmers})

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
        data = date.split('-')[::-1]
        extra = {'vocher':'**','name':name,'date':'-'.join(date.split('-')[::-1]),'sum':0,'lot':0, 'comm':0, 'others':10, 'advance':ad,'sub_tot':0, 'net':0}
        record = list(Pending.objects.filter(name = name, date = date))
        if record:
            record = record[-1]
            extra['vocher'] = str(record.id)
        else:
            extra['vocher'] = '**'
        for record in bill_data:
            extra['sum'] += record.qnt * record.price
            extra['lot'] += record.qnt

        extra['comm'] = ceil(extra['sum'] * 0.1)
        extra['sub_tot'] = (extra['comm']+extra['advance']+extra['others'])
        extra['net'] = extra['sum'] - extra['sub_tot']
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
        # try:
        #     print("0")
        #     e = Transactions.objects.get(name = tup.fname, date = tup.date, type='FARMER', out_amt = None)
        #     e.delete()
        #     print("1")
        #     e = Transactions.objects.get(name = tup.cname, date = tup.date, type='SALE', in_amt = None)
        #     print("2")
        #     e.out_amt -= tup.tot
        #     print("3")
        #     e.save()
        #     print("4")
        # except:
        #     print("5")
        #     pass
        # try:
        #     record = list(Pending.objects.filter(name = tup.name, date = tup.date, pending = False))[-1]
        #     record.pending = True
        # except:
        #     pass
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
        typed = request.POST.get('type')
        ad= 'True' if is_ad == 'on' else 'False'
        data1 = Transactions.objects.filter(name=name, date=date, ad=ad, type=typed, in_amt = None)
        if typed == 'SALE':
            data1 = Transactions.objects.filter(name=name, date=date, ad=ad, type=typed, out_amt = None)
        if not data1:
            if typed == 'SALE':
                e = Transactions(name=name, date=date,in_amt = out_amt, ad=ad, type=typed)
                e.save()
            else:
                e = Transactions(name=name, date=date,out_amt = out_amt, ad=ad, type=typed)
                e.save()
            return redirect('transactions')
        else:
            if typed == 'SALE':
                data1 = Transactions.objects.get(name=name, date=date, ad=ad, type=typed, out_amt = None)
            else:
                data1 = Transactions.objects.get(name=name, date=date, ad=ad, type=typed, in_amt = None)
            text = 'Record Already Entered' + "   id : " + str(data1.id)
            return render(request, 'error.html', {'error':text})
    return render(request, 'transactions.html', data)

@login_required
def accounts(request):
    farmers = Accounts.objects.filter(type = 'FARMER')
    farmers = [farmer.name for farmer in farmers]
    clients = Accounts.objects.filter(type = 'SALE')
    clients = [client.name for client in clients]
    data = {'farmers' : farmers, 'sales' : clients}
    if request.method == 'POST':
        name = request.POST.get('name')
        type = request.POST.get('type')
        transactions = list(Transactions.objects.filter(name = name, type=type))[::-1]
        acc = Accounts.objects.get(name = name, type=type)
        return render(request, 'accounts.html', {'data':transactions, 'acc':acc})
    else:
        return render(request, 'acc_search.html', data)

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
    data = list(Pending.objects.filter(pending = True))
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
            if not id:
                return redirect('bills')
            try:
                records = Pending.objects.get(id=id)
                name = records.name
                date = records.date
                records.pending = False
                records.save()
            except:
                return render(request, 'error.html', {'error':'Invalid action'})
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
        extra = {'vocher':'**','name':name,'date':'-'.join(str(date).split('-')[::-1]),'sum':0,'lot':0, 'comm':0, 'others':10, 'advance':ad,'sub_tot':0, 'net':0}
        record = list(Pending.objects.filter(name = name, date = date))
        if record:
            record = record[-1]
        else:
            extra['vocher'] = '**'
        extra['vocher'] = str(record.id)
        for record in bill_data:
            extra['sum'] += record.qnt * record.price
            extra['lot'] += record.qnt

        extra['comm'] = ceil(extra['sum'] * 0.1)
        extra['sub_tot'] = (extra['comm']+extra['advance']+extra['others'])
        extra['net'] = extra['sum'] - extra['sub_tot']
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
        tran.delete()
        return redirect('transactions')
    return render('transactions')

def client_bill(request):
    clients = Accounts.objects.filter(type = 'SALE')
    clients = [client.name for client in clients]
    if request.method == 'POST':
        name = request.POST.get('name')
        date = request.POST.get('date')
        bags = int(request.POST.get('bags'))  if request.POST.get('bags') else 0
        hamali = 1 if request.POST.get('hamali') else 0
        if name == '' or date == '':
            return render(request, 'error.html', {'error':'Enter Valid Details'})
        bill_data = Person.objects.filter(cname = name, date = date)
        if not bill_data:
            return render(request, 'error.html', {'error':'Record Not Found'})
        name = name.upper()
        extra = {'name':name,'date':'-'.join(str(date).split('-')[::-1]),'sum':0,'lot':0, 'bags':0, 'hamali' : 0, 'others':10, 'sub_tot':0, 'net':0, 'bcou':bags, 'cash':0}
        extra['bags'] = int(bags) * 30
        for record in bill_data:
            extra['sum'] += record.qnt * record.price
            extra['lot'] += record.qnt
        extra['hamali'] = int(hamali) * 15 * extra['lot']
        try:
            e = Transactions.objects.get(name = name, date = date, type = 'SALE', out_amt = None)
            extra['cash'] = e.in_amt
        except:
            extra['cash']  = 0
            extra['sub_tot'] = (extra['hamali']+extra['others']+extra['bags'] - extra['cash'])
            extra['net'] = extra['sum'] + extra['sub_tot']
        data = {
            'bill': bill_data,
            'extra': extra,
            'clients' : clients
        }
        return render(request, 'client_paper.html', data)
    else:
        return render(request, 'client_bills.html', {'clients' : clients})
