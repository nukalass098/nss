from math import ceil
from django.shortcuts import render,redirect
from app.models import Accounts, Person, Transactions, Pending, Submit
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
    try:
        top = list(Person.objects.all())[-1]
    except:
        top = []
    data = {'farmers' : farmers, 'sales' : clients, 'data':top}
    if request.method == 'POST':
        fname = request.POST.get('farmer_name')
        cname = request.POST.get('client_name')
        qnt = int(request.POST.get('quantity'))
        price = int(request.POST.get('price'))
        date = request.POST.get('date')
        tot = qnt*price
        try:
            ele = Submit.objects.get(name = fname, date = date)
        except:
            ele = Submit(name = fname, date = date)
            ele.save()
        if fname not in farmers or cname not in clients:
            return render(request, 'error.html', {'error':'Name not registered'})
        e = Person(fname = fname, cname = cname, qnt = qnt, price = price,tot = tot , date=date)
        e.save()
        try:
            p = Pending.objects.get(name = fname, date = date)
            p.pending = 'True'
            p.save()
        except:
            p = Pending(name = fname, date = date)
            p.save()
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
            data = list(Person.objects.filter(fname = name, date=date))
        elif not date and name:
            data = list(Person.objects.filter(fname = name))
        elif not name and date:
            data = list(Person.objects.filter(date = date))
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
    data = []
    given= []
    if request.method == 'POST':
        name = request.POST.get('name')
        date = request.POST.get('date')
        if date and name:
            data = list(Transactions.objects.filter(name = name, date=date))
        elif not date and name:
            data = list(Transactions.objects.filter(name = name, type="SALE"))
            data = list(Transactions.objects.filter(name = name, type="FARMER", in_amt=None))
        elif not name and date:
            data = list(Transactions.objects.filter(date = date,ad='True'))
            data += list(Transactions.objects.filter(date = date,in_amt=None))
            given = list(Pending.objects.filter(given = date))
        else:
            data = data
    return render(request, 'advance.html', {'data':set(data), 'farmers' :farmers, 'given':given})

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
        try:
            tran = Transactions.objects.get(name = name, date=date, type='FARMER',ad = 'False',out_amt = None)
            tran.in_amt = extra['net']+extra['advance']
            tran.save()
        except:
            e = Transactions(name = name, date=date,type='FARMER' ,ad='False', in_amt =extra['net']+extra['advance'])
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
            t = Transactions.objects.get(name = tup.fname, date = tup.date, out_amt = None, type='FARMER')
            t.delete()
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
        typed = request.POST.get('type')
        m = Accounts.objects.get(name = name)
        if m.type != typed:
            return render(request, 'error.html', {'error':'Name not registered'})
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
    farmers = Accounts.objects.all()
    farmers = [farmer.name for farmer in farmers]
    flis = []
    dlis =[]
    slis = []
    if request.method == 'POST':
        name = request.POST.get('name')
        date = request.POST.get('date')
        if date and name:
            pass
        elif not date and name:
            dlis = [x.date for x in Person.objects.filter(fname = name)]
            dlis += [x.date for x in Person.objects.filter(cname = name)]
        elif not name and date:
            flis = [x.fname for x in Person.objects.filter(date=date)]
            slis = [x.cname for x in Person.objects.filter(date=date)]
        else:
            pass
    return render(request, 'print_all.html', {'flis':set(flis),'slis': set(slis),'dlis': set(dlis),'farmers':farmers})

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
        p_date =request.POST.get('p_date')
        if name == None and date == None:
            id = request.POST.get('id')
            if not id:
                return redirect('bills')
            try:
                records = Pending.objects.get(id=id)
                name = records.name
                date = records.date
                records.pending = False
                records.given = p_date
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
        try:
            tran = Transactions.objects.get(name = name, date=date, type='FARMER',ad = 'False',out_amt = None)
            tran.in_amt = extra['net']+extra['advance']
            tran.save()
        except:
            e = Transactions(name = name, date=date,type='FARMER' ,ad='False', in_amt =extra['net']+extra['advance'])
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
        tran.delete()
        return redirect('transactions')
    return render('transactions')

@login_required
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

@login_required
def acc_statement(request):
    farmers = Accounts.objects.filter(type = 'FARMER')
    farmers = [farmer.name for farmer in farmers]
    if request.method == 'POST':
        name = request.POST.get('name')
        p_date = request.POST.get('p_date')
        extra = {'name':name, 'net':0, 'bags_tot':0}
        lot =[]
        pending = Pending.objects.filter(name = name, given=p_date)
        pending_bills = []
        for pend in set(pending):
            try:
                bill_data = Person.objects.filter(fname = pend.name, date = pend.date)
                bags = 0
                for record in bill_data:
                    bags += record.qnt
                lot.append(bags)
                extra['bags_tot'] += bags
                p = Transactions.objects.get(name = pend.name, date = pend.date, out_amt = None, ad = 'False')
                pending_bills.append(p)
                extra['net'] += p.in_amt
            except:
                pass
        pending_bills = zip(pending_bills, lot)
        return render(request, 'statement.html',{'extra':extra, 'pending_bills':pending_bills})
    return render(request, 'acc_statement.html', {'farmers':farmers})


@login_required
def submit(request):
    data = set([x.date for x in Submit.objects.all()])
    if request.method == 'POST':
        unsave = Submit.objects.all()
        for un in unsave:
            value = 0
            records = Person.objects.filter(fname = un.name, date = un.date)
            for x in records:
                value += x.tot
            value = value - (value * 0.1) - 10
            try:
                e = Transactions.objects.get(name = un.name, date = un.date, out_amt = None, ad = 'False', type='FARMER')
                e.in_amt = value
                e.save()
            except:
                tran = Transactions(name = un.name, date = un.date, in_amt = value, ad = 'False', type='FARMER')
                tran.save()
            un.delete()
        data = set([x.date for x in Submit.objects.all()])
    return render(request, 'submit.html', {'data':data})

def summary(request):
    name = [x for x in Accounts.objects.all()]
    name_lis  = []
    price_lis = []
    for name in name:
        bal = 0
        dates_pend = [x.date for x in Pending.objects.filter(name=name, pending = 'True')]
        for date in dates_pend:
            try:
                bal += int(Transactions.objects.get(name = name, out_amt = None, date = date, type='FARMER').in_amt)
            except:
                pass
        name_lis.append(name)
        price_lis.append(bal)
        data = list(zip(name_lis, price_lis))
        data = sorted(data, key = lambda x:x[1], reverse=True)
    return render(request, 'summary.html', {'data':data})