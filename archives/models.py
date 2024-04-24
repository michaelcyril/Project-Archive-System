from django.db import models
from django.contrib.auth.models import User
import datetime
# Create your models here.


# class User(AbstractUser):
#     class Meta:
#         db_table = 'users'
date =  datetime.datetime.now().year
first = str(date-1)
date = str(date)

date = f'{first}/{date}'
class Level(models.Model):
    name = models.CharField(max_length=30)
    date_created = models.DateField(auto_now_add=True)
    
    
    
    def __str__(self):
        return self.name

    class Meta:
        db_table = "Level"

class Department(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

    class Meta:
        db_table = "Department"

        
class Awards(models.Model):
    name = models.CharField(max_length=100)
    level = models.ForeignKey(Level,on_delete=models.CASCADE)
    department = models.ForeignKey(Department,on_delete=models.CASCADE)
    
    def __str__(self):
        return self.name

    class Meta:
        db_table = "Awards"
   
class Student(models.Model):
    GENDER = (('Male','Male'),('Female','Female'))
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    gender = models.CharField(choices=GENDER, max_length=20)
    regNo =  models.CharField(unique=True,max_length=14)
    NTA_Level = models.IntegerField(null=True,blank=True)
    level = models.ForeignKey(Level,null=True,blank=True,on_delete=models.CASCADE)
    department = models.ForeignKey(Department,null=True,on_delete=models.CASCADE)
    academic_year = models.CharField(max_length=12)
    mobile = models.CharField(max_length=14, null=True,blank=True)
    photo = models.ImageField(upload_to='profile_pic',default='default.jpg', null=True, blank=True)
    course = models.CharField(max_length=100)
    
    def __str__(self):
        return self.regNo

    class Meta:
        db_table = "Student"


class Staff(models.Model):
    GENDER = (('Male','Male'),('Female','Female'))
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    gender = models.CharField(choices=GENDER, max_length=20)
    staff_id =  models.IntegerField(unique=True)
    department = models.ForeignKey(Department,on_delete=models.CASCADE)
    mobile = models.TextField(max_length=14, null=True,blank=True)
    photo = models.ImageField(upload_to='profile_pic/staff',default='default.jpg', null=True, blank=True)
    level = models.ForeignKey(Level,null=True,blank=True,on_delete=models.CASCADE)

    def __str__(self):
        return self.user.first_name

    class Meta:
        db_table = "Staff"
        
        
class Project_type(models.Model):
    name = models.CharField(max_length=30)
    date_created = models.DateField(auto_now_add=True)
    department= models.ForeignKey(Department,null=True,blank=True,on_delete=models.CASCADE)    
    def __str__(self):
        return self.name

    class Meta:
        db_table = "project_type"
        
class Project(models.Model):
    title = models.CharField(null=True,blank=True,max_length=200)
    student = models.OneToOneField(Student, on_delete=models.CASCADE)
    project_type = models.ForeignKey(Project_type,on_delete=models.CASCADE,null=True,blank=True)
    department = models.ForeignKey(Department,on_delete=models.CASCADE,null=True,blank=True)
    date_created = models.DateField(auto_now_add=True)
    
    
    def __str__(self):
        return self.title

    class Meta:
        db_table = "project"



class Document(models.Model):
    project = models.OneToOneField(Project,null=True, blank=True, on_delete=models.CASCADE)
    file = models.FileField(upload_to='projects',null=True,blank=True)
    preview = models.FileField(upload_to='preview',null=True,blank=True)
    submitted = models.BooleanField(null=True,blank=True,default=False)
    date_created = models.DateField(auto_now_add=True)
    cover = models.ImageField(upload_to='cover', null=True, blank=True)
    # def __str__(self):
    #     return self.id

    class Meta:
        db_table = "document"       

class Progress(models.Model):
    document = models.OneToOneField(Document,on_delete=models.CASCADE,null=True,blank=True)
    #staff = models.ForeignKey(Staff,on_delete=models.CASCADE,null=True,blank=True)
    prog = models.IntegerField(default=0,null=True,blank=True)
    #comments = models.TextField(max_length=100,null=True,blank=True) 
    date_created = models.DateField(auto_now_add=True)
    
    status = models.BooleanField(null=True,blank=True,default=False)
    
    def __str__(self):
        return str(self.prog)

    class Meta:
        db_table = "progress"  
        
class Submission(models.Model):
    when = models.DateTimeField(auto_now=False,auto_now_add=False)
    level = models.ForeignKey(Level,on_delete=models.CASCADE, null=True,blank=True)
    academic_year =  models.CharField(max_length=50,null=True,blank=True,default=date)
    status = models.BooleanField(default=True)
    department = models.ForeignKey(Department,on_delete=models.CASCADE, null=True,blank=True)
    class Meta:
        db_table = "submission"

class Likes(models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE)
    document = models.ManyToManyField(Document)
    class Meta:
        db_table = "Likes"
    # class Meta:
    #     default_permissions = ('')
    #     permissions = (('like_document','Can like documents'),('can_hire','Can hire employees'),('hire','Can employees'))
    # staff = models.OneToOneField(Staff,on_delete=models.CASCADE,null=True,blank=True)
    