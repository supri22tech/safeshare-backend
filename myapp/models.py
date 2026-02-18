from django.db import models
from django.contrib.auth.models import User
# Create your models here.


class Expert(models.Model):
    LOGIN=models.ForeignKey(User,on_delete=models.CASCADE)
    Name=models.CharField(max_length=200)
    Email=models.CharField(max_length=200)
    Phone=models.BigIntegerField()
    place=models.CharField(max_length=200)
    pin=models.IntegerField()
    district=models.CharField(max_length=200)
    status=models.CharField(max_length=200)
    Photo=models.FileField()
    proof=models.FileField()

class User_table(models.Model):
    LOGIN=models.ForeignKey(User,on_delete=models.CASCADE)
    name=models.CharField(max_length=200)
    email=models.CharField(max_length=200)
    phone=models.BigIntegerField()
    place=models.CharField(max_length=200)
    pincode=models.BigIntegerField()
    district=models.CharField(max_length=200)
    gender=models.CharField(max_length=200)
    status=models.CharField(max_length=20,default='user')
    identity_status=models.CharField(max_length=20,default='user')
    dob=models.DateField()
    photo=models.FileField()
    adhaaer=models.FileField(null=True,blank=True)

class Complaints(models.Model):
    USER=models.ForeignKey(User_table,on_delete=models.CASCADE)
    date=models.DateField()
    complaints=models.CharField(max_length=200)
    reply=models.CharField(max_length=200)

class feedback(models.Model):
    user=models.ForeignKey(User_table,on_delete=models.CASCADE)
    date=models.DateField()
    feedback=models.CharField(max_length=200)
    rating=models.FloatField()

class review(models.Model):
    user=models.ForeignKey(User_table,on_delete=models.CASCADE)
    expert=models.ForeignKey(Expert,on_delete=models.CASCADE)
    date=models.DateField()
    review=models.CharField(max_length=200)
    rating=models.FloatField()

class post(models.Model):
    user = models.ForeignKey(User_table, on_delete=models.CASCADE)
    date = models.DateField()
    photo=models.FileField()
    caption=models.CharField(max_length=200)
    description=models.CharField(max_length=200)

class comment(models.Model):
    user = models.ForeignKey(User_table, on_delete=models.CASCADE)
    post = models.ForeignKey(post, on_delete=models.CASCADE)
    comment=models.CharField(max_length=200)
    date=models.DateField()

class like(models.Model):
    post=models.ForeignKey(post,on_delete=models.CASCADE)
    user=models.ForeignKey(User_table,on_delete=models.CASCADE)
    date=models.DateField()
    like_dislike=models.CharField(max_length=200)


class IdentityTheft(models.Model):
    Theft_user=models.ForeignKey(User_table,on_delete=models.CASCADE,related_name="tuser")
    user=models.ForeignKey(User_table,on_delete=models.CASCADE,related_name="nuser")
    date=models.DateField()
    status=models.CharField(max_length=200)



class tips(models.Model):
    expert=models.ForeignKey(Expert,on_delete=models.CASCADE)
    tips=models.CharField(max_length=200)
    date=models.DateField()
    details=models.CharField(max_length=200)

class Friend_request(models.Model):
    from_id=models.ForeignKey(User_table,on_delete=models.CASCADE,related_name="fr_fid")
    to_id=models.ForeignKey(User_table,on_delete=models.CASCADE,related_name="fr_tid")
    date=models.DateField()
    status=models.CharField(max_length=200)

class parent(models.Model):
    LOGIN = models.ForeignKey(User, on_delete=models.CASCADE)
    student=models.ForeignKey(User_table,on_delete=models.CASCADE)
    name=models.CharField(max_length=200)
    email=models.CharField(max_length=200)
    phone=models.BigIntegerField()
    Housename=models.CharField(max_length=200)
    place=models.CharField(max_length=200)

class guideline(models.Model):
    expert=models.ForeignKey(Expert,on_delete=models.CASCADE)
    date=models.DateField()
    title=models.CharField(max_length=200)
    details=models.CharField(max_length=200)

class ImageNotification(models.Model):
    post= models.ForeignKey(post,on_delete=models.CASCADE)
    user= models.ForeignKey(User_table, on_delete=models.CASCADE)
    date=models.DateField()
    status=models.CharField(max_length=200)

class IdentityNotification(models.Model):
    fuser= models.ForeignKey(User_table, on_delete=models.CASCADE,related_name="fid")
    tuser= models.ForeignKey(User_table, on_delete=models.CASCADE,related_name="tid")
    date=models.DateField()
    status=models.CharField(max_length=200)



class share_account(models.Model):
    POST=models.ForeignKey(post,on_delete=models.CASCADE)
    from_id=models.ForeignKey(User_table,on_delete=models.CASCADE,related_name='from_id')
    to_id=models.ForeignKey(User_table,on_delete=models.CASCADE,related_name='to_id')
    date=models.DateField()
    status=models.CharField(max_length=200)



class Chat_table(models.Model):
    from_id=models.ForeignKey(User_table,on_delete=models.CASCADE,related_name='cfrom_id')
    to_id=models.ForeignKey(User_table,on_delete=models.CASCADE,related_name='cto_id')
    date=models.DateField()
    message=models.CharField(max_length=2000)

class Share_User_Account(models.Model):
    from_user=models.ForeignKey(User_table,on_delete=models.CASCADE,related_name='from_user')
    to_user=models.ForeignKey(User_table,on_delete=models.CASCADE,related_name='to_user')
    share_user=models.ForeignKey(User_table,on_delete=models.CASCADE,related_name='share_user')
    date=models.DateField()
    status=models.CharField(max_length=50)




