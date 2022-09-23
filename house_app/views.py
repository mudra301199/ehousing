from django.shortcuts import redirect, render
from .models import *
from django.conf import settings
from django.core.mail import send_mail
from random import randint

default_data = {
    'no_header_pages': ['login_page', 'register_page', 'otp_page', 'forgot_password'],
    'current_page': None,
    'user_roles': UserRole.objects.all(),
    'gender_choices': [],
}

for gc in gender_choices:
    default_data['gender_choices'].append({'short_text': gc[0], 'text': gc[1]})

print(default_data['gender_choices'])
# [
#     {
#         'short_text': 'm',
#         'text': 'male'
#     },
# ]

# alert_system
def alert(type, text):
    default_data['alert'] = {
        'type': type,
        'text': text,
    }
    print('alert called.')

def index(request):
    return redirect(login_page)
    # return render(request, 'index.html', default_data)

# login page
def login_page(request):
    default_data['current_page'] = 'login_page'
    return render(request, 'login_page.html', default_data)

# register page
def register_page(request):
    default_data['current_page'] = 'register_page'
    return render(request, 'register_page.html', default_data)

# otp page
def otp_page(request):
    default_data['current_page'] = 'otp_page'
    return render(request, 'otp_page.html', default_data)

# OTP Creation
def otp(request):
    otp_number = randint(10000, 99999)
    
    print("OTP is: ", otp_number)
    request.session['otp'] = otp_number

# send_otp
def send_otp(request, otp_for="register"):
    print(otp_for)
    otp(request)

    email_to_list = [request.session['email'],]

    if otp_for == 'activate':
        request.session['otp_for'] = 'activate'
        subject = f'OTP for house Account Activation'
    elif otp_for == 'recover_pwd':
        request.session['otp_for'] = 'recover_pwd'
        subject = f'OTP for house Password Recovery'
    else:
        request.session['otp_for'] = 'register'
        subject = f'OTP for house Registration'

    email_from = settings.EMAIL_HOST_USER

    message = f"Your One Time Password for verification is: {request.session['otp']}."

    send_mail(subject, message, email_from, email_to_list)

    alert('success', 'An OTP has sent to your email.')

    
    # default_data.update({'next_step': 'otp'})
    
    # return JsonResponse(data)    
    # return redirect(otp_page)

# verify otp
def verify_otp(request, verify_for="register"):

    if request.session['otp'] == int(request.POST['otp']):

        if verify_for == 'activate':
            master = Master.objects.get(Email=request.session['email'])
            master.IsActive = True
            master.save()


            return redirect(profile_page)
        elif verify_for == 'recover_pwd':
            master = Master.objects.get(Email=request.session['email'])
            master.Password = request.session['password']
            master.save()
        else:
            user_role = UserRole.objects.get(id=request.session['reg_data']['user_role_id'])
            master = Master.objects.create(
                UserRole = user_role,
                Email = request.session['reg_data']['email'],
                Password = request.session['reg_data']['password'],
                IsActive = True,
            )

            Profile.objects.create(
                Master = master,
            )

        print("verified.")
        alert('success', 'An OTP verified.')

    else:
        print("Invalid OTP")
        
        alert('danger', 'Invalid OTP')

        return redirect(otp_page)
    
    return redirect(login_page)

# profile page
def profile_page(request):
    if 'email' in request.session:
        default_data['current_page'] = 'profile_page'
        
        profile_data(request) # load data
        
        return render(request, 'profile_page.html', default_data)
    return redirect(login_page)

# registration functionality
def register(request):
    print(request.POST)

    request.session['reg_data'] = {
        'user_role_id': int(request.POST['user_role']),
        'email': request.POST['email'],
        'password': request.POST['password']
    }

    request.session['email'] = request.POST['email']
    send_otp(request, 'register')

    # verify_otp(request)

    
    return redirect(otp_page)

# load profile data
def profile_data(request):
    master = Master.objects.get(Email = request.session['email'])
    profile = Profile.objects.get(Master = master)
    if profile.FullName:
        splitted_names = profile.FullName.split()
        profile.FirstName = splitted_names[0]
        
        if len(splitted_names) > 1:
            profile.LastName = splitted_names[1]

    default_data['profile_data'] = profile

# login functionality
def login(request):
    print(request.POST)

    try:
        master = Master.objects.get(
            Email = request.POST['email']
        )
        request.session['email'] = master.Email
        if master.IsActive:
            if master.Password == request.POST['password']:
                
                return redirect(profile_page)
            else:
                alert('danger', 'incorrect password!')
                print('incorrect password!')
        else:
            alert('warning', 'Your account is inactive!')
            print('Your account is inactive!')
            
            

            send_otp(request, otp_for='activate')
            
            return redirect(otp_page)

    except Master.DoesNotExist as err:
        print('record not found!')

    return redirect(login_page)

# update profile functionality
def update_profile(request):
    master = Master.objects.get(Email = request.session['email'])
    profile = Profile.objects.get(Master = master)

    print('update data', request.POST)

    profile.FullName = f"{request.POST['first_name']} {request.POST['last_name']}"
    profile.Gender = request.POST['gender']
    profile.BirthDate = request.POST['birth_date']
    profile.Mobile = request.POST['mobile']
    profile.Country = request.POST['country']
    profile.State = request.POST['state']
    profile.City = request.POST['city']
    profile.Pincode = request.POST['pincode']
    profile.Address = request.POST['address']

    profile.save()

    return redirect(profile_page)

from pathlib import Path

# upload profile image
def upload_image(request):
    master = Master.objects.get(Email = request.session['email'])
    profile = Profile.objects.get(Master = master)

    if 'profile_image' in request.FILES:
        image = request.FILES['profile_image']
        print('old name', image.name)
        image_type = image.name.split('.')[-1]
        new_name = master.Email.split('@')[0]
        old_name = profile.ProfileImage.name.split('/')[-1]
        image.name = f"{new_name}.{image_type}"
        print('new name', image.name)
        
        base_dir = Path(__file__).resolve().parent.parent
        image_path = Path.joinpath(settings.MEDIA_ROOT, f"profiles/{image.name}")

        print(image.name, old_name)
        
        print(image.name == old_name)
        
        if image.name == old_name:
            Path(image_path).unlink()
        
        profile.ProfileImage = image

        profile.save()

    return redirect(profile_page)

# remove profile photo
def remove_profile_image(request):
    master = Master.objects.get(Email = request.session['email'])
    profile = Profile.objects.get(Master = master)
    
    # print('image path: ', user.Image.url.split('/')[-1])
    upload_path = Path.joinpath(settings.MEDIA_ROOT, f"profiles/{profile.ProfileImage.url.split('/')[-1]}")
    Path(upload_path).unlink()
    
    profile.ProfileImage = ""
    profile.save()
    

    print('image removed.')
    default_data['image_uploaded'] = 'false'

    return redirect(profile_page)

# change password functionality
def change_password(request):
    master = Master.objects.get(Email = request.session['email'])

    if master.Password == request.POST['current_password']:
        master.Password = request.POST['new_password']
        master.save()
    else:
        print('incorrect current password.')

    return redirect(profile_page)

# addissue
def add_issue(request):
    return redirect(login_page)

#forgot password
def forgot_password(request):
    default_data['current_page'] = 'forgot_password'
    return render(request, 'forgot_password.html', default_data)

# contact
def contact(request):
    return redirect(profile_page)

# logout
def logout(request):
    if 'email' in request.session:
        del request.session['email']
    return redirect(login_page)   

    
