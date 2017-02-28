from django.shortcuts import render, redirect
from django.contrib import messages
from datetime import datetime, timedelta
from .models import User, Trip

def index(request):
    if "id" in request.session:
        return redirect('/travels')
    return render(request, 'travel/index.html')

def success(request):
    # this method will render the homepage template-- will need to send along filtered user, differentiated trip objects to be parsed through in the template for displaying purposes

    if "id" not in request.session:
        messages.info(request, "Pleaes log in or register")
        return redirect('/main')
    try:
        user = User.objects.get(id=request.session["id"])
    except User.DoesNotExist:
        messages.info(request, "User not found. Please register")
        return redirect('/main')
    # for displaying on template-- excludes trips that started yesterday or earlier
    my_trips = Trip.objects.filter(members=user).exclude(start__lt=(datetime.now()-timedelta(days=1))).order_by("start")
    other_trips = Trip.objects.all().exclude(members=user).exclude(start__lt=(datetime.now()-timedelta(days=1))).order_by("start")
    return render(request, 'travel/success.html', {"user": user, "my_trips":my_trips, "other_trips": other_trips})

def process(request):
    # this method will use call on REGISTRATION validations made in models and either set session.id to the valid user.id and redirect to home page or return relevant error messages and redirect back home
    if request.method != "POST":
        return redirect('/main')
    else:
        user_valid = User.objects.validate(request.POST)
    if user_valid[0] == True:
        request.session["id"] = user_valid[1].id
        return redirect('/travels')
    else:
        for msg in user_valid[1]:
            messages.add_message(request, messages.INFO, msg)
        return redirect('/main')

def login(request):
    # this method will use call on LOGIN validations made in models and either set session.id to the valid user.id and redirect to home page or return relevant error messages and redirect back home
    if request.method != "POST":
        return redirect('/main')
    else:
        user = User.objects.authenticate(request.POST)
        if user[0] == True:
            request.session["id"] = user[1].id
            return redirect('/travels')
        else:
            messages.add_message(request, messages.INFO, user[1])
            return redirect('/main')

def logout(request):
    if "id" in request.session:
        request.session.pop("id")
    return redirect('/main')

def addtrip(request):
    # this method is used to make sure that only user.id's that are in session access the corresponding url and RENDER the add trip template
    if "id" not in request.session:
        messages.info(request, "Plese login or register")
        return redirect('/main')
    return render(request, 'travel/add.html')

def addprocess(request):
    if request.method != "POST":
        messages.info(request, "Please use the form to add a trip")
        return redirect('/travels')
    if "id" not in request.session:
        messages.info(request, "Please log in or register")
        return redirect('/main')
    trip_valid = Trip.objects.makeTrip(request.POST, request.session["id"])
    if trip_valid["success"] == True:
        return redirect('/travels/destination/{}'.format(trip_valid["trip_object"].id))
    else:
        for msg in trip_valid["error_list"]:
            messages.info(request, msg)
        return redirect('/travels/add')

def destination(request, dest_id):
    # this method will render destination.html. Need to pass through user object (as curr_user), trip object (as destination), another trip object (as members of the trip but excluding the creator username).
    if "id" not in request.session:
        messages.info(request, "Please log in or register")
        return redirect('/main')
    try:
        curr_user = User.objects.get(id=request.session["id"])
    except User.DoesNotExist:
        messages.info(reqeust, "Your session has expired. Please log in or register")
        return redirect('/main')
    try:
        dest = Trip.objects.get(id=dest_id)
    except Trip.DoesNotExist:
        messages.info(request, "Trip not found!")
        return redirect('/travels')

    return render(request, 'travel/destination.html', {"user":curr_user, "dest":dest, "members":dest.members.exclude(username=dest.creator.username)})

def join (request, dest_id):
    if "id" not in request.session:
        messages.info(request, "Please log in or register.")
        return redirect('/main')
    try:
        dest = Trip.objects.get(id=dest_id)
    except Trip.DoesNotExist:
        messages.info(request, "Trip not found!")
        return redirect('/travels')
    try:
        curr_user = User.objects.get(id=request.session["id"])
    except User.DoesNotExist:
        messages.info(reqeust, "Your session has expired. Please log in or register")
        return redirect('/main')

    valid_join = Trip.objects.joinTrip(request.session["id"], dest_id)

    for msg in valid_join["msgs"]:
        messages.info(request, msg)
    return redirect('/travels')
