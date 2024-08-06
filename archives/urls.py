from . import views
from .views import *
from django.urls import path

urlpatterns = [
    ############################# AUTHENTICATION URLS #############################
    path("", DashboardView.as_view(), name="home"),
    path("login/", LoginView.as_view(), name="login"),
    path("logout/", LogoutView.as_view(), name="logout"),
    path("resetpassword/<str:pk>/", views.reset_password, name="resetpassword"),
    path("changepassword/", ChangePasswordView.as_view(), name="changepassword"),
    ############################# USER URLS #############################
    path("upload/", views.upload, name="upload"),
    path("student/", StudentView.as_view(), name="student"),
    path("edit-student/<str:pk>/", EditStudentView.as_view(), name="editstudent"),
    path("upload-student/", views.upload_student, name="upload_student"),
    path("delete-student/<str:pk>/", views.deletestudent, name="deletestudent"),
    path("add-student/", AddStudentView.as_view(), name="addstudent"),
    path("staff/", StaffView.as_view(), name="staff"),
    path("add-staff/", AddStaffView.as_view(), name="addstaff"),
    path("edit-staff/<str:pk>/", views.editstaff, name="editstaff"),
    path("upload-addstaff/", views.upload_addstaff, name="upload_addstaff"),
    # path("blockuser/<str:pk>/", views.blockuser, name="blockuser"),
    ########################### DEPARTMENT URLS #############################
    path("department/", views.department, name="department"),
    path("edit-department/<str:pk>/", views.editdepartment, name="editdepartment"),
    path(
        "delete_department/<str:pk>/", views.deletedepartment, name="deletedepartment"
    ),
    ############################ PROJECT URLS ############################
    path("project-type/", ProjectTypeView.as_view(), name="project_type"),
    path("add-project-type/", views.addprojecttype, name="addprojecttype"),
    path("edit_project_type/<str:pk>/", views.editprojecttype, name="editprojecttype"),
    path(
        "delete-project-type/<str:pk>/",
        views.deleteprojecttype,
        name="deleteprojecttype",
    ),
    path("delete-pdf/<str:pk>/", views.deletepdf, name="deletepdf"),
    path("delete-document/<str:pk>/", views.delete_document, name="delete_document"),
    path("completed_projects/", CompletedProjectView.as_view(), name="projects"),
    path(
        "manage-project/<str:user_id>/",
        ManageProjectView.as_view(),
        name="manage_project",
    ),
    path("preview-pdf/<str:pk>/", views.preview_pdf, name="preview_pdf"),
    path(
        "project-list/<str:project_type>/",
        ProjectListView.as_view(),
        name="projectlist",
    ),
    path("student-request/", StudentRequestView.as_view(), name="student_request"),
    path(
        "student-projects/<str:pk>/",
        StudentProjectCommentView.as_view(),
        name="student_projects",
    ),
    path("project-comment/", CommentListView.as_view(), name="project_comment"),
    path("program/", ProgramView.as_view(), name="program"),
    path("academic-year/", AcademicYearView.as_view(), name="academic_year"),
    
    ######################## ROLES URLS ############################
    path("manage-roles/", views.manageroles, name="manageroles"),
    path("add-roles/", views.addroles, name="addroles"),
    path("delete-roles/<str:pk>/", views.deleteroles, name="deleteroles"),
    path("edit-roles/<str:pk>/", views.editroles, name="editroles"),
    # path("get_courses/", views.get_courses, name="get_courses"),
    # path("edit_speciality/<str:pk>",views.edit_speciality,name="edit_speciality"),
    # path("delete_speciality/<str:pk>",views.delete_speciality,name="delete_speciality"),
    # path("deadline",views.deadline,name="deadline"),
    # path("deadlines/", views.deadlines, name="deadlines"),
    # path("deletesub/<str:pk>/", views.deletesub, name="deletesub"),
    # path("assessment/", AssessmentView.as_view(), name="assessment"),
    # path("editsubtime/<str:pk>/", views.editSubmittionTime, name="editsubtime"),
    # path("progress/", views.progress, name="progress"),
    # path(
    #     "get_project_types/<str:department>/",
    #     views.get_project_types,
    #     name="get_project_types",
    # ),
    # path("subtime/", views.submissionTime, name="subtime"),
    path("level/", views.level, name="level"),
    path("delete-level/<str:pk>/", views.deletelevel, name="delete_level"),
    path("update-level/<str:pk>/", views.update_level, name="update_level"),
    # path("pdf_upload/", views.pdf_upload, name="pdf_upload"),
    path("add-level/", views.addlevel, name="add_level"),
    path("edit-level/<str:pk>/", views.editlevel, name="edit_level"),
    path("delete-level/<str:pk>/", views.deletelevel, name="delete_level"),
    # path("q/", views.my_view, name="my_view"),
    # path("student_od/", StudentODView.as_view(), name="student_od"),
]