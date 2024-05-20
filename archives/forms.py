from django import forms
from .models import Student, Staff


class StudentForm(forms.ModelForm):
    firstname = forms.CharField(max_length=100)
    lastname = forms.CharField(max_length=100)
    email = forms.EmailField()

    class Meta:
        model = Student
        fields = [
            "firstname",
            "lastname",
            "regNo",
            "NTA_Level",
            "email",
            "mobile",
            "course",
            "academic_year",
            "department",
            "gender",
        ]

class StaffForm(forms.ModelForm):
    firstname = forms.CharField(max_length=100)
    lastname = forms.CharField(max_length=100)
    email = forms.EmailField()

    class Meta:
        model = Staff
        fields = [
            "firstname",
            "lastname",
            "email",
            "staff_id",
            "mobile",
            "department",
            "gender",
        ]