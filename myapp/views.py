import smtplib
from email.mime.text import MIMEText

from django.contrib.auth import authenticate, login
from django.db.models.query_utils import Q
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.hashers import check_password, make_password
from django.contrib.auth.models import Group
from django.core.files.storage import FileSystemStorage
from django.db.models import Sum, Value, F, FloatField
from django.db.models.functions import Coalesce
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect
from django.contrib import messages
# Create your views here.
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import authenticate, login, update_session_auth_hash, logout
from django.utils import timezone

from myapp.encode_faces import enf
from myapp.recognize_face import rec_face_image
from .models import *
from django.contrib.auth.models import User
# Create your views here.
from datetime import datetime
import cv2
import numpy as np
from PIL import Image
# from .encode_faces import enf

def loginget(request):
    # hg = User.objects.get(id=request.user.id)
    # hg.set_password="admin123"
    # hg.save()
    return render(request,"index.html")

def login_post(request):


    uname=request.POST['uname']
    password=request.POST['password']

    print(request.POST)

    obj=authenticate(request,username=uname,password=password)



    if obj is not None:
        if obj.groups.filter(name="Admin").exists():
            login(request,obj)
            return redirect('/myapp/admin_home')
        elif obj.groups.filter(name="Expert").exists():
            ob=Expert.objects.get(LOGIN__id=obj.id)
            if ob.status == "Accepted":
                login(request, obj)
                return redirect('/myapp/expert_home')
            else:
                messages.warning(request,'You are not verified yet!')
                return redirect('/myapp/')
        else:
            messages.warning(request, 'Invalid Username or password')
            return redirect('/myapp/')
    else:
        messages.warning(request, 'Invalid Username or password')
        return redirect('/myapp/')


def changepassword(request):
    if request.method == "POST":
        oldpasspwrd= request.POST["cpassword"]
        newpassword= request.POST["npassword"]


        print(request.user)
        f=check_password(oldpasspwrd,request.user.password)
        if f:
            user=request.user
            user.set_password(newpassword)
            user.save()

            logout(request)

            messages.success(request, 'Password changed successfully')
            return redirect('/myapp/')
        else:
            messages.warning(request, 'Invalid Current Password')
            return redirect('/myapp/change_password/')


    return render(request,"admin/change password.html")






def admin_home(request):
    users = User_table.objects.all().count()
    experts = Expert.objects.all().count()
    # We pass these as integers to the frontend
    return render(request, "adminindex.html", {
        'user_count': users,
        'expert_count': experts
    })

def verify_expert(request):
    ob=Expert.objects.all()
    return render(request,"admin/verifyexpert.html",{"data":ob})

def verify_expert_accept(request,id):
    ob=Expert.objects.get(id=id)
    ob.status='Accepted'
    ob.save()
    return redirect("/myapp/verify_expert/")

def verify_expert_reject(request,id):
    ob=Expert.objects.get(id=id)
    ob.status='Rejected'
    ob.save()
    return redirect("/myapp/verify_expert/")

def view_complaint(request):
    ob = Complaints.objects.all()
    return render(request, "admin/view complaint.html",{"data":ob})

def sendreply(request,id):
    reply=request.POST['reply']
    ob=Complaints.objects.get(id=id)
    ob.reply=reply
    ob.save()
    return redirect('/myapp/view_complaint/')

def view_expert_review(request):
    ob = review.objects.all()
    return render(request,"admin/view expert review.html",{"data":ob})

def view_users(request):
    ob=User_table.objects.all()
    return render(request,"admin/view users.html",{"data":ob})

def view_feedback(request):
    ob=feedback.objects.all()
    return render(request,"admin/view feedback.html",{"data":ob})

def change_password(request):
    return render(request,"admin/change password.html")

def admin_view_post(request):
    ob=post.objects.all()
    return render(request,"admin/view post.html",{"data":ob})



def expert_registration(request):
    return render(request,"register.html")


def expert_registration_post(request):
    name=request.POST['textfield']
    email=request.POST['textfield2']
    phone=request.POST['textfield3']
    photo=request.FILES['textfield4']
    place=request.POST['textfield6']
    pin=request.POST['textfield7']
    district=request.POST['textfield8']
    username=request.POST['textfield9']
    password=request.POST['textfield10']
    proof = request.FILES['proof']
    if User.objects.filter(username=username).exists():
        messages.warning(request,'Username already taken')
        data={
            'name':name,
            'email':email,
            'phone':phone,
            'place':place,
            'pin':pin,
            'district':district,
        }
        return render(request,'register.html',{'data':data})

    user = User.objects.create(username=username, password=make_password(password), email=email, first_name=name)
    user.save()
    user.groups.add(Group.objects.get(name="Expert"))

    ob=Expert()
    ob.LOGIN=user
    ob.Name=name
    ob.Email=email
    ob.Phone=phone
    ob.place=place
    ob.pin=pin
    ob.district=district
    ob.status='pending'
    ob.Photo=photo
    ob.proof=proof
    ob.save()
    messages.success(request,"Registred")

    return redirect("/myapp/")


def expert_update_profile_post(request):
    name=request.POST['textfield']
    email=request.POST['textfield2']
    phone=request.POST['textfield3']

    place=request.POST['textfield6']
    pin=request.POST['textfield7']
    district=request.POST['textfield8']


    ob=Expert.objects.get(LOGIN__id=request.user.id)

    ob.Name=name
    ob.Email=email
    ob.Phone=phone
    ob.place=place
    ob.pin=pin
    ob.district=district
    ob.status='pending'
    if 'textfield4' in request.FILES:
        photo = request.FILES['textfield4']
        ob.Photo=photo
    if 'proof' in request.FILES:
        proof = request.FILES['proof']
        ob.proof=proof
    ob.save()


    return redirect("/myapp/expert_view_profile/")





def expert_add_guideline(request):
    return render(request,"expert/add guideline.html")

def expert_add_guideline_post(request):
    title = request.POST['textfield']
    des = request.POST['textfield2']
    ob = guideline()
    ob.expert = Expert.objects.get(LOGIN__id=request.user.id)
    ob.date = datetime.today()
    ob.title = title
    ob.details = des
    ob.save()
    return redirect("/myapp/expert_view_guideline/")



def expert_update_guideline_post(request):
    title = request.POST['textfield']
    des = request.POST['textfield2']
    ob = guideline.objects.get(id=request.session['gid'])

    ob.title = title
    ob.details = des
    ob.save()
    return redirect("/myapp/expert_view_guideline/")




def expert_add_tips(request):
    return render(request, "expert/add tips.html")

def expert_add_tips_post(request):
        tip = request.POST['textfield']
        details = request.POST['textfield2']
        ob = tips()
        ob.expert=Expert.objects.get(LOGIN__id=request.user.id)
        ob.tips = tip
        ob.details = details
        ob.date = datetime.today()
        ob.save()
        return redirect("/myapp/expert_view_tips/")

def expert_update_tips_post(request):
        tip = request.POST['textfield']
        details = request.POST['textfield2']
        ob = tips.objects.get(id=request.session['tid'])

        ob.tips = tip
        ob.details = details

        ob.save()
        return redirect("/myapp/expert_view_tips/")

def expert_home(request):
    return render(request,"expert/expert_home.html")


def expert_edit_profile(request):
    return render(request, 'expert/expert_home.html')

def expert_view_guideline(request):
    ob=guideline.objects.filter(expert__LOGIN__id=request.user.id)
    return render(request,"expert/view guideline.html",{"data":ob})

def expert_view_profile(request):
    ob=Expert.objects.get(LOGIN__id=request.user.id)
    print(ob)
    print(ob.Name)
    return render(request,"expert/edit profile.html",{"data":ob})

def expert_view_tips(request):
    ob=tips.objects.filter(expert__LOGIN__id=request.user.id)
    return render(request,"expert/view tips.html",{"data":ob})


def expert_edit_tips(request,id):
    ob=tips.objects.get(id=id)
    request.session['tid']=id

    return render(request,"expert/edittips.html",{"data":ob})

def expert_delete_tips(request,id):
    ob=tips.objects.get(id=id)
    ob.delete()

    return redirect("/myapp/expert_view_tips/#")

def expert_delete_guideline(request,id):
    ob=guideline.objects.get(id=id)
    ob.delete()

    return redirect("/myapp/expert_view_guideline/#")

def expert_edit_guideline(request,id):
    ob=guideline.objects.get(id=id)
    request.session['gid']=id

    return render(request,"expert/editguideline.html",{"data":ob})





# =================================================
# =================================================
# =================================================
# =================================================


from django.contrib.auth import authenticate
from django.http import JsonResponse
from .models import User_table, parent

def android_login(request):
    uname = request.POST['uname']
    passwd = request.POST['passwd']

    print(request.POST)

    obj = authenticate(request, username=uname, password=passwd)

    if obj is not None:

        if obj.groups.filter(name="User").exists():

            try:
                u = User_table.objects.get(LOGIN=obj)

                if u.status == 'blocked':
                    return JsonResponse({
                        "task": "blocked",
                        "message": "Account blocked due to verification failure"
                    })
                if u.status == 'minor':
                    return JsonResponse({
                        "task": "blocked",
                        "message": "Account blocked due to verification failure(minor user)"
                    })

                if u.status == 'verified_minor':
                    if not parent.objects.filter(student=u).exists():
                        return JsonResponse({
                            "task": "parent_required",
                            "message": "Parent verification required"
                        })

                return JsonResponse({
                    "task": "valid",
                    "type": "User",
                    "id": str(obj.id),
                    "img": str(u.photo.url),
                    "name": str(u.name),
                    "status": str(u.status),
                })

            except User_table.DoesNotExist:
                return JsonResponse({
                    "task": "error",
                    "message": "User profile not found"
                })

        if obj.groups.filter(name="Parent").exists():
            return JsonResponse({
                "task": "valid",
                "type": "Parent",
                "id": str(obj.id)
            })

    return JsonResponse({
        "task": "invalid",
        "message": "Invalid username or password"
    })

def android_login1(request):
    id = request.POST['id']

    ob=User_table.objects.get(id=id)
    ob.status="verified"
    ob.save()
    return JsonResponse({
        "task": "ok",

    })

import cv2
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

import subprocess
import os
from datetime import datetime, date
from django.contrib.auth.models import User, Group
from django.contrib.auth.hashers import make_password
from django.http import JsonResponse
from .models import User_table, parent

from datetime import date

def calculate_age(dob):
    today = date.today()
    return today.year - dob.year - (
        (today.month, today.day) < (dob.month, dob.day)
    )
def theftdetection(ob):
    try:
        fname=ob.photo.path
        res=rec_face_image(fname)
        for i in res:
            if str(i)!=str(ob.id):
                return str(i)
    except:
        pass
    return "ok"


def check_image_quality(image_path):
    try:
        img = cv2.imread(image_path)
        if img is None:
            return False, "Unable to read image"

        height, width = img.shape[:2]
        if width < 300 or height < 400:
            return False, "Image resolution too low (minimum 300x400)"

        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        laplacian_var = cv2.Laplacian(gray, cv2.CV_64F).var()
        print(f"Image quality check - Laplacian variance: {laplacian_var}")

        if laplacian_var < 50:
            print(f"Image rejected - too blurry (variance: {laplacian_var})")
            return False, "Aadhaar card image is blurry. Please upload a clearer image."
            return False, "Aadhaar card image is blurry. Please upload a clearer image."

        return True, "Quality check passed"
    except Exception as e:
        return False, f"Error processing image: {str(e)}"


import logging
logger = logging.getLogger(__name__)

def android_user_registration(request):
    logger.info("=== android_user_registration started ===")
    
    try:
        iname = request.POST.get('name', '')
        email = request.POST.get('email', '')
        phone = request.POST.get('phone', '')
        place = request.POST.get('place', '')
        pincode = request.POST.get('pincode', '')
        district = request.POST.get('district', '')
        gender = request.POST.get('gender', '')
        dob_str = request.POST.get('dob', '')
        username = request.POST.get('username', '')
        password = request.POST.get('password', '')
        
        logger.info(f"Received registration request - name: {iname}, email: {email}, phone: {phone}")
        
        photo = request.FILES.get('photo')
        adhaaer = request.FILES.get('adhaaer')
        
        if not all([iname, email, phone, place, pincode, district, gender, dob_str, username, password, photo, adhaaer]):
            logger.warning("Missing required fields")
            return JsonResponse({"status": "na", "message": "Missing required fields"})
        
        user = User.objects.create(
            username=username,
            password=make_password(password),
            email=email,
            first_name=iname
        )
        user.save()
        user.groups.add(Group.objects.get(name="User"))
        logger.info(f"User created with ID: {user.id}")

        ob = User_table()
        ob.LOGIN = user
        ob.name = iname
        ob.email = email
        ob.phone = phone
        ob.place = place
        ob.pincode = pincode
        ob.district = district
        ob.gender = gender
        ob.photo = photo
        ob.adhaaer = adhaaer
        ob.dob = dob_str

        fs = FileSystemStorage()
        fp = fs.save(adhaaer.name, adhaaer)
        image_path = r"C:\Users\lenovo\PycharmProjects\safeshare\media/" + fp
        logger.info(f"Aadhaar image saved: {image_path}")

        is_valid, message = check_image_quality(image_path)
        logger.info(f"Image quality check: {is_valid}, {message}")
        if not is_valid:
            user.delete()
            logger.warning(f"Image quality failed: {message}")
            return JsonResponse({"status": "na", "message": message})

        try:
            from myapp.dob_ocr import extract_details
            logger.info("Starting OCR extraction...")
            dob, name, aadhaar, gender, full_text = extract_details(image_path)
            logger.info(f"OCR Extracted - Name: {name}, DOB: {dob}, Aadhaar: {aadhaar}, Gender: {gender}")
        except Exception as e:
            logger.error(f"OCR Error: {str(e)}", exc_info=True)
            dob, name, aadhaar, gender = None, None, None, None

        if not name:
            logger.warning("OCR failed to extract name from image")
            user.delete()
            return JsonResponse({"status": "na", "message": "Could not extract name from Aadhaar image"})
        
        if not dob:
            logger.warning("OCR failed to extract DOB from image")
            user.delete()
            return JsonResponse({"status": "na", "message": "Could not extract DOB from Aadhaar image"})
        
        name_match = False
        if name and iname:
            ocr_name_clean = name.lower().replace(' ', '').strip()
            input_name_clean = iname.lower().replace(' ', '').strip()
            name_match = ocr_name_clean in input_name_clean or input_name_clean in ocr_name_clean
            logger.info(f"Name matching - OCR: '{name}', Input: '{iname}', Match: {name_match}")
        
        if name_match and dob:
            try:
                dob_parts = dob.split("/")
                if len(dob_parts) == 3:
                    dob_year = dob_parts[2]
                    age = int(datetime.now().strftime("%Y")) - int(dob_year)
                    logger.info(f"Calculated age: {age}")
                else:
                    age = 0
                    logger.warning(f"Invalid DOB format: {dob}")
            except Exception as e:
                logger.error(f"DOB parsing error: {str(e)}")
                age = 0

            if age >= 18:
                ob.status = "verified"
                ob.save()
                logger.info("User verified as adult")

                try:
                    res = theftdetection(ob)
                    logger.info(f"Theft detection result: {res}")
                except Exception as e:
                    logger.error(f"Theft detection error: {str(e)}", exc_info=True)
                    res = "error"

                if res == "ok":
                    try:
                        enf([(ob.id, str(ob.photo))])
                        logger.info("Face embedding saved")
                    except Exception as e:
                        logger.error(f"Face embedding error: {str(e)}", exc_info=True)

                    otp = random.randint(10000, 99999)
                    logger.info(f"Generated OTP: {otp}")
                    
                    ob.status = "pending"
                    ob.save()
                    
                    try:
                        sendmail(email, otp)
                        logger.info(f"OTP sent to email: {email}")
                    except Exception as e:
                        logger.error(f"Email send error: {str(e)}", exc_info=True)
                    
                    return JsonResponse({"status": "ok", "message": "verified_adult", "otp": str(otp), "id": ob.id})
                else:
                    ob.identity_status = "theft"
                    ob.save()
                    uob = ob.LOGIN
                    uob.delete()
                    logger.warning("Theft detected, user deleted")
                    return JsonResponse({"status": "ok", "message": "Theft Detected"})
            else:
                ob.status = "minor"
                ob.save()
                logger.info("User marked as minor")

                try:
                    res = theftdetection(ob)
                    logger.info(f"Theft detection result (minor): {res}")
                except Exception as e:
                    logger.error(f"Theft detection error: {str(e)}", exc_info=True)
                    res = "error"

                if res == "ok":
                    try:
                        enf([(ob.id, str(ob.photo))])
                        logger.info("Face embedding saved (minor)")
                    except Exception as e:
                        logger.error(f"Face embedding error: {str(e)}", exc_info=True)

                    otp = random.randint(10000, 99999)
                    logger.info(f"Generated OTP (minor): {otp}")
                    
                    try:
                        sendmail(email, otp)
                        logger.info(f"OTP sent to email: {email}")
                    except Exception as e:
                        logger.error(f"Email send error: {str(e)}", exc_info=True)
                    
                    return JsonResponse({"status": "ok", "message": "verified_minor", "otp": str(otp), "id": ob.id})
                else:
                    ob.identity_status = "theft"
                    ob.save()
                    uob = ob.LOGIN
                    uob.delete()
                    logger.warning("Theft detected (minor), user deleted")
                    return JsonResponse({"status": "ok", "message": "Theft Detected"})
        else:
            logger.warning(f"Name verification failed. OCR: {name}, Input: {iname}, DOB: {dob}")
            user.delete()
            return JsonResponse({"status": "ok", "message": "pending"})
            
    except Exception as e:
        logger.error(f"Registration error: {str(e)}", exc_info=True)
        try:
            if 'user' in locals():
                user.delete()
        except:
            pass
        return JsonResponse({"status": "na", "message": "Registration failed. Please try again."})
import random
def sendmail(email,otp):

    try:

            try:
                gmail = smtplib.SMTP('smtp.gmail.com', 587)
                gmail.ehlo()
                gmail.starttls()
                gmail.login('supriyapv222006@gmail.com', 'mkuttkdohtmodcqa')
                print("login=======")
            except Exception as e:
                return "na"
            msg = MIMEText("Your verification OTP : " + str(otp))
            print(msg)
            msg['Subject'] = 'Safe Share'
            msg['To'] = email
            msg['From'] = 'supriyapv222006@gmail.com'

            print("ok====")

            try:
                gmail.send_message(msg)
            except Exception as e:
                return "na"
            return "ok"

    except Exception as e:
       return "ok"
def insert_feedback(request):
    feeedbackk=request.POST['feedback']
    lid=request.POST['lid']
    rating=request.POST['rating']
    ob=feedback()
    ob.user=User_table.objects.get(LOGIN__id=lid)
    ob.feedback=feeedbackk
    ob.rating=rating
    ob.date=datetime.today()
    ob.save()
    return JsonResponse({"status": "ok"})

def veryfy_user(request):

    lid=request.POST['lid']
    ob=User_table.objects.get(id=lid)
    ob.status = "minor"
    ob.save()
    return JsonResponse({"status": "ok"})


def view_feedback_content(request):
    ob = feedback.objects.all()
    data = []
    for i in ob:
        data.append({
            'user':str(i.user.name),
            'user_photo':str(i.user.photo.url),
            'date':str(i.date),
            'feedback':str(i.feedback),
            'rating':str(i.rating),
        })
    print(data)
    return JsonResponse({'status':'ok',"data":data})

def insert_review(request):
    lid=request.POST['lid']
    Expert=request.POST['Expert']
    print(Expert)
    revieww = request.POST['review']
    rating=request.POST['rating']

    ob = review()
    ob.user = User_table.objects.get(LOGIN__id=lid)
    ob.expert_id=Expert
    ob.review = revieww
    ob.rating = rating
    ob.date = datetime.today()
    ob.save()
    return JsonResponse({"status": "ok"})

def insert_post(request):
    lid=request.POST['lid']
    caption = request.POST['caption']
    description=request.POST['description']
    photo = request.POST['photo']

    ob = post()
    ob.user = User_table.objects.get(LOGIN__id=lid)
    ob.caption = caption
    ob.description= description
    ob.photo=photo
    ob.date = datetime.today()
    ob.save()

    return JsonResponse({"task": "ok"})





def insert_like(request):
    lid=request.POST['lid']
    post = request.POST['post']


    ob = like()
    ob.user = User_table.objects.get(LOGIN__id=lid)
    ob.post = post.objects.get(id=post)
    ob.like_dislike= 1
    ob.date = datetime.today()

    return JsonResponse({"task": "ok"})

def Friend_requests(request):
    id = request.POST['User_table']
    status=request.POST['status']

    ob = Friend_request()
    ob.from_id=id
    ob.status=status
    ob.date = datetime.today()

    return JsonResponse({"task": "ok"})



def user_view_post(request):
    lid=request.POST['lid']
    l=[]

    var=post.objects.filter(user__LOGIN_id=lid)
    for i in var:
        l.append({
            'id':str(i.id),
            'date':str(i.date),
            'photo':str(i.photo.url),
            'caption':str(i.caption),
            'description':str(i.description),
        })
    return JsonResponse({"task": "ok"})

def view_image_notification(request):
    lid=request.POST['lid']
    l=[]
    print(lid)
    var=ImageNotification.objects.filter(user__LOGIN__id=lid)
    for i in var:
        l.append({
            'id':i.id,
            'date':str(i.date),
            'post':"/media/or_"+str(i.post.photo),
            'name':i.post.user.name,
            'status':str(i.status),
        })

    return JsonResponse({"task": "ok","data":l})

def view_parant(request):
    lid = request.POST['lid']
    l = []

    var = parent.objects.filter(student__LOGIN_id=lid)
    for i in var:
        l.append({
            'name':str(i.name),
            'email':str(i.email),
            'phone':str(i.phone),
            'Housename':str(i.Housename),
            'place':str(i.place),
        })

    return JsonResponse({"task": "ok"})

def view_review(request):
    # lid = request.POST['lid']
    expert = request.POST['expert']
    l = []

    # var = review.objects.filter(user__LOGIN_id=lid)
    var = review.objects.filter(expert_id=expert)
    for i in var:
        l.append({
            'date':str(i.date),
            'review':str(i.review),
            'rating':str(i.rating),

        })

    return JsonResponse({"status": "ok" , 'data':l})


def user_viewreply(request):
    lid = request.POST['lid']
    ob=Complaints.objects.filter(USER__LOGIN_id=lid)

    data=[]
    for i in ob:
        data.append({
            'cid': i.id,
            'complaint': i.complaints,
            'date': i.date,
            'reply':i.reply,
        })

    return JsonResponse({'status':'ok',"data":data})

def insert_complaint(request):
    complaints=request.POST['complaint']
    lid=request.POST['lid']

    ob = Complaints()
    ob.USER=User_table.objects.get(LOGIN__id=lid)
    ob.complaints=complaints
    ob.date=datetime.today()
    ob.reply='pending'
    ob.save()
    return JsonResponse({"status": "ok"})

def view_expert(request):
    ob=Expert.objects.all()
    data=[]
    for i in ob:
        data.append({
            'id':i.id,
            'name':str(i.Name),
            'email':str(i.Email),
            'phone':str(i.Phone),
            'place':str(i.place),
            'pin':str(i.pin),
            'district':str(i.district),
            'photo': i.Photo.url,
        })
    return JsonResponse({'status':'ok',"data":data})

def view_shared_content(request):
    ob = post.objects.all()
    data = []
    for i in ob:
        data.append({
            'date':str(i.date),
            'photo':request.build_absolute_uri(i.photo.url),
            'caption':str(i.caption),
            'description':str(i.description),
        })
    return JsonResponse({'status': 'ok', "data": data})


def view_parants(request):
    lid=request.POST['lid']
    ob=parent.objects.filter(student__LOGIN__id=lid)
    data=[]
    for i in ob:
        data.append({
            'name':str(i.name),
            'email':str(i.email),
            'phone':str(i.phone),
            'Housename':str(i.Housename),
            'place':str(i.place),
        })
    return JsonResponse({'status': 'ok', "data": data})

def view_post(request):
    lid=request.POST['lid']
    ob=post.objects.exclude(user__LOGIN__id=lid)
    data = []
    for i in ob:
        obl=like.objects.filter(post__id=i.id)
        obl1=like.objects.filter(post__id=i.id,user__LOGIN__id=lid)
        s="0"
        if len(obl1)>0:
            s="1"

        data.append({
            'id':str(i.id),
            'date':str(i.date),
            'photo':str(i.photo.url),
            'name':str(i.user.name),
            'caption':str(i.caption),
            'description':str(i.description),
            'lc':str(len(obl)),
            's':str(s),
        })
    print(data)
    return JsonResponse({'status': 'ok', "data": data})

def parent_view_post(request):
    lid=request.POST['lid']
    par=parent.objects.get(LOGIN__id=lid)
    ob=post.objects.filter(user_id=par.student.id)
    data = []
    for i in ob:
        obl=like.objects.filter(post__id=i.id)
        obl1=like.objects.filter(post__id=i.id,user__LOGIN__id=lid)
        s="0"
        if len(obl1)>0:
            s="1"

        data.append({
            'id':str(i.id),
            'date':str(i.date),
            'photo':str(i.photo),
            'name':str(i.user.name),
            'caption':str(i.caption),
            'description':str(i.description),
            'lc':str(len(obl)),
            's':str(s),
        })
    print(data)
    return JsonResponse({'status': 'ok', "data": data})




def parent_view_activity(request):
    try:
        lid = request.POST['lid']
        par = parent.objects.get(LOGIN__id=lid)
        kid = par.student

        activity_log = []
        img_url = request.build_absolute_uri('/')[:-1]  # To get full image paths

        # 1. POSTS
        for p in post.objects.filter(user=kid):
            activity_log.append({
                'type': 'post',
                'description': f"Shared a new post",
                'time': p.date.strftime("%b %d, %I:%M %p"),
                'image': p.photo.url if p.photo else "",
                'target_owner': kid.name,
                'target_caption': p.caption,
                'target_desc': p.description,
                'raw_date': p.date
            })

        # 2. LIKES
        for l in like.objects.filter(user=kid):
            activity_log.append({
                'type': 'like',
                'description': f"Liked {l.post.user.name}'s post",
                'time': l.date.strftime("%b %d, %Y"),
                'image': l.post.photo.url if l.post.photo else "",
                'target_owner': l.post.user.name,
                'target_caption': l.post.caption,
                'target_desc': l.post.description,
                'raw_date': l.date
            })

        # 3. COMMENTS
        for c in comment.objects.filter(user=kid):
            activity_log.append({
                'type': 'comment',
                'description': f"Commented on {c.post.user.name}'s post",
                'kid_comment': c.comment,  # The specific text the kid wrote
                'time': c.date.strftime("%b %d, %Y"),
                'image': c.post.photo.url if c.post.photo else "",
                'target_owner': c.post.user.name,
                'target_caption': c.post.caption,
                'target_desc': c.post.description,
                'raw_date': c.date
            })

        activity_log.sort(key=lambda x: x['raw_date'], reverse=True)
        return JsonResponse({'status': 'ok', 'data': activity_log, 'kid_name': kid.name})

    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)})
def android_like(request):
    lid=request.POST['lid']
    id=request.POST['id']

    obl1=like.objects.filter(post__id=id,user__LOGIN__id=lid)
    if len(obl1)>0:
        obl1=obl1[0]
        obl1.delete()
    else:
        ob=like()
        ob.post=post.objects.get(id=id)
        ob.user=User_table.objects.get(LOGIN__id=lid)
        ob.date=datetime.today()
        ob.like_dislike="1"
        ob.save()


    return JsonResponse({'status': 'ok'})
def view_my_post(request):
    lid=request.POST['lid']
    ob=post.objects.filter(user__LOGIN__id=lid)
    data = []
    for i in ob:
        data.append({
            'id':str(i.id),
            'date':str(i.date),
            'photo':str(i.photo),
            'name':str(i.user.name),
            'caption':str(i.caption),
            'description':str(i.description),
        })
    print(data)
    return JsonResponse({'status': 'ok', "data": data})
def view_reply(request):
    ob=Complaints.objects.all()
    data = []
    for i in ob:
        data.append({
            'date':str(i.date),
            'complaints':str(i.complaints),
            'reply':str(i.reply),
        })
    return JsonResponse({'status': 'ok', "data": data})

def user_view_review(request):
    eid=request.POST['eid']
    ob=review.objects.filter(expert__id=eid)
    data=[]
    for i in ob:
        data.append({
            'date':str(i.date),
            'review':str(i.review),
            'rating':str(i.rating),
            'user':str(i.user.name),
            'user_photo':str(i.user.photo.url),
        })
    return JsonResponse({'status': 'ok', "data": data})

###############################################################


def reg_view_student(request):
    a=User_table.objects.filter(status='minor')
    l=[]
    for i in a:
        l.append({
            "id":str(i.id),
            "name":str(i.name),
        })
    return JsonResponse({'status':'ok','data':l})



def parent_registration(request):
    name=request.POST['name']
    student=request.POST['student']
    email=request.POST['email']
    phone=request.POST['phone']
    Housename=request.POST['Housename']
    place=request.POST['place']
    username=request.POST['username']
    password=request.POST['password']


    user = User.objects.create(username=username, password=make_password(password), email=email, first_name=name)
    user.save()
    user.groups.add(Group.objects.get(name="Parent"))


    ob = parent()
    ob.student = User_table.objects.get(id=student)
    ob.name = name
    ob.email = email
    ob.phone = phone
    ob.Housename = Housename
    ob.place = place
    ob.LOGIN=user
    ob.save()

    student_user = ob.student
    if student_user.status == 'minor':
        student_user.status = 'verified_minor'
        student_user.save()

    return JsonResponse({"status": "ok"})

def parent_view_profile(request):
    lid=request.POST['lid']
    a = parent.objects.filter(LOGIN__id=lid)
    data = []
    for i in a:
        data.append({
            'name':str(i.name),'email':str(i.email),'phone':str(i.phone),'Housename':str(i.Housename),'place':str(i.place),
        }
        )
    return JsonResponse({"status": "ok","data":data})

def view_activity(request):
    lid = request.POST['lid']
    par=parent.objects.get(LOGIN_id=lid)
    a = post.objects.filter(user_id=par.student.id)
    data = []
    for i in a:
        data.append({
            'date':str(i.name),'photo':str(i.photo),'caption':str(i.caption),'description':str(i.description),
        }
        )
    return JsonResponse({"status": "ok", "data": data})
import os
# from  .recognize_face import rec_face_image
@csrf_exempt
def post_insert(request):
    if request.method == "POST":
        user_id = request.POST.get("user")
        caption = request.POST.get("caption")
        description = request.POST.get("description")

        photo = request.FILES['photo']

        user = User_table.objects.get(LOGIN__id=user_id)
        fs = FileSystemStorage()
        path = fs.save(photo.name, photo)

        image = cv2.imread(r"C:\Users\lenovo\PycharmProjects\safeshare\media/" + path)
        cv2.imwrite(r"C:\Users\lenovo\PycharmProjects\safeshare\media/or_" + path, image)

        ob=post()
        ob.user=user
        ob.caption=caption
        ob.description=description
        ob.date=datetime.today()
        ob.photo=path
        ob.save()
        data=str(ob.id)+"**"+caption+"**"+description+"**"+str(path)+"**"+str(ob.date)

        # ==========================================
        try:

            hp = subprocess.run([
                r'C:\Python310\python.exe',
                r'C:\Users\lenovo\PycharmProjects\safeshare\myapp\blockchainupload.py'
            ], input=data.encode('utf-8'))

        except Exception as e:
            print(e)

        # ==========================================


        output_dir = 'cropped_faces'
        img = cv2.imread(os.path.join(r"C:\Users\lenovo\PycharmProjects\safeshare\media",str(ob.photo)))
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        # Detect faces
        faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=3)
        print(faces)
        print(len(faces))
        for i, (x, y, w, h) in enumerate(faces):
            face = img[y:y + h, x:x + w]
            face_path = os.path.join(output_dir, f'face_{i+1}.jpg')

            cv2.imwrite(face_path, face)
            res = rec_face_image(face_path)
            print(res,ob.user.id)
            for j in res:
                if str(j) != str(ob.user.id):
                    try:
                        blurred = cv2.blur(face, (80,80))
                        img[y:y + h, x:x + w] = blurred
                        obn = ImageNotification()
                        obn.user = User_table.objects.get(id=j)
                        obn.post = ob
                        obn.date = datetime.today()
                        obn.status = 'pending'
                        obn.save()
                    except:
                        pass

        fn = path
        print(fn)
        cv2.imwrite(r"C:\Users\lenovo\PycharmProjects\safeshare\media/" + fn, img)

        return JsonResponse({"status": "success"})

def my_post(request):
    if request.method == "POST":
        user_id = request.POST.get("user")
        caption = request.POST.get("caption")
        description = request.POST.get("description")

        photo = request.FILES['photo']

        user = User_table.objects.get(LOGIN__id=user_id)

        post.objects.create(
            user=user,
            caption=caption,
            description=description,
            date=datetime.today(),
            photo=photo,
        )

        return JsonResponse({"status": "success"})

def view_comment(request):
    pid=request.POST['pid']
    a = comment.objects.filter(post__id=pid)
    data = []
    for i in a:
        data.append({
            'user':str(i.user.name),'comment':str(i.comment),'date':str(i.date),
        }
        )
    print(data,"=============")
    return JsonResponse({"status": "ok","data":data})



def add_comment(request):
    lid = request.POST['lid']
    pid = request.POST['pid']
    cmd = request.POST['comment']

    text_vector = vectorizer.transform([cmd])
    prediction = model.predict(text_vector)[0]

    # 4. Map the 0/1 result to a readable string
    # 1 = Bullying, 0 = Non-Bullying
    label = "Bullying" if int(prediction) == 1 else "Non-Bullying"
    if label=="Non-Bullying":
        ob = comment()
        ob.user=User_table.objects.get(LOGIN=lid)
        ob.post=post.objects.get(id=pid)
        ob.comment=cmd
        ob.date=datetime.now().date()
        ob.save()

        return JsonResponse({"status": "ok"})
    return JsonResponse({"status": "Bullying"})


def view_otherusers(request):
    lid=request.POST['lid']


    ids=[]
    ob=Friend_request.objects.filter(from_id__LOGIN__id=lid)
    ob1=Friend_request.objects.filter(to_id__LOGIN__id=lid)
    for i in ob:
        ids.append(i.to_id.id)
    for i in ob1:
        ids.append(i.from_id.id)
    print(ids)
    ob=User_table.objects.exclude(LOGIN_id=lid).exclude(id__in=ids)
    data=[]
    for i in ob:
        data.append({
            'id':str(i.id),
            'name':str(i.name),
            'photo':str(i.photo.url),
            'email':str(i.email),
            'gender':str(i.gender),
            'phone':str(i.phone),
        })
    print(data)
    return JsonResponse({'status': 'ok', "data": data})

def view_myFriends(request):
    lid=request.POST['lid']

    ids=[]
    ob=Friend_request.objects.filter(from_id__LOGIN__id=lid,status="Friend")
    ob1=Friend_request.objects.filter(to_id__LOGIN__id=lid,status="Friend")
    for i in ob:
        ids.append(i.to_id.id)
    for i in ob1:
        ids.append(i.from_id.id)
    print(ids)
    ob=User_table.objects.filter(id__in=ids)
    data=[]
    for i in ob:
        data.append({
            'id':str(i.LOGIN.id),
            'name':str(i.name),
            'photo':str(i.photo.url),
            'email':str(i.email),
            'gender':str(i.gender),
            'phone':str(i.phone),
        })
    print(data)
    return JsonResponse({'status': 'ok', "data": data})

def accept_notification(request):
    nid=request.POST['nid']
    ob=ImageNotification.objects.get(id=nid)
    ob.status='Accept'
    ob.save()
    pob=ob.post

    obb = ImageNotification.objects.filter(post__id=pob.id, status="Accept")
    ids = []
    for i in obb:
        ids.append(str(i.user.id))
    ids.append(str(pob.user.id))
    image = cv2.imread(r"C:\Users\lenovo\PycharmProjects\safeshare\media/or_" + str(pob.photo))
    # cv2.imwrite(r"C:\Users\salva\PycharmProjects\scam_reporting_system\media/or_" + path, image)

    #

    # Read the input image
    img = image
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # Detect faces
    faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=3)

    print(f"Detected {len(faces)} face(s)")

    # Create output directory if needed
    output_dir = 'cropped_faces'

    # Crop and save/display faces
    for i, (x, y, w, h) in enumerate(faces):
        face = img[y:y + h, x:x + w]
        face_path = os.path.join(output_dir, f'face_{i+1}.jpg')
        cv2.imwrite(face_path, face)
        res = rec_face_image(face_path)
        for j in res:
            if str(j) not in ids:
                blurred = cv2.blur(face, (80,80))
                img[y:y + h, x:x + w] = blurred

    fn = str(pob.photo)
    cv2.imwrite(r"C:\Users\lenovo\PycharmProjects\safeshare\media/" + fn, img)

    return JsonResponse({'status': 'Accepted'})

def reject_notification(request):
    nid = request.POST['nid']
    ob = ImageNotification.objects.get(id=nid)
    ob.status = 'Reject'
    ob.save()
    return JsonResponse({'status': 'Rejected'})

def send_request(request):
    lid=request.POST['from_lid']
    to_lid=request.POST['to_lid']
    ob=Friend_request()
    ob.from_id=User_table.objects.get(LOGIN__id=lid)
    ob.to_id=User_table.objects.get(id=to_lid)
    ob.date=datetime.today()
    ob.status='pending'
    ob.save()
    return JsonResponse({'status': 'ok'})

def view_request(request):
    lid=request.POST['lid']
    a = Friend_request.objects.filter(to_id__LOGIN=lid,status='pending')
    data = []
    for i in a:
        data.append({
            'photo':str(i.from_id.photo.url),
            'user':str(i.from_id.name),
            'email':str(i.from_id.email),
            'phone':str(i.from_id.phone),
            'gender':str(i.from_id.gender),
            'date':str(i.date),
            'id':str(i.id),
        }
        )
    return JsonResponse({"status": "ok","data":data})

def accept_request(request):
    id=request.POST['id']
    a = Friend_request.objects.get(id=id)
    a.status="Friend"
    a.save()
    return JsonResponse({"status": "ok"})

def reject_request(request):
    id=request.POST['id']
    a = Friend_request.objects.get(id=id)
    a.status="Rejected"
    a.save()
    return JsonResponse({"status": "ok"})


def flut_send_chat(request):
    print("flut_send_chat POST:", request.POST)
    fromid = request.POST.get('fromid')
    toid = request.POST.get('toid')

    message = request.POST.get('message')

    if not fromid or not toid or not message:
        return JsonResponse({'status': 'error', 'msg': 'Missing parameters'})

    try:
        from_user = User_table.objects.get(LOGIN__id=int(fromid))
    except User.DoesNotExist:
        return JsonResponse({'status': 'error', 'msg': 'From user not found'})

    try:
        # Strict: toid must be an auth_user id
        to_user = User_table.objects.get(LOGIN__id=int(toid))
    except User.DoesNotExist:
        return JsonResponse({'status': 'error', 'msg': 'Recipient user not found (toid must be auth user id)'})

    chat = Chat_table.objects.create(
        from_id=from_user,
        to_id=to_user,
        date=datetime.now().date(),
        message=message
    )
    print("flut_send_chat created:", chat.id)
    return JsonResponse({'status': 'ok', 'msg': 'Message sent', 'chat_id': chat.id})



def flut_view_chat(request):
    print("flut_view_chat POST:", request.POST)
    fromid = request.POST.get('fromid')
    toid = request.POST.get('toid')

    if not fromid or not toid:
        return JsonResponse({'status': 'error', 'msg': 'Missing parameters'})

    try:
        from_user = User_table.objects.get(LOGIN__id=int(fromid))
    except User.DoesNotExist:
        return JsonResponse({'status': 'error', 'msg': 'From user not found'})

    try:
        to_user = User_table.objects.get(LOGIN__id=int(toid))
    except User.DoesNotExist:
        return JsonResponse({'status': 'error', 'msg': 'Recipient user not found (toid must be auth user id)'})

    chats = Chat_table.objects.filter(
        Q(from_id=from_user, to_id=to_user) | Q(from_id=to_user, to_id=from_user)
    ).order_by('id')

    res = []
    for c in chats:
        res.append({
            'id': c.id,
            'fromid': c.from_id.LOGIN.id,
            'toid': c.to_id.id,
            'message': c.message,
            'date': str(c.date)
        })

    print("flut_view_chat result count:", len(res))
    print(res)
    return JsonResponse({'status': 'ok', 'data': res})

def delete_post(request):
    pid=request.POST['pid']
    post.objects.get(id=pid).delete()
    return JsonResponse({'status':'ok'})

def ViewSharedPost(request):
    fid=request.POST['fid']
    lid=request.POST['lid']
    print(fid,lid)
    ob=share_account.objects.filter(from_id__LOGIN__id=fid,to_id__LOGIN__id=lid)
    mdata=[]
    for i in ob:
        data={
            'post':i.POST.photo.url,
            'caption':i.POST.caption,
            'description':i.POST.description,
            'post_owner':i.POST.user.name,
            'post_id':i.POST.id,
        }
        mdata.append(data)
    print(mdata)
    return JsonResponse({'status':'ok','data':mdata})

def UserViewTips(request):
    eid=request.POST['eid']
    ob=tips.objects.filter(expert__id=eid)
    mdata=[]
    for i in ob:
        data={
            'tips':i.tips,
            'details':i.details,
            'date':i.date,
        }
        mdata.append(data)
    print(mdata)
    return JsonResponse({'status':'ok','data':mdata})

def ShareUserAccount(request):
    lid=request.POST['lid']
    toid=request.POST['to']
    share_user=request.POST['accId']

    ob=Share_User_Account()
    ob.from_user=User_table.objects.get(LOGIN=lid)
    ob.to_user=User_table.objects.get(LOGIN=toid)
    ob.share_user=User_table.objects.get(LOGIN=share_user)
    ob.date=datetime.now().date()
    ob.status='shared'
    ob.save()
    return JsonResponse({"status":"ok"})

def share_post(request):
    lid=request.POST['lid']
    to=request.POST['to']
    post=request.POST['post']
    ob=share_account()
    ob.POST_id=post
    ob.from_id=User_table.objects.get(LOGIN__id=lid)
    ob.to_id=User_table.objects.get(LOGIN__id=to)
    ob.date=datetime.today()
    ob.status='shared'
    ob.save()
    return JsonResponse({"status": "ok"})


def view_myFriends_for_share(request):
    lid=request.POST['lid']
    accid=request.POST['accid']
    obj=User_table.objects.get(LOGIN=accid)
    usr_id=obj.id
    ids=[]
    ob=Friend_request.objects.filter(from_id__LOGIN__id=lid,status="Friend")
    ob1=Friend_request.objects.filter(to_id__LOGIN__id=lid,status="Friend")
    for i in ob:
        ids.append(i.to_id.id)
    for i in ob1:
        ids.append(i.from_id.id)
    print(ids)
    ob=User_table.objects.filter(id__in=ids).exclude(id=usr_id)
    data=[]
    for i in ob:
        data.append({
            'id':str(i.LOGIN.id),
            'name':str(i.name),
            'photo':str(i.photo.url),
            'email':str(i.email),
            'gender':str(i.gender),
            'phone':str(i.phone),
        })
    print(data)
    return JsonResponse({'status': 'ok', "data": data})
import joblib
model = joblib.load('cyber_model.pkl')
vectorizer = joblib.load('vectorizer.pkl')
def send_view_shared_details(request):
    lid=request.POST['lid']
    usr=User_table.objects.get(LOGIN=lid)
    uid=usr.id
    obj=Share_User_Account.objects.filter(share_user=uid)
    l=[]
    for i in obj:
        l.append({
            "id":str(i.id),
            "from_user":str(i.from_user.name),
            "to_user":str(i.to_user.name),
            "date":str(i.date),
            "status":str(i.status),
        })
    print(l)
    return JsonResponse({"status":"ok",'data':l})

def user_profile(request):
    lid=request.POST['lid']
    user=User_table.objects.get(LOGIN_id=lid)

    return JsonResponse({
        'name':user.name,

    })


def update_profile(request):
    lid=request.POST['lid']
    user=User_table.objects.get(LOGIN_id=lid)

    user.name=request.POST['name']

    if 'photo' in request.FILES:
        user.photo=request.FILES['photo']



    user.save()
    return HttpResponse("ok")


# Add these views to your Django views.py file

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import User_table
import json


@csrf_exempt
def get_user_profile(request):
    """
    Fetch user profile data
    POST params: lid (login id)
    """
    try:
        lid = request.POST.get('lid')

        if not lid:
            return JsonResponse({
                'status': 'error',
                'message': 'Login ID is required'
            })

        # Get user data
        user = User_table.objects.get(LOGIN_id=lid)

        return JsonResponse({
            'status': 'success',
            'data': {
                'name': user.name,
                'email': user.email,
                'phone': user.phone,
                'place': user.place,
                'pincode': user.pincode,
                'district': user.district,
                'gender': user.gender,
                'status': user.status,
                'identity_status': user.identity_status,
                'dob': str(user.dob),
                'photo': str(user.photo) if user.photo else '',
                'aadhaar': str(user.adhaaer) if user.adhaaer else None,
            }
        })

    except User_table.DoesNotExist:
        return JsonResponse({
            'status': 'error',
            'message': 'User not found'
        })
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        })


@csrf_exempt
def clear_face_pickles(request):
    """
    Clear the face encodings pickle file (for development purposes)
    """
    try:
        import os
        pickle_path = r'C:\Users\lenovo\PycharmProjects\safeshare\faces.pickles'
        
        if os.path.exists(pickle_path):
            os.remove(pickle_path)
            return JsonResponse({
                'status': 'success',
                'message': 'Face pickle file deleted successfully'
            })
        else:
            return JsonResponse({
                'status': 'error',
                'message': 'Face pickle file not found'
            })
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        })


@csrf_exempt
def update_user_profile(request):
    """
    Update user profile data
    POST params: lid, name, email, phone, place, pincode, district, gender, dob
    FILES: photo (optional), aadhaar (optional)
    """
    try:
        lid = request.POST.get('lid')

        if not lid:
            return JsonResponse({
                'status': 'error',
                'message': 'Login ID is required'
            })

        # Get user
        user = User_table.objects.get(LOGIN_id=lid)

        # Update text fields
        user.name = request.POST.get('name', user.name)
        user.email = request.POST.get('email', user.email)
        user.phone = request.POST.get('phone', user.phone)
        user.place = request.POST.get('place', user.place)
        user.pincode = request.POST.get('pincode', user.pincode)
        user.district = request.POST.get('district', user.district)
        user.gender = request.POST.get('gender', user.gender)

        # Update DOB if provided
        dob = request.POST.get('dob')
        if dob:
            user.dob = dob

        # Update photo if provided


        # Update Aadhaar if provided
        if 'aadhaar' in request.FILES:
            user.adhaaer = request.FILES['aadhaar']
        user.save()
        if 'photo' in request.FILES:
            user.photo = request.FILES['photo']
            user.save()
            enf([(user.id, str(user.photo))])


        return JsonResponse({
            'status': 'success',
            'message': 'Profile updated successfully',
            'data': {
                'name': user.name,
                'email': user.email,
                'phone': user.phone,
                'place': user.place,
                'pincode': user.pincode,
                'district': user.district,
                'gender': user.gender,
                'status': user.status,
                'identity_status': user.identity_status,
                'dob': str(user.dob),
                'photo': str(user.photo) if user.photo else '',
                'aadhaar': str(user.adhaaer) if user.adhaaer else None,
            }
        })

    except User_table.DoesNotExist:
        return JsonResponse({
            'status': 'error',
            'message': 'User not found'
        })
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        })