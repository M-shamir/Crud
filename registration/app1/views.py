from django.shortcuts import render
from django.contrib.auth.models import User
from django.shortcuts import redirect, HttpResponse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import never_cache
from django.db import IntegrityError
from django.db.models import Q 



#  homepage
@login_required(login_url='login') 
@never_cache  
def HomePage(request):
    
    if request.user.is_superuser:
        return redirect('adminhome')
    username = request.user.username
    return render(request, 'home.html',{'username': username})

# signup page
def SignupPage(request):
   
    if request.user.is_authenticated:

        return redirect('home')
    
    
    message = ""
    alert_type = 'info'
    
    if request.method == 'POST':
      
        uname = request.POST.get('username')
        email = request.POST.get('email')
        pass1 = request.POST.get('password1')
        pass2 = request.POST.get('password2')
        
        
        if not uname:
            message = "Username is required!"
            alert_type = 'warning'
        elif not email:
            message = "Email is required!"
            alert_type = 'warning'
        elif pass1 != pass2:
            message = "Passwords do not match!"
            alert_type = 'warning'
        else:
            try:
                
                my_user = User.objects.create_user(uname, email, pass1)
                my_user.save()  
           
                return redirect('login') 
            except IntegrityError:
                
                message = "Username or email already exists!"
                alert_type = 'error'
    
    return render(request, 'signup.html', {'message': message,'alert_type': alert_type})

# login page
@never_cache 
def LoginPage(request):
    
    m = ""
    alert_type = 'info'
    if request.user.is_authenticated:
        
        if request.user.is_superuser:
            return redirect('adminhome')  
        else:
            return redirect('home') 
    
   
    if request.method == 'POST':
      
        username = request.POST.get('username')
        pass1 = request.POST.get('pass')
        
        if not username:
            m = "Username is required!"
            alert_type = 'warning'
        elif not pass1:
            m = "Password is required!"
            alert_type = 'warning'
        else:
            user = authenticate(request, username=username, password=pass1)
            if user is not None:
                login(request, user)
                if user.is_superuser:
                    return redirect('adminhome') 
                else:
                    return redirect('home')  
            else:
                m = "Username or password is incorrect"
                alert_type = 'error'
    
    return render(request, 'login.html', {"m": m,"alert_type": alert_type})

# logging out the user
def logoutpage(request):
    # Log the user out
    logout(request)
    # Redirect to 'login' page
    return redirect('login')


@login_required(login_url='login')
@never_cache
def AdminPage(request):
    query = request.GET.get('query', '')
    if query:
        users = User.objects.filter(Q(username__icontains=query) | Q(email__icontains=query)).order_by('id')
    else:
        users = User.objects.filter(is_superuser = False).order_by('id')

    if not request.user.is_superuser:
        return redirect('home')

    message = None  # Ensure message is defined

    if request.method == 'POST':
        if 'create' in request.POST:
            username = request.POST.get('username')
            email = request.POST.get('email')
            password = request.POST.get('password')
            try:
                user = User.objects.create_user(username, email, password)
                user.save()
                message = "User created successfully!"
            except IntegrityError:
                message = "Username or email already exists!"
        elif 'update' in request.POST:
            user_id = request.POST.get('id')
            username = request.POST.get('username')
            email = request.POST.get('email')
            user = User.objects.get(id=user_id)
            user.username = username
            user.email = email
            user.save()
            message = "User updated successfully!"
        elif 'delete' in request.POST:
            user_id = request.POST.get('id')
            User.objects.get(id=user_id).delete()
            message = "User deleted successfully!"

    return render(request, 'admin.html', {'users': users, 'search_query': query, 'message': message})


    


