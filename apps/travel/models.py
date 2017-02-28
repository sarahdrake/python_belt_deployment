from __future__ import unicode_literals

from django.db import models
from datetime import datetime, timedelta
import bcrypt, re

class UserManager(models.Manager):
    def validate(self, postData):
        errors = []
        if len(postData["name"]) < 3 or len(postData["name"]) > 45:
            errors.append("Name must be between 3-45 characters.")
        elif not re.search(r'^[A-Z a-z]+$', postData["name"]):
            errors.append("Name cannot contain numbers or special characters.")
        if len(postData["username"]) < 3 or len(postData["username"]) > 45:
            errors.append("Please enter a username between 3-45 characters.")
        elif not re.search(r'^[A-Za-z0-9 ]+$', postData["username"]):
            errors.append("Username cannot contain special characters.")
        elif len(User.objects.filter(username=postData["username"])) > 0:
            errors.append("Username is already registered.")
        if len(postData["password"]) < 8:
            errors.append("Password must be 8 or more characters.")
        if postData["confirm"] != postData["password"]:
            errors.append("Passwords do not match.")
        if len(errors) == 0:
            user  = User.objects.create(name=postData["name"], username=postData["username"], pw_hash=bcrypt.hashpw(postData["password"].encode(), bcrypt.gensalt()))
            return (True, user)
        else:
            return (False, errors)

    def authenticate(self, postData):
        if "username" in postData and "password" in postData:
            try:
                user = User.objects.get(username=postData["username"])
            except User.DoesNotExist:
                return (False, "Invalid username/password combination")
            pw_match = bcrypt.hashpw(postData['password'].encode(),user.pw_hash.encode())
            if pw_match:
                return (True, user)
            else:
                return (False, "Invalid username/password combination")
        else:
            return (False, "Please enter login info")

class User(models.Model):
    name = models.CharField(max_length=45)
    username = models.CharField(max_length=45)
    pw_hash = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = UserManager()

class TripManager(models.Manager):
    def makeTrip(self, postData, user_id):
        errors = []
        # before proceeding any further check to see if user exists
        try:
            curr_user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            errors.append("User not found. Please log in again")
            return {"success":False, "error_list":errors}
        # if curr_user exists proceed with blank field validations
        if len(postData["destination"]) == 0:
            errors.append("Please enter a trip destination.")
        if len(postData["plan"]) == 0:
            errors.append("Please enter a trip description.")
        if len(postData["start"]) == 0:
            errors.append("Please enter a start date.")
        if len(postData["end"]) == 0:
            errors.append("Please enter an end date.")
        # valid date format check:
        # start date
        try:
            # attempt m/d/yy format first
            start = datetime.strptime(postData["start"], "%m/%d/%y")
        except ValueError:
            try:
                # attempt m/d/yyyy format next
                start = datetime.strptime(postData["start"], "%m/%d/%Y")
            except ValueError:
                errors.append("Invalid start date format")
        # end date
        try:
            # Attempt m/d/yy format first
            end = datetime.strptime(postData["end"], "%m/%d/%y")
        except ValueError:
            try:
                # Attempt m/d/yyyy format next
                end = datetime.strptime(postData["end"], "%m/%d/%Y")
                print "mdY", end
            except ValueError:
                errors.append("Invalid end date format.")
        # cannot further process the request if dates are not validate
        if len(errors) > 0:
            return {"success": False, "error_list": errors}
        # future date check
        # start date
        if start < datetime.now():
            errors.append("Start date must be in the future")
        if end < datetime.now():
            errors.append("End date must be in the future")
        # start date must be before end date
        if start > end:
            errors.append("Start date must be before end date")
        if len(errors) == 0:
            # no errors CREATE trip (and ADD user to it) and return it with a success code
            trip = Trip.objects.create(destination=postData["destination"], plan=postData["plan"], start=start, end=end, creator=curr_user)
            trip.members.add(curr_user)
            return {"success": True, "trip_object": trip}
        else:
            return {'success': False, "error_list": errors}

    def joinTrip(self, user_id, trip_id):
        msgs = []
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            msgs.append("User not found! Please log in again")
        try:
            trip = Trip.objects.get(id=trip_id)
        except Trip.DoesNotExist:
            msgs.append("Trip not found! Please select another trip")
        # check to see if user is already a memeber of this trip
        if user in trip.members.all():
            msgs.append("You have already been added to this trip!")
        # if validations pass then ADD user to the members in instance of the Trip object (as the variable trip)
        if len(msgs) == 0:
            trip.members.add(user)
            msgs.append("You have successfully joined the trip to {}". format(trip.destination))
            return {"success": True, "msgs":msgs}
        else:
            return {"success": False, "msgs":msgs}

class Trip(models.Model):
    destination = models.CharField(max_length=45)
    plan = models.CharField(max_length=140)
    start = models.DateTimeField()
    end = models.DateTimeField()
    creator = models.ForeignKey(User)
    members = models.ManyToManyField(User, related_name="trips")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = TripManager()
