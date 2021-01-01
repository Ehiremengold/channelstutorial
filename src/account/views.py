from django.core.files.storage import default_storage, FileSystemStorage
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth import get_user_model
import os
import cv2
import json
import base64
import requests
from django.core import files

from .models import Account, Followers
from account.forms import RegistrationForm, AccountAuthenticationForm, AccountUpdateForm
from django.conf import settings
User = get_user_model()

TEMP_PROFILE_IMAGE_NAME = "temp_profile_image.png"


def account_view(request, *args, **kwargs):
    context = {}
    user_id = kwargs.get("user_id")
    
    try:
        account = Account.objects.get(pk=user_id)
    except:
        return HttpResponse("That User Doesn't Exist")
    if account:
        context['id'] = account.id
        context['username'] = account.username
        context['email'] = account.email
        context['profile_image'] = account.profile_image.url
        context['hide_email'] = account.hide_email
        context['bio'] = account.bio
        context['link'] = account.link
        context['verified'] = account.verified
        # Define template variables
        is_self = True
        user = request.user

        logged_user_following, create = Followers.objects.get_or_create(user=request.user)
        following, create = Followers.objects.get_or_create(user=account.id)
        check_user_followers = Followers.objects.filter(another_user=account.id)
        
        is_followed = False
        if logged_user_following.another_user.filter(id=account.id).exists() or following.another_user.filter(id=account.id).exists():
            is_followed = True
        else:
            is_followed = False

        if user.is_authenticated and user != account:
            is_self = False
        elif not user.is_authenticated:
            is_self = False

        context['logged_user_following'] = logged_user_following
        context['followers'] = check_user_followers
        context['following'] = following
        context['is_followed'] = is_followed
        context['is_self'] = is_self
        context['BASE_URL'] = settings.BASE_URL
        return render(request, "account.html", context)



def follow_user(request, *args, **kwargs):
    context = {}
    user_id = kwargs.get("user_id")
    account = Account.objects.get(id=user_id)
    logged_in_user = request.user.id
    
    if account:
        context['id'] = account.id

    check_follower = Followers.objects.get(id=logged_in_user)
    is_followed = False
    if account.id != logged_in_user:
        if request.method == "POST":
            if check_follower.another_user.filter(id=account.id).exists():
                add_user = Followers.objects.get(user=logged_in_user)
                add_user.another_user.remove(account.id)
                is_followed = False
            else:
                add_user = Followers.objects.get(user=logged_in_user)
                add_user.another_user.add(account.id)
                is_followed = True
        return render(request, 'account.html')
        

def register_view(request, *args, **kwargs):
    user = request.user
    if user.is_authenticated:
        return HttpResponse(f"You are already authenticated as {user.email}")
    context = {}
    if request.method == "POST":
        form = RegistrationForm(request.POST or None)
        if form.is_valid():
            form.save()
            email = form.cleaned_data.get('email').lower()
            raw_password = form.cleaned_data.get('password1')
            account = authenticate(email=email, password=raw_password)
            login(request, account)
            destination = get_redirect_if_exists(request)
            if destination:
                return redirect(destination)
            return redirect('home')
        else:
            context['registration_form'] = form
    return render(request, 'register.html', context)


def logout_view(request):
    logout(request)
    return redirect('login')


def login_view(request, *args, **kwargs):
    context = {}
    user = request.user
    if user.is_authenticated:
        return redirect('home')
    destination = get_redirect_if_exists(request)
    if request.method == "POST":
        form = AccountAuthenticationForm(request.POST or None)
        if form.is_valid():
            email = request.POST['email']
            password = request.POST['password']
            user = authenticate(email=email, password=password)
            if user:
                login(request, user)
                destination = get_redirect_if_exists(request)
                if destination:
                    return redirect(destination)
                return redirect('home')
        else:
            context['login_form'] = form
    return render(request, 'login.html', context)


def get_redirect_if_exists(request):
    redirect = None
    if request.GET:
        if request.GET.get('next'):
            redirect = str(request.GET.get('next'))
    return redirect



def edit_profile_view(request, *args, **kwargs):
    if not request.user.is_authenticated:
        return redirect("login")
    user_id = kwargs.get("user_id")
    try:
        account = Account.objects.get(pk=user_id)
    except Account.DoesNotExist:
        return HttpResponse("Something went wrong.")
    if account.pk != request.user.pk:
        return HttpResponse("You cannot edit someone else's profile.")
    context = {}
    if request.method == "POST":
        form = AccountUpdateForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            return redirect("account:account-view", user_id=account.pk)
        else:
            form = AccountUpdateForm(request.POST, instance=request.user,
                                     initial={
                                         "id": account.pk,
                                         "email": account.email,
                                         "username": account.username,
                                         "profile_image": account.profile_image,
                                         "hide_email": account.hide_email,
                                         "bio": account.bio,
                                         "link": account.link,
                                     }
                                     )
            context['form'] = form
    else:
        form = AccountUpdateForm(
                                 initial={
                                     "id": account.pk,
                                     "email": account.email,
                                     "username": account.username,
                                     "profile_image": account.profile_image,
                                     "hide_email": account.hide_email,
                                     "bio": account.bio,
                                     "link": account.link,
                                 }
                                 )
        context['form'] = form
    context['DATA_UPLOAD_MAX_MEMORY_SIZE'] = settings.DATA_UPLOAD_MAX_MEMORY_SIZE
    return render(request, "edit_account.html", context)


def save_temp_profile_image_from_base64String(imageString, user):
    INCORRECT_PADDING_EXCEPTION = "Incorrect padding"

    try:
        if not os.path.exists(settings.TEMP):
            os.mkdir(settings.TEMP)
        if not os.path.exists(f"{settings.TEMP}/{user.pk}"):
            os.mkdir(f"{settings.TEMP}/{user.pk}")
        url = os.path.join(f"{settings.TEMP}/{user.pk}", TEMP_PROFILE_IMAGE_NAME)
        storage = FileSystemStorage(location=url)
        image = base64.b64decode(imageString)
        with storage.open('', 'wb+') as destination:
            destination.write(image)
            destination.close()
        return url
    except Exception as e:
        print("exception: " + str(e))
        # workaround for an issue I found
        if str(e) == INCORRECT_PADDING_EXCEPTION:
            imageString += "=" * ((4 - len(imageString) % 4) % 4)
            return save_temp_profile_image_from_base64String(imageString, user)
    return None


def crop_image(request, *args, **kwargs):
    payload = {}
    user = request.user
    if request.POST and user.is_authenticated:
        try:
            imageString = request.POST.get("image")
            url = save_temp_profile_image_from_base64String(imageString, user)
            img = cv2.imread(url)

            cropX = int(float(str(request.POST.get("cropX"))))
            cropY = int(float(str(request.POST.get("cropY"))))
            cropWidth = int(float(str(request.POST.get("cropWidth"))))
            cropHeight = int(float(str(request.POST.get("cropHeight"))))

            if cropX < 0:
                cropX = 0
            if cropY < 0:  # There is a bug with cropperjs. y can be negative.
                cropY = 0
            crop_img = img[cropY:cropY + cropHeight, cropX:cropX + cropWidth]

            cv2.imwrite(url, crop_img)

            # delete the old image
            user.profile_image.delete()

            # Save the cropped image to user model
            user.profile_image.save("profile_image.png", files.File(open(url, 'rb')))
            user.save()

            payload['result'] = "success"
            payload['cropped_profile_image'] = user.profile_image.url

            # delete temp file
            os.remove(url)

        except Exception as e:
            # print("exception: " + str(e))
            payload['result'] = "Error"
            payload['exception'] = str(e)
    return HttpResponse(json.dumps(payload), content_type="application/json")

