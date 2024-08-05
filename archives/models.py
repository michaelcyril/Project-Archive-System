from django.db import models
from django.contrib.auth.models import User
import datetime

date =  datetime.datetime.now().year
first = str(date-1)
date = str(date)

date = f'{first}/{date}'
class Level(models.Model):
    name = models.CharField(max_length=30)
    created_at = models.DateField(auto_now_add=True)
    class Meta:
        db_table = "Level"
    
    def __str__(self):
        return self.name
    
class AcademicYear(models.Model):
    academic_year = models.CharField(max_length=20)
    
    def __str__(self):
        return self.academic_year
    

class Department(models.Model):
    name = models.CharField(max_length=100)

    class Meta:
        db_table = "Department"

    def __str__(self):
        return self.name

class Program(models.Model):
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=10)
    department = models.ForeignKey(Department,on_delete=models.CASCADE) # type: ignore
    level = models.ForeignKey(Level,on_delete=models.CASCADE)
    created_at = models.DateField(auto_now_add=True)
    class Meta:
        db_table = "Program"
        
    
    def __str__(self):
        return self.name
    

class Awards(models.Model):
    name = models.CharField(max_length=100)
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
    # level = models.OneToOneField(Level, on_delete=models.CASCADE, null=True,blank=True)
    # department = models.ForeignKey(Department,null=True,on_delete=models.CASCADE)
    program = models.ForeignKey(Program, on_delete=models.CASCADE)
    academic_year = models.OneToOneField(AcademicYear, on_delete=models.CASCADE)
    mobile = models.CharField(max_length=14, null=True,blank=True)
    photo = models.ImageField(upload_to='Images/Profile/Student',default='default.jpg', null=True, blank=True)
    # course = models.CharField(max_length=100)
    
    class Meta:
        db_table = "Student"
        
    def __str__(self):
        return self.user.first_name + " " + self.user.last_name

class Staff(models.Model):
    GENDER = (
        ('Male','Male'),
        ('Female','Female')
    )
    
    TYPE = (
        (1, "Supervisor"),
        (2, "coordinator")
    )
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    type = models.PositiveIntegerField(choices=TYPE)
    gender = models.CharField(choices=GENDER, max_length=20)
    staff_id =  models.CharField(max_length=10, unique=True)
    department = models.ForeignKey(Department,on_delete=models.CASCADE)
    mobile = models.CharField(max_length=14, null=True,blank=True)
    photo = models.ImageField(upload_to='Images/Profile/Staff',default='default.jpg', null=True, blank=True)

    
    class Meta:
        db_table = "Staff"

    def __str__(self):
        return self.user.first_name + " " + self.user.last_name

    def get_user_type_display(self):
        return dict(self.TYPE).get(self.type, 'Unknown')


class ProjectType(models.Model):
    name = models.CharField(max_length=30)
    date_created = models.DateField(auto_now_add=True)
    department= models.ForeignKey(Department,null=True,blank=True,on_delete=models.CASCADE)
    mentor = models.ForeignKey(Staff, on_delete=models.CASCADE)
    
    class Meta:
        db_table = "project_type"
      
    def __str__(self):
        return self.name


class Project(models.Model):
    title = models.CharField(null=True, blank=True, max_length=200)
    student = models.OneToOneField(Student, on_delete=models.CASCADE)
    project_type = models.ForeignKey(ProjectType, on_delete=models.CASCADE, null=True, blank=True)
    department = models.ForeignKey(Department, on_delete=models.CASCADE, null=True, blank=True)
    date_created = models.DateField(auto_now_add=True)
    accepted = models.BooleanField(default=False)
    note = models.TextField(null=True, blank=True)

    class Meta:
        db_table = "project"

    def __str__(self):
        return self.title


class Upvote(models.Model):
    supervisor = models.ForeignKey(Staff, on_delete=models.CASCADE)
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    date_created = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"{self.supervisor.user} upvoted {self.project.title}"


class ProjectDocument(models.Model):
    DOCUMENT_TYPE = (
        ("Proposal", "Proposal"),
        ("Mini One", "Mini One"),
        ("Mini Two", "Mini Two"),
        ("Final", "Final"),
    )
    project = models.ForeignKey(Project,null=True, blank=True, on_delete=models.CASCADE)
    file = models.FileField(upload_to='Document/Projects',null=True,blank=True)
    submitted = models.BooleanField(null=True,blank=True,default=False)
    date_created = models.DateField(auto_now_add=True)
    document_type = models.CharField(choices=DOCUMENT_TYPE, max_length=20, null=True, blank=True)
    cover = models.ImageField(upload_to='Document/Cover', null=True, blank=True)

    class Meta:
        db_table = "document"       

    def __str__(self):
        return self.project.title

class Progress(models.Model):
    STATUS = (
        ('Pending','Pending'),
        ('Approved','Approved'),
        ('Rejected','Rejected')
    )
    document = models.OneToOneField(ProjectDocument,on_delete=models.CASCADE,null=True,blank=True)
    date_created = models.DateField(auto_now_add=True)
    status = models.CharField(choices=STATUS, max_length=20)

    class Meta:
        db_table = "progress"

    def __str__(self):
        return str(self.status)

class Submission(models.Model):
    when = models.DateTimeField(auto_now=False,auto_now_add=False)
    academic_year =  models.CharField(max_length=50,null=True,blank=True,default=date)
    status = models.BooleanField(default=True)
    department = models.ForeignKey(Department,on_delete=models.CASCADE, null=True,blank=True)
    
    class Meta:
        db_table = "submission"

class StudentRequest(models.Model):
    REQUEST_STATUS = (
        ('Pending','Pending'),
        ('Accepted','Accepted'),
        ('Rejected','Rejected')
    )
    student = models.ForeignKey(Student,on_delete=models.CASCADE)
    project = models.ForeignKey(Project,on_delete=models.CASCADE)
    description = models.TextField()
    date_created = models.DateField(auto_now_add=True)
    status = models.CharField(choices=REQUEST_STATUS, max_length=20, default='Pending')

    class Meta:
        db_table = "student_request"

    def __str__(self):
        return self.student.user.first_name + " " + self.student.user.last_name

class Comment(models.Model):
    document = models.ForeignKey("ProjectDocument", on_delete=models.CASCADE)
    supervisor = models.ForeignKey(Staff, on_delete=models.CASCADE)
    text = models.TextField()
    date_created = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "comment"

    def __str__(self):
        return f"Comment by {self.supervisor.user.username} on {self.document.project.title}"
