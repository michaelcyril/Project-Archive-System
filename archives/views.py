from django.shortcuts import redirect, render
from django.db.models import Q
import pandas as pd
import os
import datetime
from django.shortcuts import HttpResponseRedirect
from django.contrib.auth.decorators import *
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404
from fuzzywuzzy import fuzz
import PyPDF2
import fitz
import re
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import redirect
from django.views.generic import TemplateView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy, reverse
from django.views.generic import View
from django.views.generic import ListView
from django.views.generic import View
from django.contrib.auth.hashers import make_password
from .forms import StudentForm, StaffForm
from django.contrib.auth.models import User, Group, Permission
from django.views.generic import View
from django.contrib import messages
from django.contrib.auth.views import PasswordChangeView
from django.views.generic import FormView
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import *
from django.db.models import Sum
from django.core.exceptions import ObjectDoesNotExist
from django.http import FileResponse
import os
from django.conf import settings


# CCBV


PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))

poppler_path = os.path.join(PROJECT_DIR, "..", "poppler-23.01.0", "Library", "bin")
cover = os.path.join(PROJECT_DIR, "..", "media", "coverpage")
profile = os.path.join(PROJECT_DIR, "..", "media", "profile_pic")


# def check_connection():
#     try:
#         response = requests.get('http://www.google.com')
#         if response.status_code == 200:
#             return True
#     except:
#         pass

#     return False

######################################### FUNCTION VIEWS #########################################


def preview_pdf(request, pk):
    try:
        d = ProjectDocument.objects.filter(id=pk)
        return render(
            request, "html/dist/preview-document.html", {"side": "a", "d": d, "id": pk}
        )
    except Exception as e:
        messages.error(request, e)
        return HttpResponseRedirect(request.META.get("HTTP_REFERER"))

def upvote(request):
    try:
        if request.method == "POST":
            project_id = request.POST.get("project_id")
            project = Project.objects.get(pk=project_id)
            supervisor = Staff.objects.get(user=request.user)
            
            # if supervisor upvote already exists, delete it
            if Upvote.objects.filter(project=project, supervisor=supervisor).exists():
                upvote = Upvote.objects.get(project=project, supervisor=supervisor)
                upvote.delete()
                messages.success(request, "Upvote removed successfully")
            else:
                upvote = Upvote.objects.create(project=project, supervisor=supervisor)
                messages.success(request, "Upvote added successfully")
            
            return HttpResponseRedirect(request.META.get("HTTP_REFERER"))
          
    except Exception as e:
        messages.error(request, "Something went wrong")
        return HttpResponseRedirect(request.META.get("HTTP_REFERER"))

######################################### CCBV #########################################


class LoginRequiredView(LoginRequiredMixin):
    login_url = "/login/"


class LoginView(FormView):
    form_class = AuthenticationForm
    template_name = "html/dist/login.html"
    success_url = reverse_lazy("home")

    def get_success_url(self):
        requested_url = self.request.GET.get("next")
        if requested_url:
            return requested_url
        return super().get_success_url()

    def form_valid(self, form):
        user = authenticate(
            username=form.cleaned_data["username"],
            password=form.cleaned_data["password"],
        )
        if user is not None:
            login(self.request, user)
            messages.success(self.request, "Login successful")
            return super().form_valid(form)
        else:
            messages.error(self.request, "Invalid username or password")
            return self.form_invalid(form)

    def form_invalid(self, form):
        messages.error(self.request, "Invalid username or password")
        return super().form_invalid(form)

    def get(self, request, *args, **kwargs):
        # If the user is already logged in, they shouldn't be visiting the login page again
        if request.user.is_authenticated:
            return redirect(self.get_success_url())
        return super().get(request, *args, **kwargs)


class LogoutView(LoginRequiredView, View):
    def get(self, request, *args, **kwargs):
        logout(request)
        return redirect("login")


class ChangePasswordView(LoginRequiredView, PasswordChangeView):
    template_name = "html/dist/change_password.html"
    success_url = reverse_lazy("login")

    def form_valid(self, form):
        messages.success(self.request, "Password changed successfully.")
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, "Something went wrong.")
        return super().form_invalid(form)


class DashboardView(LoginRequiredView, TemplateView):
    template_name = "html/dist/index.html"

    def get_student_data(self):
        # This method will now return counts instead of querysets.
        if hasattr(self.request.user, "student"):
            document_count = ProjectDocument.objects.filter(
                project__student=self.request.user.student
            ).count()
            request_count = StudentRequest.objects.filter(
                student=self.request.user.student
            ).count()
            return document_count, request_count
        return 0, 0

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        try:
            context["document_count"], context["request_count"] = (
                self.get_student_data()
            )
            context["student"] = Student.objects.all().count()
            context["department"] = Department.objects.all().count()
            context["project"] = Project.objects.all().count()
            context["staff"] = Staff.objects.all().count()
            context["b"] = Progress.objects.all()
            context["projecttype"] = ProjectType.objects.all().count()
            context["completedprojects"] = ProjectDocument.objects.filter(
                document_type="Final"
            ).count()
            context["side"] = "dashboard"
        except:
            messages.error(self.request, "Something went wrong")
            # return HttpResponseRedirect(self.request.META.get("HTTP_REFERER"))
        return context


class AssessmentView(LoginRequiredView, TemplateView):
    template_name = "html/dist/assessment.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.user.is_superuser:
            date = datetime.datetime.now().year
            first = str(date - 1)
            date = str(date)
            date = f"{first}/{date}"
            finalB = Progress.objects.all()
            sub = Submission.objects.all()
            ex = True
        elif self.request.user.is_staff:
            date = datetime.datetime.now().year
            first = str(date - 1)
            date = str(date)
            date = f"{first}/{date}"
            finalB = Progress.objects.filter(
                document__project__student__level__id=self.request.user.staff.level.id
            ).filter(document__project__student__academic_year=date)
            sub = (
                Submission.objects.filter(level_id=self.request.user.staff.level.id)
                .filter(academic_year=date)
                .filter(department_id=self.request.user.staff.department.id)
            )
            ex = Submission.objects.filter(
                level_id=self.request.user.staff.level.id,
                department_id=self.request.user.staff.department.id,
            ).exists()
        context["side"] = "assessment"
        context["b"] = finalB
        context["sub"] = sub
        context["ex"] = ex
        return context


class StudentView(LoginRequiredView, TemplateView):
    template_name = "html/dist/students.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        exclude_perm = [1, 2, 3, 4, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 37]
        context["p"] = Permission.objects.exclude(id__in=exclude_perm)
        context["students"] = Student.objects.all().order_by("id")
        context["departments"] = Department.objects.all()
        context["academic_years"] = AcademicYear.objects.all()
        context["programs"] = Program.objects.all()
        context["g"] = Group.objects.all()
        return context


class StudentODView(LoginRequiredView, TemplateView):
    template_name = "html/dist/students_od.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        exclude_perm = [1, 2, 3, 4, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 37]
        context["p"] = Permission.objects.exclude(id__in=exclude_perm)
        context["s"] = Student.objects.filter(level__lte=6, level__gte=4)
        context["departments"] = Department.objects.all()
        context["g"] = Group.objects.all()
        return context


class AddStudentView(LoginRequiredMixin, FormView):
    template_name = "html/dist/students.html"
    form_class = StudentForm

    def form_valid(self, form):
        data = form.cleaned_data
        if self.user_exists(data["email"], data["regNo"]):
            if self.student_exists(data["regNo"]):
                messages.error(self.request, "Student already exists")
                return self.form_invalid(form)
            else:
                user = User.objects.get(email=data["email"])
                self.create_student(user, data)
                messages.success(self.request, "Student created successfully")
                return super().form_valid(form)
        else:
            try:
                user = self.create_user(
                    data["email"], data["firstname"], data["lastname"], data["regNo"]
                )
                self.create_student(user, data)
                messages.success(self.request, "Student created successfully")
                return super().form_valid(form)
            except Exception as e:
                messages.error(self.request, e)
                print(e)
                return HttpResponseRedirect(self.request.META.get("HTTP_REFERER"))

    def form_invalid(self, form):
        for field, errors in form.errors.items():
            for error in errors:
                messages.error(self.request, f"{field}: {error}")
        return super().form_invalid(form)

    def get_success_url(self):
        return reverse("student")

    def user_exists(self, email, regNo):
        return (
            User.objects.filter(username=email).exists()
            or Student.objects.filter(regNo=regNo).exists()
        )

    def student_exists(self, regNo):
        return Student.objects.filter(regNo=regNo).exists()

    def create_user(self, email, firstname, lastname, regNo):
        password = make_password(regNo)
        user = User.objects.create(
            username=lastname,
            email=email,
            first_name=firstname,
            last_name=lastname,
            password=password,
        )
        # student_group, _ = Group.objects.get_or_create(name="Student")
        # user.groups.add(student_group)
        return user

    def create_student(self, user, data):
        department = data.get("department")
        department = Department.objects.filter(name=department).first()
        Student.objects.create(
            user=user,
            regNo=data["regNo"],
            mobile=data["mobile"],
            academic_year=data["academic_year"],
            program=data["program"],
            # course=data["course"],
            # department=department,
            gender=data["gender"],
        )


class CompletedProjectView(LoginRequiredView, TemplateView):
    template_name = "html/dist/completedprojects.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        try:
            if self.request.user.is_superuser or hasattr(self.request.user, 'staff') and self.request.user.staff == 2:
                cover = ProjectDocument.objects.filter(cover__isnull=False).exclude(cover='').first()
            elif hasattr(self.request.user, 'staff') and self.request.user.staff == 1:
                cover = (
                    ProjectDocument.objects.filter(
                        cover__isnull=False,
                        project__department_id=self.request.user.staff.department.id,
                    )
                    .exclude(cover="")
                    .first()
                )
            else:
                cover = ProjectDocument.objects.filter(cover__isnull=False).exclude(cover='').first()

            # Retrieve final documents and proposal documents
            final_documents = ProjectDocument.objects.filter(document_type="Final")
            proposal_documents = ProjectDocument.objects.filter(
                project__in=final_documents.values_list('project', flat=True),
                document_type="Proposal"
            )

            
            # for doc in final_documents:
            #     for prop in proposal_documents:
            #         if prop.project.title == doc.project.title:
            #             print(doc.id, prop.id)

            # Populate context with required data
            context["cover"] = cover.cover.url if cover else None
            context["d"] = final_documents
            context["proposal_documents"] = proposal_documents
            context["l"] = ProjectDocument.objects.all().count()
            context["f"] = Department.objects.all()
            context["s"] = list(Student.objects.values_list("academic_year", flat=True).distinct())
            context["g"] = ProjectType.objects.all()
            context["level"] = Level.objects.all()
            name = self.request.POST.get("department")
            context["g"] = ProjectType.objects.filter(department__name=name)
            context["side"] = "projects"
            return context
        except Exception as e:
            print(e)
            messages.error(self.request, e)

    def post(self, request, *args, **kwargs):
        try:
            if request.method == "POST":
                student_reg = request.POST.get("student")
                project_id = request.POST.get("project")
                student = get_object_or_404(Student, regNo=student_reg)
                project = get_object_or_404(Project, pk=project_id)
                description = request.POST.get("description")
                student_request = StudentRequest.objects.create(
                    student=student, project=project, description=description
                )
                student_request.save()
                messages.success(request, "Request sent successfully")
                return HttpResponseRedirect(request.META.get("HTTP_REFERER"))
        except Exception as e:
            print(e)
            messages.error(request, "Something went wrong")
            return HttpResponseRedirect(request.META.get("HTTP_REFERER"))


class ManageProjectView(LoginRequiredView, ListView):
    template_name = "html/dist/manage_project.html"
    context_object_name = "d"
    login_url = "/login/"

    def get_queryset(self):
        try:
            if self.request.user.is_superuser:
                # Return only project and not project documents under that project
                return Project.objects.all()
            elif hasattr(self.request.user, 'staff') and self.request.user.staff:
                return Project.objects.filter(
                    department_id=self.request.user.staff.department.id
                )
            elif hasattr(self.request.user, 'student') and self.request.user.student:
                return Project.objects.filter(
                    student_id=self.request.user.student.id
                )
            else:
                # Handle the case where the user is neither staff nor student
                messages.error(self.request, "User has no associated staff or student record.")
                return Project.objects.none()  # or some appropriate empty queryset
        except ObjectDoesNotExist as e:
            messages.error(self.request, f"Related object does not exist: {e}")
            return HttpResponseRedirect(self.request.META.get("HTTP_REFERER"))
        except Exception as e:
            messages.error(self.request, str(e))
            return HttpResponseRedirect(self.request.META.get("HTTP_REFERER"))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # return cover of project document with cover
        # Check if the user is staff
        if hasattr(self.request.user, 'staff') and self.request.user.staff:
            pass
        else:
            try:
                cover = ProjectDocument.objects.filter(
                    cover__isnull=False,
                    project__student_id=self.request.user.student.id,
                )
                # print the url of the cover
                print(cover[0].cover.url)
                context["cover"] = cover[0].cover.url

            except Exception as e:
                print(e)
                pass

        # give total number of upvotes per each project
        all_upvotes = []
        projects = Project.objects.all()
        for project in projects:
            upvotes = Upvote.objects.filter(project=project).count()
            dictionary = {"title": project.title, "upvotes": upvotes}
            all_upvotes.append(dictionary)

        context["upvotes"] = all_upvotes
        context["f"] = Department.objects.all()

        context["document_types"] = ProjectDocument.DOCUMENT_TYPE
        context["s"] = list(
            Student.objects.values_list("academic_year", flat=True).distinct()
        )
        name = self.request.POST.get("department")
        context["g"] = ProjectType.objects.filter(department__name=name)
        context["side"] = "manage_project"
        if hasattr(self.request.user, 'student') and self.request.user.student:
            context["documents"] = ProjectDocument.objects.filter(
                project__student=self.request.user.student
            )
            context["project_types"] = ProjectType.objects.filter(department=self.request.user.student.program.department)
            uploaded_project = UploadedProject.objects.filter(student_id=self.request.user.student.id).first()

            if uploaded_project:
                context["project_file_id"] = uploaded_project.id
            else:
                context["project_file_id"] = None 
        
        return context

    # function to add new project document
    def post(self, request, *args, **kwargs):
        if request.POST.get("_type") == "project":
            # create new projet
            student = Student.objects.get(user=request.user)
            title = request.POST.get("title")
            note = request.POST.get("note")
            department = request.POST.get("department")
            project_type = request.POST.get("project_type")

            try:
                project = Project.objects.create(
                    title=title, student=student, note=note, department_id=department, project_type_id=project_type
                )
                project.save()
                messages.success(request, "Project added successfully")
                return HttpResponseRedirect(request.META.get("HTTP_REFERER"))
            except Exception as e:
                print(e)
                messages.error(request, e)
                return HttpResponseRedirect(request.META.get("HTTP_REFERER"))

        if request.POST.get("_type") == "document":
            try:
                # project_id = request.POST.get("project")
                project_id = Project.objects.filter(student__user=request.user).last().id
                project = get_object_or_404(Project, pk=project_id)
                document_type = request.POST.get("document_type")
                file = request.FILES.get("file")
                cover = request.FILES.get("cover")
                project_document = ProjectDocument.objects.create(
                    project=project, file=file, document_type=document_type, cover=cover
                )
                project_document.save()
                messages.success(request, "Document added successfully")
                return HttpResponseRedirect(request.META.get("HTTP_REFERER"))
            except Exception as e:
                print(e)
                messages.error(request, e)
                return HttpResponseRedirect(request.META.get("HTTP_REFERER"))   
            
        if request.POST.get("_method") == "PUT":
            document_id = request.POST.get("document_id")
            
            try:
                document = ProjectDocument.objects.get(pk=document_id)
                document_type = request.POST.get("document_type")
                file = request.FILES.get("file")
                cover = request.FILES.get("cover")
                document.document_type = document_type
                if file:
                    document.file = file
                if cover:
                    document.cover = cover
                document.save()
                messages.success(request, "Document updated successfully")
                return HttpResponseRedirect(request.META.get("HTTP_REFERER"))
            except Exception as e:
                print(e)
                messages.error(request, e)
                return HttpResponseRedirect(request.META.get("HTTP_REFERER"))


class ProjectListView(LoginRequiredView, ListView):
    template_name = "html/dist/project_list.html"
    context_object_name = "projects"
    login_url = "/login/"

    # return all projects with a specific project type
    def get_queryset(self):
        project_type = self.kwargs.get("project_type")
        return ProjectDocument.objects.filter(project__project_type_id=project_type)

    # return the project type name
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        project_type = ProjectType.objects.get(pk=self.kwargs.get("project_type"))
        context["project_type"] = project_type
        return context


class EditStudentView(LoginRequiredMixin, FormView):
    template_name = "html/dist/students.html"
    form_class = StudentForm
    success_url = reverse_lazy("student")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["u"] = Group.objects.all()

        try:
            context["d"] = Student.objects.filter(user=self.request.user)
            context["p"] = Student.objects.get(user=self.request.user)

        except Student.DoesNotExist:
            context["d"] = None
            context["p"] = None

        context["t"] = Permission.objects.all()
        return context

    def form_valid(self, form):
        try:
            pk = self.kwargs.get("pk")
            user = User.objects.get(pk=pk)
            student = Student.objects.get(user=user)

            # Update student information
            student.regNo = form.cleaned_data["regno"]
            student.mobile = form.cleaned_data["mobile"]
            student.academic_year = form.cleaned_data["academic_year"]
            student.level = form.cleaned_data["level"]
            student.course = form.cleaned_data["course"]
            student.department_id = form.cleaned_data["department"]
            student.gender = form.cleaned_data["gender"]
            student.save()

            # Update user groups and permissions
            user.groups.clear()
            user.user_permissions.clear()

            selected_groups = form.cleaned_data.get("groups", [])
            selected_permissions = form.cleaned_data.get("permissions", [])

            user.groups.add(*selected_groups)
            user.user_permissions.add(*selected_permissions)

            messages.success(self.request, "Student updated successfully")
            return super().form_valid(form)

        except Student.DoesNotExist:
            messages.error(self.request, "Student does not exist")
            return super().form_invalid(form)

        except Exception as e:
            messages.error(self.request, f"An error occurred: {e}")
            return super().form_invalid(form)


class StaffView(LoginRequiredMixin, TemplateView):
    template_name = "html/dist/staffs.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        try:
            exclude_perm = [
                1,
                2,
                3,
                4,
                13,
                14,
                15,
                16,
                17,
                18,
                19,
                20,
                21,
                22,
                23,
                24,
                37,
            ]

            context["side"] = "staff"
            context["s"] = Staff.objects.all()
            context["d"] = Department.objects.all()
            context["type_choices"] = Staff.TYPE
            context["g"] = Group.objects.all()
            context["p"] = Permission.objects.exclude(id__in=exclude_perm)
        except:
            messages.error(self.request, "Something went wrong")
            return HttpResponseRedirect(self.request.META.get("HTTP_REFERER"))
        return context


class AddStaffView(LoginRequiredMixin, FormView):
    template_name = "html/dist/staffs.html"
    form_class = StaffForm
    success_url = reverse_lazy("staff")

    def form_valid(self, form):
        data = form.cleaned_data
        if self.user_exists(data["email"]):
            if self.staff_exists(data["staff_id"]):
                messages.error(self.request, "Staff already exists")
                return self.form_invalid(form)
            else:
                user = User.objects.get(email=data["email"])
                self.create_staff(user, data)
                messages.success(self.request, "Staff created successfully")
                return super().form_valid(form)

        else:
            user = self.create_user(
                data["email"], data["firstname"], data["lastname"], data["staff_id"]
            )
            self.create_staff(user, data)
            messages.success(self.request, "Staff created successfully")
            return super().form_valid(form)

    def form_invalid(self, form):
        for field, errors in form.errors.items():
            for error in errors:
                messages.error(self.request, f"{field}: {error}")
        return super().form_invalid(form)

    def user_exists(self, email):
        return User.objects.filter(email=email).exists()

    def staff_exists(self, staff_id):
        return Staff.objects.filter(staff_id=staff_id).exists()

    def create_user(self, email, firstname, lastname, staff_id):
        password = staff_id + "@DIT123"
        password = make_password(password)
        user = User.objects.create(
            username=lastname,
            email=email,
            password=password,
            first_name=firstname,
            last_name=lastname,
            is_staff=True,
        )
        staff_group, _ = Group.objects.get_or_create(name="Staff")
        user.groups.add(staff_group)
        return user

    def create_staff(self, user, data):
        Staff.objects.create(
            user=user,
            staff_id=data["staff_id"],
            mobile=data["mobile"],
            department=data["department"],
            gender=data["gender"],
            type=data["type"],
        )


class ProjectTypeView(LoginRequiredView, TemplateView):
    template_name = "html/dist/project_type.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["d"] = Department.objects.all()
        context["mentors"] = Staff.objects.all()
        context["t"] = ProjectType.objects.all()
        project = ProjectType.objects.all()

        return context


class StudentRequestView(LoginRequiredView, ListView):
    template_name = "html/dist/student_request.html"
    context_object_name = "requests"

    def get_queryset(self):
        if self.request.user.is_superuser:
            return StudentRequest.objects.all()

        if hasattr(self.request.user, "staff") and self.request.user.staff:
            if self.request.user.staff.type == 2:
                if self.request.user.staff.department:
                    department_id = self.request.user.staff.department.id
                    return StudentRequest.objects.filter(project__department_id=department_id, project__project_type__mentor_id=self.request.user.staff.id)
                else:
                    return StudentRequest.objects.none()
            return StudentRequest.objects.filter(
                project__project_type__mentor_id=self.request.user.staff.id
            )

        elif hasattr(self.request.user, "student") and self.request.user.student:
            student = self.request.user.student
            return StudentRequest.objects.filter(student=student)
        else:
            return StudentRequest.objects.none()

    def post(self, request, *args, **kwargs):
        try:
            if (
                request.POST.get("_method") == "DELETE"
            ):  # Check if the request is for deletion
                request_id = request.POST.get("request_id")
                student_request = get_object_or_404(StudentRequest, pk=request_id)
                student_request.delete()
                messages.success(request, "Request deleted successfully")

            else:  # it's for updating status
                request_id = request.POST.get("request_id")
                status = request.POST.get("status")
                student_request = get_object_or_404(StudentRequest, pk=request_id)
                student_request.status = status
                student_request.save()
                if status == "Accepted":
                    messages.success(request, "Request Accepted")
                else:
                    messages.success(request, "Request Rejected")
        except Exception as e:
            messages.error(request, f"An error occurred: {e}")
        return HttpResponseRedirect(request.META.get("HTTP_REFERER"))


class StudentProjectCommentView(LoginRequiredMixin, TemplateView):
    template_name = "html/dist/student_projects.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["documents"] = ProjectDocument.objects.filter(
            project__student_id=self.kwargs.get("pk")
        )
        context["student"] = Student.objects.get(id=self.kwargs.get("pk"))
        context["upvotes"] = Upvote.objects.filter(
            project__student_id=self.kwargs.get("pk")
        ).count()
        context["project_file_id"] = UploadedProject.objects.filter(
            student_id=self.kwargs.get("pk")
        ).first().id
        # print(context["project_file_id"])
        
        context["side"] = "student_projects"
        # if requested user has upvote to project, return yes
        if Upvote.objects.filter(
            supervisor__user=self.request.user, project__student_id=self.kwargs.get("pk")
        ).exists():
            context["upvoted"] = True
        else:
            context["upvoted"] = False
            
        return context

    def post(self, request, *args, **kwargs):
        try:
            document = request.POST.get("document")
            supervisor = request.POST.get("supervisor")
            text = request.POST.get("comment")
            # document = get_object_or_404(ProjectDocument, pk=document_id)
            print(document, text, supervisor)
            comment = Comment.objects.create(
                document_id=document, supervisor_id=supervisor, text=text
            )

            print("Comment added successfully")
            messages.success(request, "Comment added successfully")
        except Exception as e:
            messages.error(request, f"An error occurred: {e}")

        return HttpResponseRedirect(request.META.get("HTTP_REFERER"))


class CommentListView(LoginRequiredMixin, ListView):
    template_name = "html/dist/comments_list.html"
    context_object_name = "comments"

    def get_queryset(self):
        if self.request.user.is_superuser:
            return Comment.objects.all()
        elif hasattr(self.request.user, "staff") and self.request.user.staff:
            return Comment.objects.filter(supervisor__user=self.request.user)
        else:
            return Comment.objects.filter(
                document__project__student__user=self.request.user
            )

    def post(self, request, *args, **kwargs):
        try:
            if request.POST.get("_method") == "DELETE":
                comment_id = request.POST.get("comment_id")
                comment = get_object_or_404(Comment, pk=comment_id)
                comment.delete()
                messages.success(request, "Comment deleted successfully")

            if request.POST.get("_method") == "PUT":
                comment_id = request.POST.get("comment_id")
                text = request.POST.get("text")
                comment = get_object_or_404(Comment, pk=comment_id)
                comment.text = text
                comment.save()
                messages.success(request, "Comment updated successfully")

        except Exception as e:
            messages.error(request, f"An error occurred: {e}")
        return HttpResponseRedirect(request.META.get("HTTP_REFERER"))


class ProgramView(LoginRequiredView, TemplateView):
    template_name = "html/dist/program.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["programs"] = Program.objects.all()
        context["levels"] = Level.objects.all()
        context["departments"] = Department.objects.all()
        context["side"] = "program"
        return context

    def post(self, request, *args, **kwargs):
        if request.user.is_superuser or request.user.staff.type == 2:
            try:
                if request.POST.get("_method") == "DELETE":
                    program_id = request.POST.get("program_id")
                    program = get_object_or_404(Program, pk=program_id)
                    program.delete()
                    messages.success(request, "Program deleted successfully")

                if request.POST.get("_method") == "PUT":
                    program_id = request.POST.get("program_id")
                    name = request.POST.get("name")
                    code = request.POST.get("code")
                    department = request.POST.get("department")
                    level = request.POST.get("level")
                    program = get_object_or_404(Program, pk=program_id)
                    program.name = name
                    program.code = code
                    program.department = Department.objects.get(id=department)
                    program.level = Level.objects.get(id=level)
                    program.save()
                    messages.success(request, "Program updated successfully")

                if request.POST.get("_method") == "POST":
                    name = request.POST.get("name")
                    code = request.POST.get("code")
                    department = request.POST.get("department")
                    level = request.POST.get("level")
                    Program.objects.create(
                        name=name,
                        code=code,
                        department=Department.objects.get(id=department),
                        level=Level.objects.get(id=level),
                    )
                    messages.success(request, "Program added successfully")

            except Exception as e:
                messages.error(request, f"An error occurred: {e}")
            return HttpResponseRedirect(request.META.get("HTTP_REFERER"))


class AcademicYearView(LoginRequiredView, TemplateView):
    template_name = "html/dist/academic_year.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["academic_years"] = AcademicYear.objects.all()
        context["side"] = "academic_year"
        return context

    def post(self, request, *args, **kwargs):
        if request.user.is_superuser or request.user.staff.type == 2:
            try:
                if request.POST.get("_method") == "DELETE":
                    academic_year_id = request.POST.get("academic_year_id")
                    academic_year = get_object_or_404(AcademicYear, pk=academic_year_id)
                    academic_year.delete()
                    messages.success(request, "Academic Year deleted successfully")

                if request.POST.get("_method") == "PUT":
                    academic_year_id = request.POST.get("academic_year_id")
                    academic_year = request.POST.get("academic_year")
                    academic_year_object = get_object_or_404(AcademicYear, pk=academic_year_id)
                    academic_year_object.academic_year = academic_year
                    academic_year_object.save()
                    messages.success(request, "Academic Year updated successfully")

                if request.POST.get("_method") == "POST":
                    academic_year = request.POST.get("academic_year")
                    AcademicYear.objects.create(academic_year=academic_year)
                    messages.success(request, "Academic Year added successfully")

            except Exception as e:
                messages.error(request, f"An error occurred: {e}")
                print(e)
            return HttpResponseRedirect(request.META.get("HTTP_REFERER"))


######################################### END OF CCBV #########################################


@login_required(login_url="/login/")
def department(request):
    try:
        if request.method == "POST":
            name = request.POST["name"]
            Department.objects.create(name=name)
            messages.success(request, "Department Added successful")
            return HttpResponseRedirect(request.META.get("HTTP_REFERER"))
        d = Department.objects.all().order_by("id")
        return render(
            request, "html/dist/departments.html", {"side": "department", "d": d}
        )
    except:
        messages.error(request, "Something Went Wrong")
        return HttpResponseRedirect(request.META.get("HTTP_REFERER"))


@login_required(login_url="/login/")
def deletedepartment(request, pk):
    try:
        Department.objects.filter(id=pk).delete()
        messages.success(request, "deleted successful")
        return HttpResponseRedirect(request.META.get("HTTP_REFERER"))
    except:
        messages.error(request, "something went wrong")
        return HttpResponseRedirect(request.META.get("HTTP_REFERER"))


@login_required(login_url="/login/")
def editdepartment(request, pk):
    try:
        if request.method == "POST":
            name = request.POST.get("name")
            Department.objects.filter(id=pk).update(name=name)
            messages.success(request, "updated successful")
            return HttpResponseRedirect(request.META.get("HTTP_REFERER"))
    except:
        messages.error(request, "something went wrong")
        return HttpResponseRedirect(request.META.get("HTTP_REFERER"))


@login_required(login_url="/login/")
def addprojecttype(request):
    try:

        if request.method == "POST":
            name = request.POST.get("name")
            department = request.POST.get("department")
            mentor = request.POST.get("mentor")
            ProjectType.objects.create(name=name, department_id=department, mentor_id=mentor)
            messages.success(request, "Project Type added successful")
            return HttpResponseRedirect(request.META.get("HTTP_REFERER"))
    except Exception as e:
        print(e)
        messages.error(request, e)
        return HttpResponseRedirect(request.META.get("HTTP_REFERER"))


@login_required(login_url="/login/")
def editprojecttype(request, pk):
    try:
        if request.method == "POST":
            name = request.POST.get("name")
            department = request.POST.get("department")
            mentor = request.POST.get("mentor")
            if request.user.is_superuser or request.user.staff.type ==2:
                ProjectType.objects.filter(id=pk).update(
                    name=name, department_id=department, mentor_id=mentor
                )
                messages.success(request, "Project Type edited successful")
                return HttpResponseRedirect(request.META.get("HTTP_REFERER"))
            else:
                ProjectType.objects.filter(id=pk).update(name=name)
                messages.success(request, "Project Type edited successful")
                return HttpResponseRedirect(request.META.get("HTTP_REFERER"))
    except:
        messages.error(request, "Something went wrong")
        return HttpResponseRedirect(request.META.get("HTTP_REFERER"))


@login_required(login_url="/login/")
def deleteprojecttype(request, pk):
    try:
        ProjectType.objects.filter(id=pk).delete()
        messages.success(request, "Project Type deleted successful")
        return HttpResponseRedirect(request.META.get("HTTP_REFERER"))
    except:
        messages.error(request, "something is wrong")
        return HttpResponseRedirect(request.META.get("HTTP_REFERER"))


@login_required(login_url="/login/")
def level(request):
    levels = Level.objects.all().order_by("id")
    return render(request, "html/dist/level.html", {"side": "level", "level": levels})


@login_required(login_url="/login/")
def deletelevel(request, pk):
    try:
        Level.objects.filter(id=pk).delete()
        messages.success(request, "deleted successful")
        return HttpResponseRedirect(request.META.get("HTTP_REFERER"))
    except Exception as e:
        messages.error(request, e)
        return HttpResponseRedirect(request.META.get("HTTP_REFERER"))


@login_required(login_url="/login/")
def editlevel(request, pk):
    try:
        if request.method == "POST":
            name = request.POST.get("name")
            Level.objects.filter(id=pk).update(name=name)
            messages.success(request, "updated successful")
            return HttpResponseRedirect(request.META.get("HTTP_REFERER"))
    except:
        messages.error(request, "something went wrong")
        return HttpResponseRedirect(request.META.get("HTTP_REFERER"))


@login_required(login_url="/login/")
def addlevel(request):
    try:
        if request.method == "POST":
            name = request.POST.get("name")
            Level.objects.create(name=name)
            messages.success(request, "level created successful")
            return HttpResponseRedirect(request.META.get("HTTP_REFERER"))
    except Exception as e:
        print(e)
        messages.error(request, e)
        return HttpResponseRedirect(request.META.get("HTTP_REFERER"))


@login_required(login_url="/login/")
def deletestudent(request, pk):
    User.objects.filter(id=pk).delete()
    messages.success(request, "User deleted successful")
    return HttpResponseRedirect(request.META.get("HTTP_REFERER"))


@login_required(login_url="/login/")
def update_level(request, pk):
    try:
        if request.method == "POST":
            name = request.POST.get("name")
            Level.objects.filter(id=pk).update(name=name)
            messages.success(request, "updated successful")
            return redirect("/level")
    except:
        messages.error(request, "something went wrong")


@login_required(login_url="login/")
def manageroles(request):
    try:
        g = Group.objects.all().order_by("id")
        exclude_perm = [1, 2, 3, 4, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24]
        p = Permission.objects.exclude(id__in=exclude_perm)

        return render(
            request, "html/dist/manageroles.html", {"side": "role", "p": p, "g": g}
        )
    except:
        messages.error(request, "Something went wrong")
        return HttpResponseRedirect(request.META.get("HTTP_REFERER"))


@login_required(login_url="login/")
def addroles(request):
    try:
        p = Group()
        if request.method == "POST":
            name = request.POST.get("name")
            permission = [x.name for x in Permission.objects.all()]
            s_id = []
            p.name = name
            for x in permission:
                (
                    s_id.append(int(request.POST.get(x)))
                    if request.POST.get(x)
                    else print("")
                )
            p.save()
            for s in s_id:
                p.permissions.add(Permission.objects.get(id=s))
            messages.success(request, "Role added successful")
            return redirect("manageroles")
    except:
        messages.error(request, "Something went wrong")
        return HttpResponseRedirect(request.META.get("HTTP_REFERER"))


@login_required(login_url="/login/")
def editroles(request, pk):

    try:
        exclude_perm = [1, 2, 3, 4, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 37]
        p = Permission.objects.exclude(id__in=exclude_perm)
        r = Group.objects.filter(id=pk)
        y = Group.objects.get(id=pk)
        if request.method == "POST":
            name = request.POST.get("name")

            for j in Permission.objects.all():
                y.permissions.remove(j.id)

            permission = [x.name for x in Permission.objects.all()]

            s_id = []
            Group.objects.filter(id=pk)
            for x in permission:
                (
                    s_id.append(int(request.POST.get(x)))
                    if request.POST.get(x)
                    else print("")
                )
            r = Group.objects.filter(id=pk).update(name=name)

            for s in s_id:
                y.permissions.add(Permission.objects.get(id=s))
            messages.success(request, "Login successful")
            return redirect("manageroles")

        return render(request, "html/dist/editroles.html", {"r": r, "p": p})
    except:
        messages.error(request, "Something is wrong")


@login_required(login_url="/login/")
def deleteroles(request, pk):
    try:
        g = Group.objects.filter(id=pk).delete()
        if g:
            messages.success(request, "Role deleted successful")

        return redirect("manageroles")
    except:
        messages.error(request, "Something went wrong")
        return HttpResponseRedirect(request.META.get("HTTP_REFERER"))


@login_required(login_url="/login/")
def blockuser(request, pk):

    try:
        u = User.objects.filter(id=pk).filter(is_active="True")
        if u:
            User.objects.filter(id=pk).update(is_active="False")
            messages.success(request, "block successful")
            return HttpResponseRedirect(request.META.get("HTTP_REFERER"))
        else:
            User.objects.filter(id=pk).update(is_active="True")
            messages.success(request, "Activation successful")
            return HttpResponseRedirect(request.META.get("HTTP_REFERER"))
    except:
        messages.error(request, "Something went Wrong")
        return HttpResponseRedirect(request.META.get("HTTP_REFERER"))


@login_required(login_url="/login/")
def reset_password(request, pk):
    password = make_password("@DIT123")
    User.objects.filter(id=pk).update(password=password)
    messages.success(request, "Password reseted successful")
    return HttpResponseRedirect(request.META.get("HTTP_REFERER"))


@login_required(login_url="/login/")
def editstaff(request, pk):
    try:
        if request.method == "POST":

            name = request.POST.get("name")
            email = request.POST.get("username")
            staff_id = request.POST.get("staff_id")
            mobile = request.POST.get("mobile")
            level = request.POST.get("level")

            departments = request.POST.get("department")
            gender = request.POST.get("gender")

            group_id = request.POST.get("roles")

            group = Group.objects.get(id=group_id)

            password = make_password("@DIT123")
            users = User.objects.filter(username=email).exists()
            user = Staff.objects.filter(staff_id=staff_id).exists()

            User.objects.filter(id=pk).update(
                username=email, email=email, first_name=name
            )
            Staff.objects.filter(user_id=pk).update(
                staff_id=staff_id,
                mobile=mobile,
                department_id=departments,
                gender=gender,
                level=level,
            )
            u = User.objects.get(id=pk)
            for i in Group.objects.all():
                u.groups.remove(i.id)
            u.groups.add(group)
            messages.success(request, "Staff created successful")
            return HttpResponseRedirect(request.META.get("HTTP_REFERER"))
    except:
        messages.error(request, "Something went wrong")
        return HttpResponseRedirect(request.META.get("HTTP_REFERER"))


@login_required(login_url="/login/")
def download_student_excel(request):
    file_path = os.path.join(
        settings.STATIC_ROOT, "student sample excel.xlsx"
    )
    if os.path.exists(file_path):
        return FileResponse(open(file_path, 'rb'), as_attachment=True, filename='sample_students.xlsx')
    else:
        # Handle the case where the file does not exist
        return HttpResponse(status=404)


@login_required(login_url="/login/")
def upload_student(request):
    if request.method != "POST":
        messages.error(request, "Invalid request method.")
        return HttpResponseRedirect(request.META.get("HTTP_REFERER"))

    file_data = request.FILES.get("file")
    if not file_data or not str(file_data).endswith(".xlsx"):
        messages.error(request, "Please upload an Excel (.xlsx) file.")
        return HttpResponseRedirect(request.META.get("HTTP_REFERER"))

    try:
        df = pd.read_excel(file_data)
    except Exception as e:
        messages.error(
            request, "Error reading the Excel file. Please ensure it's valid."
        )
        print(e)
        return HttpResponseRedirect(request.META.get("HTTP_REFERER"))

    for _, row in df.iterrows():
        try:
            program = Program.objects.get(name=row["Program"])
        except Exception as e:
            messages.error(request, f"Program '{row['Program']}' does not exist.")
            print(e)
            return HttpResponseRedirect(request.META.get("HTTP_REFERER"))
        try:
            academic_year = AcademicYear.objects.get(academic_year=row["Academic Year"])
        except Exception as e:
            messages.error(request, f"Academic Year '{row['Academic Year']}' does not exist.")
            print(e)
            return HttpResponseRedirect(request.META.get("HTTP_REFERER"))

        if Student.objects.filter(regNo=row["Registration Number"]).exists():
            messages.error(
                request,
                f"Student with Registration Number '{row['Registration Number']}' already exists.",
            )
            return HttpResponseRedirect(request.META.get("HTTP_REFERER"))

        if User.objects.filter(username=row["Last Name"]).exists():
            messages.error(
                request, f"User with username '{row['Last Name']}' already exists."
            )
            return HttpResponseRedirect(request.META.get("HTTP_REFERER"))

        try:
            user = User.objects.create(
                first_name=row["First Name"],
                last_name=row["Last Name"],
                email=row["Email"],
                username=row["Last Name"],
                password=make_password(str(row["Registration Number"])),
            )

            Student.objects.create(
                user=user,
                gender=row["Gender"],
                regNo=row["Registration Number"],
                mobile=row["Mobile"],
                program=program,
                academic_year=academic_year,
            )
            messages.success(request, "Student created successfully.")
        except Exception as e:
            messages.error(request, f"Error creating student for {row['Last Name']}.")
            print(e)
            return HttpResponseRedirect(request.META.get("HTTP_REFERER"))

    return HttpResponseRedirect(request.META.get("HTTP_REFERER"))


@login_required(login_url="/login/")
def download_staff_excel(request):
    file_path = os.path.join(settings.STATIC_ROOT, "staff sample excel.xlsx")
    if os.path.exists(file_path):
        return FileResponse(
            open(file_path, "rb"), as_attachment=True, filename="sample_staff.xlsx"
        )
    else:
        # Handle the case where the file does not exist
        return HttpResponse(status=404)


@login_required(login_url="/login/")
def upload_staff(request):
    if request.method != "POST":
        messages.error(request, "Invalid request method.")
        return HttpResponseRedirect(request.META.get("HTTP_REFERER"))

    file_data = request.FILES.get("file")
    if not file_data or not str(file_data).endswith(".xlsx"):
        messages.error(request, "Please upload an Excel (.xlsx) file.")
        return HttpResponseRedirect(request.META.get("HTTP_REFERER"))

    try:
        df = pd.read_excel(file_data)
    except Exception as e:
        messages.error(
            request, "Error reading the Excel file. Please ensure it's valid."
        )
        print(e)
        return HttpResponseRedirect(request.META.get("HTTP_REFERER"))

    for _, row in df.iterrows():
        try:
            department = Department.objects.get(name=row["Department"])
        except Exception as e:
            messages.error(request, f"Department '{row['Department']}' does not exist.")
            print(e)
            return HttpResponseRedirect(request.META.get("HTTP_REFERER"))

        valid_type_names = [t[1] for t in Staff.TYPE]
        staff_type = row["Staff Type"]
        if staff_type not in valid_type_names:
            messages.error(request, f"Invalid staff type '{staff_type}'.")
            return HttpResponseRedirect(request.META.get("HTTP_REFERER"))
        else:
            staff_type = [t[0] for t in Staff.TYPE if t[1] == staff_type][0]

        if Staff.objects.filter(staff_id=row["Staff ID"]).exists():
            messages.error(
                request,
                f"Staff with ID '{row['Staff ID']}' already exists.",
            )
            return HttpResponseRedirect(request.META.get("HTTP_REFERER"))

        if User.objects.filter(username=row["Last Name"]).exists():
            messages.error(
                request, f"User with username '{row['Last Name']}' already exists."
            )
            return HttpResponseRedirect(request.META.get("HTTP_REFERER"))

        try:
            user = User.objects.create(
                first_name=row["First Name"],
                last_name=row["Last Name"],
                email=row["Email"],
                username=row["Last Name"],
                password=make_password(str(row["Staff ID"] + "@DIT123")),
            )

            Staff.objects.create(
                user=user,
                gender=row["Gender"],
                staff_id=row["Staff ID"],
                type=staff_type,
                mobile=row["Mobile"],
                department=department,
            )
            messages.success(request, "Staff created successfully.")
        except Exception as e:
            messages.error(request, f"Error creating staff for {row['Last Name']}.")
            print(e)
            return HttpResponseRedirect(request.META.get("HTTP_REFERER"))

    return HttpResponseRedirect(request.META.get("HTTP_REFERER"))

@login_required(login_url="/login/")
def upload_project(request):
    if request.method == "POST":
        file = request.FILES.get("file")
        if not file:
            messages.error(request, "No file uploaded.")
            return redirect("upload_file")

        # Save the uploaded file
        student = Student.objects.get(user=request.user)
        uploaded_file = UploadedProject(student=student, project=file)
        uploaded_file.save()

        messages.success(request, "Project uploaded successfully.")
        return HttpResponseRedirect(request.META.get("HTTP_REFERER"))

@login_required(login_url="/login/")
def download_project(request, file_id):
    uploaded_file = get_object_or_404(UploadedProject, id=file_id)

    # Check if the user is allowed to download the file (e.g., staff or related to the file)
    is_staff = False
    if hasattr(request.user, "staff"):
        is_staff = request.user.staff.type == 2

    # Allow the uploader or staff with appropriate role
    if is_staff or request.user.student == uploaded_file.student:
        return FileResponse(open(uploaded_file.project.path, "rb"), as_attachment=True)
    else:
        messages.error(request, "You are not authorized to download this file.")
        return HttpResponseRedirect(request.META.get("HTTP_REFERER"))


def upload(request):
    try:
        if request.method == "POST":

            image = request.FILES.get("file")
            ProjectDocument.objects.create(project_id=1, file=image)
        s = Student.objects.all().count()
        d = Department.objects.all().count()
        p = Project.objects.all().count()
        f = Staff.objects.all().count()
        finalB = Progress.objects.all()
        finalD = Student.objects.filter(level=6)
        return render(
            request,
            "html/dist/project.html",
            {
                "side": "dashboard",
                "s": s,
                "d": d,
                "f": f,
                "p": p,
                "b": finalB,
                "o": finalD,
            },
        )
    except:
        messages.error(request, "Something went wrong")
        return HttpResponseRedirect(request.META.get("HTTP_REFERER"))


def check_file_similarity(file_path):

    similarity_scores = []

    # extract text content from PDF files
    if file_path.endswith(".pdf"):
        with open(file_path, "rb") as f:
            pdf_reader = PyPDF2.PdfReader(f)
            file_content = ""
            for page in pdf_reader.pages:
                file_content += page.extract_text()

    # extract text content from Word files
    # other file types not supported
    else:
        raise ValueError("Unsupported file type")

    for obj in ProjectDocument.objects.all():
        # extract text content from object file
        if obj.file.path.endswith(".pdf"):
            with open(obj.file.path, "rb") as f:
                pdf_reader = PyPDF2.PdfReader(f)
                obj_content = ""
                for page in pdf_reader.pages:
                    obj_content += page.extract_text()
        else:
            continue
        name = (obj.file.name)[9:]

        # calculate similarity score
        similarity_score = fuzz.token_set_ratio(obj_content, file_content)
        similarity_scores.append((name, similarity_score))

    return similarity_scores


t = "SPECIFIC OBJECTIVES"
k = "OBJECTIVES"
u = "SPECIFIC OBJECTIVE"
c = "content"
y = "table of content"
ab = "ABSTRACT"
t = "TITLE"
g = "DAR ES SALAAM"
d = "DAR ES SALAAM INSTITUTE OF TECHNOLOGY"
objectives = [ab, t, k]

dsm = [g]
pattern = "|".join(objectives)
ds = "|".join(dsm)


def split_merge(input, output):
    pages = [0]
    pdf2 = PyPDF2.PdfReader(input)
    pdf_w = PyPDF2.PdfWriter()

    for i in range(1, len(pdf2.pages)):
        text = pdf2.pages[i].extract_text()
        text.lower()

        if "".join(str(y.lower()).split()) in "".join(str(text.lower()).split()):
            pass
        else:
            matches = re.findall(pattern, text)
        if matches:
            pages.append(i)

            if len(pages) == 3:
                break

    for page in pages:
        page = pdf2.pages[page]
        pdf_w.add_page(page)

    with open(output, "wb") as output_file:
        pdf_w.write(output_file)

    return pages


def pdf_upload(request):

    # try:

    zoom_x = 2.0  # horizontal zoom
    zoom_y = 2.0  # vertical zoom
    mat = fitz.Matrix(zoom_x, zoom_y)
    if request.method == "POST" and request.FILES["pdf"]:
        j = ProjectDocument.objects.filter(
            project__student_id=request.user.student.id
        ).exists()
        role = Group.objects.get(name="Student")
        title = request.POST.get("title")
        type = request.POST.get("type")
        file = request.FILES.get("pdf").read()
        f = request.FILES.get("pdf")
        name = str(request.user.student.regNo)
        print(name)
        pdf = request.FILES["pdf"]
        tit = [title]
        n = [name]
        print(n)
        if len(title) >= 3:
            path = f"media/projects/{str(request.user.student.regNo)}.pdf"
            patt = f"projects/{str(request.user.student.regNo)}.pdf"

            if str(f).endswith(".pdf"):
                with open(path, "wb+") as destination:
                    destination.write(file)
                pdf2 = PyPDF2.PdfReader(path)
                text2 = ""

                text2 += pdf2.pages[0].extract_text()
                dar = pdf2.pages[0].extract_text()
                patts = "|".join(tit)
                m = "|".join(n)
                match = re.findall(ds, dar, re.IGNORECASE)

                if match:
                    matches = re.findall(patts, dar, re.IGNORECASE)
                    matc = re.findall(m, dar)
                    if name[-6:] in dar:
                        if "".join(str(title).upper().split()) in "".join(
                            str(dar).upper().split()
                        ):
                            project = Project()
                            similarity_scores = check_file_similarity(path)
                            if len(similarity_scores) == 0:

                                name = str(pdf)[-6:-4]
                                pdfs = str(pdf)[:-4]
                                doc = fitz.open(path)  # open document

                                names = f"{request.user.student.regNo}.jpg"
                                paths = f"media/coverpage/{str(request.user.student.regNo)}.jpg"
                                pic = f"coverpage/{str(request.user.student.regNo)}.jpg"

                                project.title = title.title()
                                project.student_id = request.user.student.id
                                project.department_id = (
                                    request.user.student.department.id
                                )
                                project.project_type_id = type
                                project.save()
                                p = User.objects.get(id=request.user.id)
                                for i in Group.objects.all():
                                    p.groups.remove(i.id)
                                p.groups.add(role)
                                pix = doc[0].get_pixmap(
                                    matrix=mat
                                )  # render page to an image
                                pix.save(paths)
                                profile = os.path.join(
                                    PROJECT_DIR, "..", "media", "projects"
                                )
                                input = path
                                output = f"media/preview/{str(request.user.student.regNo)}.pdf"
                                out = f"preview/{str(request.user.student.regNo)}.pdf"
                                # print(output)

                                # print(pagez)
                                split_merge(input, output)

                                pdf_file = ProjectDocument(
                                    cover=pic,
                                    file=patt,
                                    project_id=project.id,
                                    preview=out,
                                    submitted=True,
                                )
                                pdf_file.save()

                                Progress.objects.create(document_id=pdf_file.id)
                                messages.success(
                                    request, "Your PDF was uploaded successfully!"
                                )
                                # os.remove(path)
                                return HttpResponseRedirect(
                                    request.META.get("HTTP_REFERER")
                                )
                                # return render(request, 'html/dist/pdf_upload.html', {'pdf_file': pdf_file,'j':j})
                            else:

                                if max(similarity_scores, key=lambda x: x[1])[1] > 80:
                                    print(
                                        f"projects/{max(similarity_scores,key=lambda x:x[1])[0]}"
                                    )
                                    d = ProjectDocument.objects.get(
                                        file=f"projects/{max(similarity_scores,key=lambda x:x[1])[0]}"
                                    )

                                    messages.error(
                                        request,
                                        f"Your file is {max(similarity_scores,key=lambda x:x[1])[1]} %  resemble with project with title {d.project.title.title()} of year {d.project.student.academic_year} {d.project.student.level.name.title()} from {d.project.student.department.name.title()} Department",
                                    )

                                    return HttpResponseRedirect(
                                        request.META.get("HTTP_REFERER")
                                    )

                                else:
                                    name = str(pdf)[-6:-4]
                                    name = f"{request.user.student.regNo}.jpg"
                                    doc = fitz.open(path)

                                    paths = f"media/coverpage/{str(request.user.student.regNo)}.jpg"
                                    pic = f"coverpage/{str(request.user.student.regNo)}.jpg"
                                    "media/coverpage/{str(request.user.student.regNo)}.jpg"
                                    project.title = title.title()
                                    project.student_id = request.user.student.id
                                    project.department_id = (
                                        request.user.student.department.id
                                    )
                                    project.project_type_id = type
                                    project.save()
                                    p = User.objects.get(id=request.user.id)
                                    for i in Group.objects.all():
                                        p.groups.remove(i.id)
                                    p.groups.add(role)

                                    pix = doc[0].get_pixmap(
                                        matrix=mat
                                    )  # render page to an image
                                    pix.save(paths)
                                    profile = os.path.join(
                                        PROJECT_DIR, "..", "media", "projects"
                                    )

                                    input = path
                                    output = f"media/preview/{str(request.user.student.regNo)}.pdf"
                                    out = (
                                        f"preview/{str(request.user.student.regNo)}.pdf"
                                    )

                                    split_merge(input, output)

                                    pdf_file = ProjectDocument(
                                        cover=pic,
                                        file=patt,
                                        project_id=project.id,
                                        preview=out,
                                        submitted=True,
                                    )
                                    pdf_file.save()

                                    Progress.objects.create(document_id=pdf_file.id)

                                    messages.success(
                                        request, "Your PDF was uploaded successfully!"
                                    )
                                    return HttpResponseRedirect(
                                        request.META.get("HTTP_REFERER")
                                    )

                        else:
                            messages.error(
                                request, "Title doesnt match with one on pdf"
                            )
                            return HttpResponseRedirect(
                                request.META.get("HTTP_REFERER")
                            )  # return render(request, 'html/dist/pdf_upload.html', {'pdf_file': pdf_file,'j':j})

                    else:
                        messages.error(
                            request,
                            "The document doesnt contain your name! upload your book",
                        )
                        return HttpResponseRedirect(request.META.get("HTTP_REFERER"))
                else:
                    messages.error(request, "Upload your document with cover page")
                    return HttpResponseRedirect(request.META.get("HTTP_REFERER"))
            else:
                messages.error(request, "only Pdf file required")
                return HttpResponseRedirect(request.META.get("HTTP_REFERER"))
        else:
            messages.error(request, "Title name cant be less than 3 words")
            return HttpResponseRedirect(request.META.get("HTTP_REFERER"))

    if request.user.is_superuser:

        p = ProjectType.objects.all()
        sub = Submission.objects.all()

    elif request.user.is_staff:

        p = ProjectType.objects.filter(department_id=request.user.staff.department.id)
        sub = Submission.objects.filter(level=request.user.staff.level.id)
    else:
        sub = Submission.objects.filter(
            level_id=request.user.student.level.id,
            department_id=request.user.student.department.id,
        )

        p = ProjectType.objects.filter(department_id=request.user.student.department.id)
        j = ProjectDocument.objects.filter(
            project__student_id=request.user.student.id
        ).exists()

    role = Group.objects.get(name="Student")
    return render(
        request,
        "html/dist/pdf_upload.html",
        {"side": "upload_project", "p": p, "sub": sub},
    )


def submissionTime(request):
    try:

        role8 = Group.objects.get(name="Final_Year")
        role = Group.objects.get(name="Student")
        if request.method == "POST":
            date = request.POST.get("date")
            time = request.POST.get("time")
            y, m, d = date.split("-")
            h, mm = time.split(":")
            date = datetime.datetime(int(y), int(m), int(d), int(h), int(mm))

            dates = datetime.datetime.now().year
            first = str(dates - 1)
            dates = str(dates)

            dates = f"{first}/{dates}"

            if request.user.staff.level.id == "":
                messages.error(request, "Data")
                return HttpResponseRedirect(request.META.get("HTTP_REFERER"))
            t = Submission.objects.create(
                when=date,
                level_id=request.user.staff.level.id,
                department_id=request.user.staff.department.id,
                academic_year=dates,
            )
            if t:
                for s in Student.objects.filter(
                    level_id=request.user.staff.level.id,
                    department_id=request.user.staff.department.id,
                ):

                    if (
                        s.level == 8
                        and s.level_id == request.user.staff.level.id
                        and s.academic_year == dates
                    ):
                        for i in Group.objects.all():
                            s.user.groups.remove(i.id)
                        s.user.groups.add(role8)
                    elif (
                        s.level == 6
                        and s.level_id == request.user.staff.level.id
                        and s.academic_year == dates
                    ):
                        for i in Group.objects.all():
                            s.user.groups.remove(i.id)
                        s.user.groups.add(role8)

                messages.success(request, "data saved successful")
                return HttpResponseRedirect(request.META.get("HTTP_REFERER"))
    except:
        messages.error(request, "Something went wrong")
        return HttpResponseRedirect(request.META.get("HTTP_REFERER"))


def editSubmittionTime(request, pk):
    try:
        if request.method == "POST":
            date = request.POST.get("date")

            time = request.POST.get("time")

            y, m, d = date.split("-")
            h, mm = time.split(":")
            role = Group.objects.get(name="Final_Year")

            date = datetime.datetime(int(y), int(m), int(d), int(h), int(mm))

            dates = datetime.datetime.now().year
            first = str(dates - 1)
            dates = str(dates)

            dates = f"{first}/{dates}"

            if date < datetime.datetime.now():
                messages.error(request, "date should be greater than today")
                return HttpResponseRedirect(request.META.get("HTTP_REFERER"))
            else:
                Submission.objects.filter(id=pk).update(when=date)

                for s in Student.objects.filter(
                    level_id=request.user.staff.level.id,
                    department_id=request.user.staff.department.id,
                ):

                    if (
                        s.level == 8
                        and s.level_id == request.user.staff.level.id
                        and s.academic_year == dates
                    ):
                        for i in Group.objects.all():
                            print(i.id)
                            s.user.groups.remove(i.id)
                        s.user.groups.add(role.id)
                    elif (
                        s.level == 6
                        and s.level.id == request.user.staff.level.id
                        and s.academic_year == date
                    ):
                        for i in Group.objects.all():
                            s.user.groups.remove(i.id)
                        s.user.groups.add(role)

                messages.success(request, "data edited successful")
                return HttpResponseRedirect(request.META.get("HTTP_REFERER"))
    except:
        messages.error(request, "Something went wrong")
        return HttpResponseRedirect(request.META.get("HTTP_REFERER"))


def deletesub(request, pk):

    Submission.objects.get(id=pk).delete()
    role = Group.objects.get(name="Student")
    print(request.user.staff.level.id)

    date = datetime.datetime.now().year
    first = str(date - 1)
    date = str(date)

    date = f"{first}/{date}"

    for s in Student.objects.filter(department_id=request.user.staff.department.id):

        if (
            s.level == 8
            and s.level_id == request.user.staff.level.id
            and s.academic_year == date
        ):
            for i in Group.objects.all():
                s.user.groups.remove(i.id)
            s.user.groups.add(role.id)
        elif (
            s.level == 6
            and s.level_id == request.user.staff.level.id
            and s.academic_year == date
        ):
            for i in Group.objects.all():
                s.user.groups.remove(i.id)
            s.user.groups.add(role)

    messages.success(request, "data deleted successful")
    return HttpResponseRedirect(request.META.get("HTTP_REFERER"))


def deadlines(request):
    try:

        role = Group.objects.get(name="Student")

        sb = Submission.objects.get(level_id=request.user.student.level.id)
        d = Submission.objects.get(department_id=request.user.student.department.id)

        date = datetime.datetime.now().year
        first = str(date - 1)
        date = str(date)

        date = f"{first}/{date}"
        for s in Student.objects.all():

            if (
                s.level == 8
                and s.level_id == sb.level_id
                and s.academic_year == date
                and s.department_id == d.department_id
            ):
                for i in Group.objects.all():
                    print(i.id)
                    s.user.groups.remove(i.id)
                s.user.groups.add(role.id)
                messages.error(request, "TIMEOUT")

                return render(request, "html/dist/deadline.html")
            elif (
                s.level == 6
                and s.level.id == sb.level_id
                and s.academic_year == date
                and s.department_id == d.department_id
            ):
                for i in Group.objects.all():
                    s.user.groups.remove(i.id)
                s.user.groups.add(role)
                messages.error(request, "TIMEOUT")

                return render(request, "html/dist/deadline.html")

    except:
        messages.error(request, "something went wrong")
        return HttpResponseRedirect(request.META.get("HTTP_REFERER"))


def my_view(request):

    time_instance = Submission.objects.filter(
        level_id=request.user.staff.level.id
    ).first()

    date = time_instance.date.strftime("%Y-%m-%d")

    time = time_instance.time.strftime("%H:%m")
    y, m, d = date.split("-")
    h, mm = time.split(":")
    datt = datetime.datetime(int(y), int(m), int(d), int(h), int(mm))
    now = datetime.datetime.now()

    return render(request, "html/dist/b.html", {"date": datt, "now": now})


def get_project_types(request, department):
    project_types = ProjectType.objects.filter(department__name=department)
    data = [{"id": p.id, "name": p.name} for p in project_types]
    return JsonResponse({"project_types": data})


def deletepdf(request, pk):
    try:
        Project.objects.get(id=pk).delete()
        messages.success(request, "data deleted successful")
        return HttpResponseRedirect(request.META.get("HTTP_REFERER"))
    except:
        messages.error(request, "something went wrong")
        return HttpResponseRedirect(request.META.get("HTTP_REFERER"))

def delete_document(request, pk):
    try:
        ProjectDocument.objects.get(id=pk).delete()
        messages.success(request, "data deleted successful")
        return HttpResponseRedirect(request.META.get("HTTP_REFERER"))
    except:
        messages.error(request, "something went wrong")
        return HttpResponseRedirect(request.META.get("HTTP_REFERER"))

def progress(request):
    try:
        if request.method == "POST":
            id = request.POST.get("id")

            sad = 0
            sad = request.POST.get("sad")
            if sad is None:
                sad = 0

            data = request.POST.getlist("data")

            sum = 0
            for i in data:
                sum += int(i)
            sum = sum + int(sad)

            Progress.objects.filter(id=id).update(prog=sum, status=True)

            return redirect("/assessment")
        else:
            return redirect("/assessment")
    except:
        messages.error(request, "Something went wrong")
        return HttpResponseRedirect(request.META.get("HTTP_REFERER"))


def autocomplete(request):
    if "q" in request.GET:
        q = request.GET["q"]

        multiple_q = Q(
            Q(document__project__title__icontains=q) | Q(last_name__icontains=q)
        )
        data = Progress.objects.filter(multiple_q)
        titles = list()
        for product in data:
            titles.append(product.title)
        return JsonResponse(titles, safe=False)
    else:
        data = Progress.objects.all()
    context = {"data": data}

    return render(request, "html/dist/completedprojects.html", context)


def get_level(request):
    level = request.GET.get("level")
    department = request.GET.get("dept")
    if department != "":

        districts = Awards.objects.filter(department__name=level).values("id", "name")
    elif level != "":
        districts = Awards.objects.filter(
            department__name=level, level_id=level
        ).values("id", "name")

    return JsonResponse({"districts": list(districts)})


def get_courses(request):
    department = request.GET.get("department")
    department = department.upper()

    level = request.GET.get("level")

    dept = Department.objects.get(name=department)

    if level == "":
        pass
    else:
        lev = Level.objects.get(name=level)
        courses = Awards.objects.filter(department_id=dept.id, level_id=lev.id).values(
            "id", "name"
        )
        typ = ProjectType.objects.filter(department_id=dept.id).values("id", "name")

    courses = list(courses)
    types = list(typ)

    print(types)

    return JsonResponse({"courses": courses, "types": types})
