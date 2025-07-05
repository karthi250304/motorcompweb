from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
import random
import string
from .models import Bill, Company, CustomUser, Dealer, Item, ItemCategory, ItemSubCategory, Tax
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone


def outer_login(request):
    error = ''
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        if username == 'admin' and password == 'admin123':
            return redirect('dashboard') 
        else:
            error = 'Invalid Username or Password'
    
    return render(request, 'outer_login.html', {'error': error})

def dashboard(request):
    return render(request,'dashboard.html')

def logout_view(request):
    logout(request)
    return redirect ('outer_login')

def generate_password(length=8):
    characters = string.ascii_letters + string.digits + "!@#$"
    return ''.join(random.choice(characters) for _ in range(length))

def user_form(request):
    users = CustomUser.objects.all().order_by('id')
    edit_user = None

    if request.method == 'POST' and 'save_user' in request.POST:
        user_id = request.POST.get('user_id')
        name = request.POST.get('name', '').strip()
        phone = request.POST.get('phone', '').strip()

        if len(name) < 2 or not phone.isdigit() or len(phone) != 10:
            return render(request, 'user_form.html', {
                'error': 'Invalid input',
                'users': users,
                'edit_user': edit_user,
            })

        if user_id:
            user = get_object_or_404(CustomUser, pk=user_id)
            user.name = name
            user.phone = phone
            user.save()
        else:
            username = name[-4:].lower() + phone[-4:]
            password = generate_password()
            CustomUser.objects.create(
                name=name,
                phone=phone,
                username=username,
                password=password
            )
            return redirect(f"/masters/users/?popup=1&username={username}&password={password}")

        return redirect('user_form')

    if request.GET.get('edit'):
        edit_user = get_object_or_404(CustomUser, pk=request.GET.get('edit'))

    return render(request, 'user_form.html', {
        'users': users,
        'edit_user': edit_user,
        'username': request.GET.get('username'),
        'password': request.GET.get('password')
    })


def toggle_company_status(request, company_id):
    company = Company.objects.get(id=company_id)
    company.is_active = not company.is_active
    company.save()
    return redirect('company_master')



def toggle_status(request, user_id):
    user = get_object_or_404(CustomUser, pk=user_id)
    user.is_active = not user.is_active
    user.save()
    return redirect('user_form')

def reset_password(request, user_id):
    user = get_object_or_404(CustomUser, pk=user_id)
    new_password = generate_password()
    user.password = new_password
    user.save()
    return redirect(f"/masters/users/?reset=1&username={user.username}&password={new_password}")

def edit_user(request, user_id):
    user = get_object_or_404(CustomUser, pk=user_id)

    if request.method == 'POST':
        user.name = request.POST.get('name')
        user.phone = request.POST.get('phone')
        user.save()
        return redirect('user_form')

    return render(request, 'edit_user.html', {'user': user})

def company_master(request):
    edit_company = None

    if request.method == 'POST':
        company_id = request.POST.get('company_id')
        name = request.POST.get('name')
        address = request.POST.get('address')
        gst_number = request.POST.get('gst_number')
        company_phone = request.POST.get('company_phone')
        contact_person = request.POST.get('contact_person')
        contact_phone = request.POST.get('contact_phone')
        logo = request.FILES.get('logo')

        if company_id:  # Editing existing
            company = get_object_or_404(Company, pk=company_id)
            company.name = name
            company.address = address
            company.gst_number = gst_number
            company.company_phone = company_phone
            company.contact_person = contact_person
            company.contact_phone = contact_phone
            if logo:
                company.logo = logo
            company.save()
        else:  # New Company
            Company.objects.create(
                name=name,
                address=address,
                gst_number=gst_number,
                company_phone=company_phone,
                contact_person=contact_person,
                contact_phone=contact_phone,
                logo=logo
            )

        return redirect('company_master')

    # Handle ?edit=ID
    company_id = request.GET.get('edit')
    if company_id:
        edit_company = get_object_or_404(Company, pk=company_id)

    companies = Company.objects.all().order_by('-id')
    return render(request, 'company_master.html', {
        'companies': companies,
        'edit_company': edit_company
    })




def dealer_master(request):
    edit_dealer = None

    if request.method == 'POST':
        dealer_id = request.POST.get('dealer_id')
        name = request.POST.get('name')
        address = request.POST.get('address')
        gst_number = request.POST.get('gst_number')
        company_phone = request.POST.get('company_phone')
        contact_person = request.POST.get('contact_person')
        contact_phone = request.POST.get('contact_phone')
        logo = request.FILES.get('logo')

        if dealer_id:
            dealer = get_object_or_404(Dealer, pk=dealer_id)
            dealer.name = name
            dealer.address = address
            dealer.gst_number = gst_number
            dealer.company_phone = company_phone
            dealer.contact_person = contact_person
            dealer.contact_phone = contact_phone
            if logo:
                dealer.logo = logo
            dealer.save()
        else:
            Dealer.objects.create(
                name=name,
                address=address,
                gst_number=gst_number,
                company_phone=company_phone,
                contact_person=contact_person,
                contact_phone=contact_phone,
                logo=logo
            )
        return redirect('dealer_master')

    # If ?edit=ID is passed in URL
    dealer_id = request.GET.get('edit')
    if dealer_id:
        edit_dealer = get_object_or_404(Dealer, pk=dealer_id)

    dealers = Dealer.objects.all().order_by('-id')
    return render(request, 'dealer_master.html', {'dealers': dealers, 'edit_dealer': edit_dealer})

def toggle_dealer_status(request, dealer_id):
    dealer = get_object_or_404(Dealer, pk=dealer_id)
    dealer.is_active = not dealer.is_active
    dealer.save()
    return redirect('dealer_master')

tax_list = []  # Temporary list to simulate storage

def tax_master(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        cgst = request.POST.get('cgst')
        sgst = request.POST.get('sgst')
        igst = request.POST.get('igst')

        Tax.objects.create(
            name=name,
            cgst=cgst,
            sgst=sgst,
            igst=igst,
        )
        return redirect('tax_master')

    taxes = Tax.objects.all().order_by('-id')
    return render(request, 'tax_master.html', {'taxes': taxes})

@csrf_exempt
def delete_tax(request, tax_id):
    if request.method == 'POST':
        tax = get_object_or_404(Tax, pk=tax_id)
        tax.delete()
    return redirect('tax_master')

def item_category(request):
    if request.method == 'POST':
        cat_id = request.POST.get('category_id')
        name = request.POST.get('name')

        if cat_id:  # Update
            category = ItemCategory.objects.get(id=cat_id)
            category.name = name
            category.save()
        else:  # Create
            ItemCategory.objects.create(name=name)

        return redirect('item_category')

    categories = ItemCategory.objects.all()
    edit_category = None

    if 'edit' in request.GET:
        edit_id = request.GET.get('edit')
        edit_category = get_object_or_404(ItemCategory, id=edit_id)

    context = {
        'categories': categories,
        'edit_category': edit_category
    }
    return render(request, 'itemcategory.html', context)

def toggle_item_category_status(request, pk):
    category = get_object_or_404(ItemCategory, id=pk)
    category.is_active = not category.is_active
    category.save()
    return redirect('item_category')

def item_subcategory(request):
    from .models import ItemSubCategory, ItemCategory

    edit_subcategory = None

    if request.method == 'POST':
        subcat_id = request.POST.get('subcategory_id')
        name = request.POST.get('name')
        category_id = request.POST.get('category_id')

        if subcat_id:
            subcat = get_object_or_404(ItemSubCategory, pk=subcat_id)
            subcat.name = name
            subcat.category_id = category_id
            subcat.save()
        else:
            ItemSubCategory.objects.create(name=name, category_id=category_id)

        return redirect('item_subcategory')

    if 'edit' in request.GET:
        edit_subcategory = get_object_or_404(ItemSubCategory, pk=request.GET.get('edit'))

    subcategories = ItemSubCategory.objects.select_related('category').all().order_by('-id')
    categories = ItemCategory.objects.filter(is_active=True)

    return render(request, 'item_subcategory.html', {
        'subcategories': subcategories,
        'categories': categories,
        'edit_subcategory': edit_subcategory
    })

def toggle_subcategory_status(request, pk):
    subcat = get_object_or_404(ItemSubCategory, pk=pk)
    subcat.is_active = not subcat.is_active
    subcat.save()
    return redirect('item_subcategory')

def item_master(request):
    edit_item = None

    if request.method == 'POST':
        item_id = request.POST.get('item_id')
        name = request.POST.get('name')
        code = request.POST.get('code')
        brand = request.POST.get('brand')
        category_id = request.POST.get('category_id')
        subcategory_id = request.POST.get('subcategory_id')
        warranty = request.POST.get('warranty')

        if item_id:
            item = get_object_or_404(Item, pk=item_id)
            item.name = name
            item.code = code
            item.brand = brand  # ← make sure this is here
            item.category_id = category_id
            item.subcategory_id = subcategory_id
            item.warranty = warranty
            item.save()
        else:
            Item.objects.create(
                name=name,
                code=code,
                brand=brand,  # ← include this
                category_id=category_id,
                subcategory_id=subcategory_id,
                warranty=warranty
            )

        return redirect('item_master')

    # for editing
    if request.GET.get('edit'):
        edit_item = get_object_or_404(Item, pk=request.GET.get('edit'))

    items = Item.objects.select_related('category', 'subcategory').all().order_by('-id')
    categories = ItemCategory.objects.filter(is_active=True)
    subcategories = ItemSubCategory.objects.filter(is_active=True)

    return render(request, 'items.html', {
        'items': items,
        'categories': categories,
        'subcategories': subcategories,
        'edit_item': edit_item
    })


def toggle_item_status(request, pk):
    item = get_object_or_404(Item, pk=pk)
    item.is_active = not item.is_active
    item.save()
    
    return redirect('item_master')

def create_bill(request):
    if request.method == 'POST':
        item_id = request.POST['item']
        quantity = int(request.POST['quantity'])
        rate = float(request.POST['rate'])
        tax_id = request.POST['tax']
        dealer_id = request.POST['dealer']
        company_id = request.POST['company']

        name = request.POST['customer_name']
        address = request.POST['customer_address']
        phone = request.POST['customer_phone']
        billing_address = request.POST['billing_address']
        shipping_address = request.POST['shipping_address']

        Bill.objects.create(
            item_id=item_id,
            quantity=quantity,
            rate=rate,
            tax_id=tax_id,
            dealer_id=dealer_id,
            company_id=company_id,
            customer_name=name,
            customer_address=address,
            customer_phone=phone,
            billing_address=billing_address,
            shipping_address=shipping_address
        )

        return redirect('create_bill')

    context = {
        'items': Item.objects.filter(is_active=True),
        'taxes': Tax.objects.all(),
        'dealers': Dealer.objects.filter(is_active=True),
        'companies': Company.objects.filter(is_active=True),
        'categories': ItemCategory.objects.filter(is_active=True),  # ✅ Add this
        'subcategories': ItemSubCategory.objects.filter(is_active=True),  # ✅ Add this
    }
    return render(request, 'createbills.html', context)


