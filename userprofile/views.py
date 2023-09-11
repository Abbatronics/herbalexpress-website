from django.contrib import messages
from django.contrib.auth import login, logout, authenticate, get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm, PasswordResetForm
from .decorators import user_not_authenticated
from django.contrib.auth.models import User
from django.shortcuts import render, redirect, reverse, get_object_or_404
from django.utils.text import slugify
from .forms import UserRegistrationForm, UserLoginForm, UserUpdateForm, ProfileUpdateForm
from .models import Userprofile 
from store.forms import ItemForm
from store.models import  Item, OrderItem  
from .tokens import account_activation_token
from django.template.loader import render_to_string
from django.contrib.sites.shortcuts import get_current_site
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.core.mail import EmailMessage, send_mail, BadHeaderError 
from django.http import HttpResponse 
from django.db.models.query_utils import Q
from django.contrib.auth.tokens import default_token_generator 
from django.conf import settings
from .forms import SetPasswordForm



@user_not_authenticated
def vendor_detail(request, pk):
    user = User.objects.get(pk=pk)
    products = user.products.filter(status=Item.ACTIVE)

    return render(request, 'userprofile/vendor_detail.html', {
        'user': user,
        'products': products
    })

@login_required
def add_product(request):
    

    if request.method == "POST":
        form = ItemForm(request.POST, request.FILES)

        if form.is_valid():
            title = request.POST.get('title', )
            slug = slugify(title)

            item = form.save(commit=False)
            item.user = (request.user)
            item.slug = slug
            item.save()

            messages.success(request, 'The product was added !')

            return redirect('my_store')
    else:        
        form = ItemForm()


    return render(request, 'userprofile/product_form.html', {
        'title': 'Add product ', 
        'form': form
    })

@login_required
def edit_product(request, pk):
    product = Item.objects.filter(user=request.user).get(pk=pk)

    if request.method == "POST":
        form = ItemForm(request.POST, request.FILES, instance=product)

        if form.is_valid():
           form.save()

           messages.success(request, 'The product was edited !')


           return redirect('my_store')

    else:    
        form = ItemForm(instance=product)

    return render(request, 'userprofile/product_form.html', {
        'title': 'Edit product ',
        'product': product , 
        'form': form
    })

@login_required
def delete_product(request, pk):
    product = Item.objects.filter(user=request.user).get(pk=pk)
    product.status = Product.DELETED
    product.save()
    
    messages.success(request, 'The product was deleted !')

    return redirect( 'my_store')
    

@login_required
def my_store(request):
    products = request.user.products.exclude(status=Item.DELETED)
    order_items = OrderItem.objects.filter(product__user=request.user)

    return render(request, 'userprofile/my_store.html', {
        'products': products,
        'order_items': order_items
    })

@login_required
def my_store_order_detail(request, pk):
    order = get_object_or_404(Order, pk=pk)

    return render(request, 'userprofile/my_store_order_detail.html', {
        'order': order
    })
    
@login_required
def account(request):
    return render(request, 'userprofile/account.html')

def activate(request, uidb64, token):
    User = get_user_model()
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except(TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and account_activation_token.check_token(user, token):
        user.is_active = True
        user.save()

        messages.success(request, 'Thank you for your email confirmation. Now you can login your account.')
        return redirect('login')
    else:
        messages.error(request, 'Activation link is invalid!')
    
    return redirect('/')


def activateEmail(request, user, to_email):
    mail_subject = 'Activate your user account.'
    message = render_to_string('userprofile/template_activate_account.html', {
        'user': user.username,
        'domain': get_current_site(request).domain,
        'uid': urlsafe_base64_encode(force_bytes(user.pk)),
        'token': account_activation_token.make_token(user),
        'protocol': 'https' if request.is_secure() else 'http'
    })
    email = EmailMessage(mail_subject, message, to=[to_email])
    if email.send():
        messages.success(request, f'Dear {user}, Please go to your email {to_email} inbox and Click on \
             received activation link to confirm and Complete the registration, NOTE: Check your spam folder,') 
    else:
        messages.error(request, f'Problem sending email to {to_email}, chck if you typed it correctly,')

@user_not_authenticated
def signup(request):
    if request.method == "POST":
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False
            user.save()
            activateEmail(request, user, form.cleaned_data.get('email'))
            return redirect('/')

        else:
            for error in list(form.errors.values()):
                messages.error(request, error)

    else:
        form = UserRegistrationForm()

    return render(
        request=request,
        template_name="userprofile/signup.html",
        context={"form": form}
    ) 

@login_required
def custom_logout(request):
    logout(request)
    messages.info(request, "Logged out successfully")
    return redirect("/")

@user_not_authenticated
def custom_login(request):   
    if request.method == "POST":
        form = UserLoginForm(request=request, data=request.POST)
        if form.is_valid():
            user = authenticate(
                username=form.cleaned_data["username"],
                password=form.cleaned_data["password"],
            )
            if user is not None:
                login(request, user)
                messages.success(request, f"Hello {user.username}! You have been logged in")
                return redirect('/')
        else:
            for key, error in list(form.errors.items ()):
                if key == 'captcha' and error[0] == 'This field is required.':
                    messages.error(request, "You must pass the reCAPTCHA test")
                    continue 


                messages.error(request, error)

    
    form = UserLoginForm()
    return render(
        request=request,
        template_name = "userprofile/login.html",
        context={"form": form}
    )

@user_not_authenticated
def password_reset_request(request):
    if request.method == 'POST':
       password_form = PasswordResetForm(request.POST)
       if password_form.is_valid():
        data = password_form.cleaned_data['email']
        user_email = User.objects.filter(Q(email=data))
        if user_email.exists():
            for user in user_email:
                subject = 'Pasword Request'
                email_template_name = 'userprofile/password_message.txt'
                parameters = {
                    'email': user.email,
                    'domain': '127.0.0.1:8000',
                    'site_name': 'HerbalExpress',
                    'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                    'token': default_token_generator.make_token(user),
                    'protocol': 'http',
                }
                email = render_to_string(email_template_name, parameters)
                try:
                    send_mail(subject, email, '', [user.email], fail_silently=False)
                except:
                    return HttpResponse('Invalid Header')
                return redirect('password_reset_done')
    else:
       password_form = PasswordResetForm()
    context = {
        'password_form': password_form,
        
    }



    return render(request, 'userprofile/password_reset.html', context) 

@login_required
def profile(request):
    if request.method == 'POST':
        u_form = UserUpdateForm(request.POST or None, instance=request.user)
        p_form = ProfileUpdateForm(
            request.POST or None, request.FILES or None, instance=request.user.userprofile)
        if u_form.is_valid() and p_form.is_valid():
            u_form.save()
            p_form.save()
            return redirect('profile')
    else:
        u_form = UserUpdateForm(instance=request.user)
        p_form = ProfileUpdateForm(instance=request.user.userprofile)
    context = {
        'u_form': u_form,
        'p_form': p_form,
    }
    return render(request, 'userprofile/profile.html', context)


