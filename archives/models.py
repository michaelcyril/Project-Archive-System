from django.db import models
from django.contrib.auth.models import User
import datetime

date =  datetime.datetime.now().year
first = str(date-1)
date = str(date)

date = f'{first}/{date}'
class Level(models.Model):
    name = models.CharField(max_length=30)
    date_created = models.DateField(auto_now_add=True)
    class Meta:
        db_table = "Level"
    
    def __str__(self):
        return self.name
    

class Department(models.Model):
    name = models.CharField(max_length=100)

    class Meta:
        db_table = "Department"

    def __str__(self):
        return self.name
    

class Awards(models.Model):
    name = models.CharField(max_length=100)
    # level = models.ForeignKey(Level,on_delete=models.CASCADE)
    department = models.ForeignKey(Department,on_delete=models.CASCADE)
    class Meta:
        db_table = "Awards"
    
    def __str__(self):
        return self.name
    

class Student(models.Model):
    GENDER = (
        ('Male','Male'),
        ('Female','Female')
    )
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    gender = models.CharField(choices=GENDER, max_length=20)
    regNo =  models.CharField(unique=True,max_length=14)
    NTA_Level = models.IntegerField(null=True,blank=True)
    # level = models.ForeignKey(Level,null=True,blank=True,on_delete=models.CASCADE)
    department = models.ForeignKey(Department,null=True,on_delete=models.CASCADE)
    academic_year = models.CharField(max_length=12)
    mobile = models.CharField(max_length=14, null=True,blank=True)
    photo = models.ImageField(upload_to='Images/Profile/Student',default='default.jpg', null=True, blank=True)
    course = models.CharField(max_length=100)
    
    class Meta:
        db_table = "Student"
        
    def __str__(self):
        return self.regNo

class Staff(models.Model):
    GENDER = (
        ('Male','Male'),
        ('Female','Female')
    )
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    gender = models.CharField(choices=GENDER, max_length=20)
    staff_id =  models.CharField(max_length=10, unique=True)
    department = models.ForeignKey(Department,on_delete=models.CASCADE)
    mobile = models.CharField(max_length=14, null=True,blank=True)
    photo = models.ImageField(upload_to='Images/Profile/Staff',default='default.jpg', null=True, blank=True)
    # level = models.ForeignKey(Level,null=True,blank=True,on_delete=models.CASCADE)
    
    class Meta:
        db_table = "Staff"

    def __str__(self):
        return self.user.first_name


class ProjectType(models.Model):
    name = models.CharField(max_length=30)
    date_created = models.DateField(auto_now_add=True)
    department= models.ForeignKey(Department,null=True,blank=True,on_delete=models.CASCADE)  
    
    class Meta:
        db_table = "project_type"
      
    def __str__(self):
        return self.name


class Project(models.Model):
    title = models.CharField(null=True,blank=True,max_length=200)
    student = models.OneToOneField(Student, on_delete=models.CASCADE)
    project_type = models.ForeignKey(ProjectType,on_delete=models.CASCADE,null=True,blank=True)
    department = models.ForeignKey(Department,on_delete=models.CASCADE,null=True,blank=True)
    date_created = models.DateField(auto_now_add=True)
    accepted = models.BooleanField(default=False)
    note = models.TextField(null=True,blank=True)

    class Meta:
        db_table = "project"

    def __str__(self):
        return self.title


class ProjectDocument(models.Model):
    project = models.OneToOneField(Project,null=True, blank=True, on_delete=models.CASCADE)
    file = models.FileField(upload_to='Document/Projects',null=True,blank=True)
    # preview = models.FileField(upload_to='Document/Preview',null=True,blank=True)
    submitted = models.BooleanField(null=True,blank=True,default=False)
    date_created = models.DateField(auto_now_add=True)
    # cover = models.ImageField(upload_to='Document/Cover', null=True, blank=True)

    class Meta:
        db_table = "document"       

class Progress(models.Model):
    STATUS = (
        ('Pending','Pending'),
        ('Approved','Approved'),
        ('Rejected','Rejected')
    )
    document = models.OneToOneField(ProjectDocument,on_delete=models.CASCADE,null=True,blank=True)
    prog = models.IntegerField(default=0,null=True,blank=True) 
    date_created = models.DateField(auto_now_add=True)
    status = models.CharField(choices=STATUS, max_length=20)

    class Meta:
        db_table = "progress"

    def __str__(self):
        return str(self.prog)

class Submission(models.Model):
    when = models.DateTimeField(auto_now=False,auto_now_add=False)
    # level = models.ForeignKey(Level,on_delete=models.CASCADE, null=True,blank=True)
    academic_year =  models.CharField(max_length=50,null=True,blank=True,default=date)
    status = models.BooleanField(default=True)
    department = models.ForeignKey(Department,on_delete=models.CASCADE, null=True,blank=True)
    
    class Meta:
        db_table = "submission"

# class Upvote(models.Model):
#     user = models.ForeignKey(User,on_delete=models.CASCADE)
#     document = models.ManyToManyField(ProjectDocument)
    
#     class Meta:
#         db_table = "Likes"
