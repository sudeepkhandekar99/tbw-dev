from django.shortcuts import render, redirect, HttpResponse
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import authenticate, login
from django.views.decorators import csrf
from .forms import ContactForm
from django.views.generic import View
from django.contrib import messages
from django.views.generic import FormView
from django.urls import reverse_lazy
from .models import *
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
import json, random, smtplib, stripe, os, dotenv
from datetime import datetime
from csv import writer
from urllib.parse import unquote
from labeltbw import settings
from json2table import convert

dotenv.load_dotenv()

stripe.api_key = os.getenv('stripe_api')

# FOR CREATING RAZORPAY CLIENT.
import razorpay
razorpay_client = razorpay.Client(auth=(settings.RAZORPAY_ID, settings.RAZORPY_SECRET))

# Create your views here.
def index(request):
    if request.user.is_authenticated:
        customer = request.user
        order, created = Order.objects.get_or_create(customer=customer, complete=False)
        items = order.orderitem_set.all()
        productsFeatured = Product.objects.filter(uniqueCode__in = ["t1", "t6", "t4"])
        productsTrending = Product.objects.filter(uniqueCode__in = ["t2", "t8", "t15"])
        productsNewCol = Product.objects.filter(uniqueCode__in = ["t20", "t15", "t5", "t12"])
    else:
        items = []
        order = {
            'get_cart_items' : 0,
            'get_cart_total' : 0,
        }
        productsFeatured = Product.objects.filter(uniqueCode__in = ["t1", "t6", "t4"])
        productsTrending = Product.objects.filter(uniqueCode__in = ["t2", "t8", "t15"])
        productsNewCol = Product.objects.filter(uniqueCode__in = ["t20", "t15", "t5", "t12"])

    context = {'items' : items, 'order' : order, 'productsFeatured':productsFeatured, 'productsTrending' : productsTrending, 'productsNewCol' : productsNewCol}
    return render(request, 'index.html', context)

def shop(request):
    if request.user.is_authenticated:
        customer = request.user
        order, created = Order.objects.get_or_create(customer=customer, complete=False)
        items = order.orderitem_set.all()
    else:
        items = []
        order = {
            'get_cart_items' : 0,
            'get_cart_total' : 0,
        }

    products = Product.objects.all()
    context = {'items' : items, 'order' : order, 'products' : products}
    return render(request, 'shop.html', context)

def product(request, id):
    if request.user.is_authenticated:
        customer = request.user
        order, created = Order.objects.get_or_create(customer=customer, complete=False)
        items = order.orderitem_set.all()
    else:
        items = []
        order = {
            'get_cart_items' : 0,
            'get_cart_total' : 0,
        }
    product = Product.objects.get(id = id)
    context = {'product': product, 'items' : items, 'order' : order, 'id' : product.id}
    return render(request, 'product/' + str(product.uniqueCode) + '.html', context)

def moreProducts(request):
    return render(request, 'moreProducts.html')

def about(request):
    return render(request, 'aboutMe.html')

def register(request):
    form = ContactForm()
    if request.method == 'POST':
        form = ContactForm(request.POST)

        if form.is_valid():
            print(form.errors)
            form.save()
            user = form.cleaned_data.get('username')
            messages.success(request, "Account created succesfully for " + user + "! You can now continue logging in :)")
            return redirect('auth_login')
    else:
        form = ContactForm()

    context = {'form' : form}
    return render(request, 'registration/register.html', context)

@csrf_exempt
def auth_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('/')
        else:
            messages.error(request, "Username OR password is incorrect")

    return render(request, 'registration/login.html')

def cart(request):
    if request.user.is_authenticated:
        customer = request.user
        order, created = Order.objects.get_or_create(customer=customer, complete=False)
        items = order.orderitem_set.all()
    else:
        items = []
        order = {
            'get_cart_items' : 0,
            'get_cart_total' : 0,
        }

    context = {'items' : items, 'order' : order}
    return render(request, 'cart.html', context)

def update_item(request):
    data = json.loads(request.body)
    productId = data['productId']
    action = data['action']
    size = data['size']
    color = data['color']

    customer = request.user
    product = Product.objects.get(id = productId)
    order, created = Order.objects.get_or_create(customer=customer, complete=False)
    orderItem, created = OrderItem.objects.get_or_create(order=order, product = product)

    if action == 'add':
        orderItem.quantity += 1
    elif action == 'remove':
        orderItem.quantity -= 1

    orderItem.size = size
    orderItem.color = color

    orderItem.save()
    if orderItem.quantity <= 0:
        orderItem.delete()

    return JsonResponse("Item added :)", safe=False)

def checkout(request):
    if request.user.is_authenticated:
        customer = request.user
        order, created = Order.objects.get_or_create(customer=customer, complete=False)
        items = order.orderitem_set.all()
    else:
        items = []
        order = {
            'get_cart_items' : 0,
            'get_cart_total' : 0,
        }
    context = {'items' : items, 'order' : order}
    return render(request, 'checkout.html', context)

@csrf_exempt
def confirmation(request):
    if request.user.is_authenticated:
        customer = request.user
        order, created = Order.objects.get_or_create(customer=customer, complete=False)
        items = order.orderitem_set.all()
        address = ShippingAddress.objects.get(customer=customer)
    else:
        items = []
        order = {
            'get_cart_items' : 0,
            'get_cart_total' : 0,
        }
        address = ""
    context = {'items' : items, 'order' : order, "address" : address}
    return render(request, 'confirmation.html', context)

@csrf_exempt
def handlerequest(request):
    if request.method == "POST":
        try:
            payment_id = request.POST.get('razorpay_payment_id', '')
            order_id = request.POST.get('razorpay_order_id','')
            signature = request.POST.get('razorpay_signature','')
            params_dict = {
                'razorpay_order_id': order_id,
                'razorpay_payment_id': payment_id,
                'razorpay_signature': signature
            }
            try:
                order_db = Order.objects.get(razorpay_order_id=order_id)
            except:
                return HttpResponse("505 Not Found, get error")

            result = razorpay_client.utility.verify_payment_signature(params_dict)
            if result == None:
                amount = order_db.total_amount * 100   #we have to pass in paisa

                try:
                    razorpay_client.payment.capture(payment_id, amount)
                    order_db.razorpay_payment_id = payment_id
                    order_db.razorpay_signature = signature
                    order_db.payment_status = 1
                    order_db.save()

                    shipment = ShippingAddress.objects.get(customer=order_db.customer)
                    items = order_db.orderitem_set.all()
                    '''
                    cart = {
                        key : product
                        value : (size, color, quantity)
                    }
                    '''
                    data = {}
                    for item in items:
                        data[item.product.name] = [item.quantity, item.color, item.size]

                    data1 = {}
                    data1['customer'] = str(order_db.customer).split(':')[0]
                    data1['order'] = str(order_db).split(':')[0]
                    data1['razorpay_order_id']= order_db.razorpay_order_id
                    data1['razorpay_payment_id']= order_db.razorpay_payment_id
                    data1['address'] = shipment.address
                    data1['state'] = shipment.state
                    data1['city'] = shipment.city

                    emailMessage = "Product\tQuantity\tColor\tSize\n"
                    for item in data:
                        emailMessage += str(item) + "\t" + str(data[item][0])+ "\t" + str(data[item][1]) + "\t" + str(data[item][2]) + "\n"

                    emailMessage += "\n\n\n"

                    for item in data1:
                        emailMessage += str(item) + "\t" + str(data1[item]) + "\n"
                    
                    entry = AllOrders.objects.create(customer=order_db.customer,
                                                                    order=order_db,
                                                                    order_details=emailMessage,
                                                                    shipment=shipment,
                                                                    date_ordered=order_db.date_ordered,
                                                                    order_id_unique=order_db.order_id,
                                                                    address= shipment.address,
                                                                    city= shipment.city,
                                                                    state= shipment.state,
                                                                    zipcode= shipment.zipcode,
                                                                    total_items= order_db.get_cart_items,
                                                                    total_amount= order_db.get_cart_total,
                                                                    razorpay_order_id= order_db.razorpay_order_id,
                                                                    razorpay_payment_id= order_db.razorpay_payment_id
                                                                )

                    # Email stufff
                    try:
                        sender_email = "pqrsudeepqrs@gmail.com"
                        rec_email = "support@labeltbw.com"
                        password = "algolosers1"
                        subject = "New order! (" + str(order_db.order_id) + ")"
                        message = 'Subject: {}\n\n{}'.format(subject, emailMessage)
                        server = smtplib.SMTP("smtp.gmail.com", 587)
                        server.starttls()
                        server.login(sender_email, password)
                        server.sendmail(sender_email, rec_email, message)
                    except:
                        return render("ErrorEmail.html")
                    return redirect('confirmation')
                except Exception as e:
                    print(e)
                    order_db.payment_status = 2
                    order_db.save()
                    return HttpResponse("Payment failed! <br> Any amount deducted (if any) will be refunded within 7-10 working days :)")
            else:
                order_db.payment_status = 2
                order_db.save()
                return HttpResponse("Payment failed! <br> Any amount deducted (if any) will be refunded within 7-10 working days hereeee :)")

        except Exception as e:
            print(e)
            return HttpResponse("505 not found (outermost try except block)")

@csrf_exempt
def process_order(request):
    if request.method == 'POST':

        # print('Data:', request.POST)
        user = request.user
        address = request.POST['address']  # data[3].replace("%2C", ",").replace("+", " ").replace("%3B", ",").replace("%28", "(").replace("%29", ")").replace("%2F", "-").split("=")[-1]
        state = request.POST['state']  # data[5].split("=")[-1]
        city = request.POST['city']  # data[4].split("=")[-1]
        zipcode = request.POST['zipcode']  # data[6].split("=")[-1][:-1]
        date_added = datetime.now()

        if Order.objects.all().filter(customer=user).exists():
            order = Order.objects.get(customer=user)
            order.transaction_id = str(random.randint(0, 100))
            order.date_ordered = date_added
            order.save()
        else:
            order, created = Order.objects.get_or_create(customer=user, complete=False, transaction_id=str(random.randint(0, 100)), date_ordered=date_added)

        if ShippingAddress.objects.all().filter(customer=user).exists():
            shipment = ShippingAddress.objects.get(customer=user)
            shipment.address = address
            shipment.city = city
            shipment.state = state
            shipment.zipcode = zipcode
            shipment.date_added = date_added
            shipment.order = order
            shipment.save()
        else:
            shipment, created = ShippingAddress.objects.get_or_create(customer=user, address=address, zipcode=zipcode, city=city, state=state, date_added=date_added, order=order)

        total_items = order.get_cart_items
        total_price = order.get_cart_total
        order_no = order.order_id
        transaction_id = order.transaction_id

        order.total_amount = total_price
        order.save()

        # total_price = int(request.POST['amount'])
        amount = int(total_price)
        customer = stripe.Customer.create(
            email=request.POST['email'],
            name=request.POST['name'],
            source=request.POST['stripeToken']
        )

        # print(amount)

        charge = stripe.Charge.create(
            customer=customer,
            amount=amount*100,
            currency='inr',
            description="Donation"
        )

        return redirect('confirmation')
    else:
        return HttpResponse("404, page not found!")

def privacy(request):
    return render(request, "privacy.html")

def cancel(request):
    return render(request, "cancel.html")

def terms(request):
    return render(request, 'terms.html')