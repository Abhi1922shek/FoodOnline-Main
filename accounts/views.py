from django.shortcuts import redirect, render

from vendor.forms import VendorForm
from vendor.models import Vendor
from .forms import UserForm
from .models import User, UserProfile
from .utils import detectUser, send_verification_email
from django.contrib import messages, auth
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.exceptions import  PermissionDenied
import token
from django.utils.http import urlsafe_base64_decode
from django.contrib.auth.tokens import default_token_generator

# Restrict the vendor from accessing customer page
def chek_role_vendor(user):
    if user.role == 1:
        return True
    else:
        raise PermissionDenied
    
# Restrict the customer from accessing vendor page
def chek_role_customer(user):
    if user.role == 2:
        return True
    else:
        raise PermissionDenied

# Create your views here.
def registerUser(request):
    if request.user.is_authenticated:
        messages.warning(request, "You are already logged in.")
        return redirect("dashboard")
    elif request.method == 'POST':
        form = UserForm(request.POST)
        if form.is_valid():
            first_name = form.cleaned_data['first_name']
            last_name = form.cleaned_data['last_name']
            username = form.cleaned_data['username']
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            user = User.objects.create_user(
                first_name=first_name,
                last_name=last_name,
                username=username,
                email=email,
                password=password
            )
            user.role = User.CUSTOMER
            user.save()

            mail_subject = "Please activate your account"
            email_template = "accounts/email/account_verification_email.html"
            # Send verification email
            send_verification_email(request, user, mail_subject, email_template)

            messages.success(request, 'User created successfully')
            return redirect('registerUser')
        else:
            print(form.errors)
    else:
        form = UserForm()
    
    context = {
        'form': form,
    }
    return render(request, 'accounts/registerUser.html', context)


def registerVendor(request):
    if request.user.is_authenticated:
        messages.warning(request, "You are already logged in.")
        return redirect("myAccount")
    elif request.method == 'POST':
        # store the user & create the user
        form = UserForm(request.POST)
        v_form = VendorForm(request.POST, request.FILES) 

        if form.is_valid() and v_form.is_valid():
            first_name = form.cleaned_data['first_name']
            last_name = form.cleaned_data['last_name']
            username = form.cleaned_data['username']
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            user = User.objects.create_user(first_name=first_name, last_name=last_name, username=username, email=email, password=password)
            user.role = User.VENDOR
            user.save()

            vendor = v_form.save(commit=False)
            vendor.user = user
            user_profile = UserProfile.objects.get(user=user)
            vendor.user_profile = user_profile
            vendor.save()

            # Send verification email
            mail_subject = "Please activate your account"
            email_template = "accounts/email/account_verification_email.html"
            send_verification_email(request, user, mail_subject, email_template)

            messages.success(request, 'Your account has been registered successfully! Please wait for the approval.')
            return redirect('registerVendor')
        else:
            print(form.errors)
    else:
        form = UserForm()
        v_form = VendorForm()

    context = {
        'form' : form,
        'v_form' : v_form,
    }
    return render(request, 'accounts/registerVendor.html', context)

def activate(request, uidb64, token):
    # Activate the user by setting the is_active status to True
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = User.objects.get(pk=uid)
    except(TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
    if user is not None and default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()
        messages.success(request, "You have successfully registered your account!")
        return redirect('myAccount')
    else:
        messages.error(request, "Invalid activation link")
        return redirect('myAccount')
    
def forgot_password(request):
    if request.method == 'POST':
        email = request.POST['email']
        if User.objects.filter(email=email).exists():
            user = User.objects.get(email__exact=email)

            mail_subject = "Reset Your Password"
            email_template = "accounts/email/reset_password_email.html"
            
            # Send reset password email
            send_verification_email(request, user, mail_subject, email_template)

            messages.success(request, 'Password reset link has been sent to your mail')
            return redirect('login')
        else:
            messages.error(request, 'Account does not exist')
            return redirect('forgot_password')

    return render(request, 'accounts/forgot_password.html')

def reset_password_validate(request, uidb64, token):
    # Validate the user by decoding the token & user pk
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = User.objects.get(pk=uid)
    except(TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
    if user is not None and default_token_generator.check_token(user, token):
        request.session['uid'] = uid
        messages.info(request, "Please reset your password")
        return redirect('reset_password')
    else:
        messages.error(request, " This link has been expired")
        return redirect('myAccount')

def reset_password(request):
    if request.method == 'POST':
        password = request.POST['password']
        confirm_password = request.POST['confirm_password']
        if password == confirm_password:
            pk = request.session.get('uid')
            user = User.objects.get(pk=pk)
            user.set_password(password)
            user.is_active = True
            user.save()
            messages.success(request, "Password reset successfully")
            return redirect('login')
        else:
            messages.error(request, "Password does not match")
            return redirect('reset_password')

    return render(request, 'accounts/reset_password.html')

def login(request):
    if request.user.is_authenticated:
        messages.warning(request, "You are already logged in.")
        return redirect("myAccount")
    elif request.method == 'POST':
        email = request.POST['email'] # here email is the name value (name = "email") of the input field
        password = request.POST['password']
        # print(password)  # here password is the name value (name = "password") of the input field
        user = auth.authenticate(email=email, password=password)
        if user is not None:
            auth.login(request, user)
            messages.success(request, "You are now logged in.")
            return redirect('myAccount')

        else:
            messages.error(request, "INVALID CREDENTIALS")
            return redirect('login')
    return  render(request, 'accounts/login.html')

def logout(request):
    auth.logout(request)
    messages.info(request, "You are logged out.")
    return redirect('login')

@login_required(login_url = 'login')
def myAccount(request):
    user = request.user
    redirectUrl = detectUser(user)
    return redirect(redirectUrl)

@login_required(login_url = 'login')
@user_passes_test(chek_role_customer)
def customerDashboard(request):
    return render(request, "accounts/customerDashboard.html")

@login_required(login_url = 'login')
@user_passes_test(chek_role_vendor)
def vendorDashboard(request):
    return render(request, "accounts/vendorDashboard.html")
