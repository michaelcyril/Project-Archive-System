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
    path("editstudent/<str:pk>/", EditStudentView.as_view(), name="editstudent"),
    path("upload_student/", views.upload_student, name="upload_student"),
    path("deletestudent/<str:pk>/", views.deletestudent, name="deletestudent"),
    path("addstudent/", AddStudentView.as_view(), name="addstudent"),
    path("staff/", StaffView.as_view(), name="staff"),
    path("addstaff/", AddStaffView.as_view(), name="addstaff"),
    path("editstaff/<str:pk>/", views.editstaff, name="editstaff"),
    path("upload_addstaff/", views.upload_addstaff, name="upload_addstaff"),
    # path("blockuser/<str:pk>/", views.blockuser, name="blockuser"),
    ########################### DEPARTMENT URLS #############################
    path("department/", views.department, name="department"),
    path("edit_department/<str:pk>/", views.editdepartment, name="editdepartment"),
    path(
        "delete_department/<str:pk>/", views.deletedepartment, name="deletedepartment"
    ),
    ############################ PROJECT URLS ############################
    path("project_type/", ProjectTypeView.as_view(), name="project_type"),
    path("add_project_type/", views.addprojecttype, name="addprojecttype"),
    path("edit_project_type/<str:pk>/", views.editprojecttype, name="editprojecttype"),
    path(
        "delete_project_type/<str:pk>/",
        views.deleteprojecttype,
        name="deleteprojecttype",
    ),
    path("delete_pdf/<str:pk>/", views.deletepdf, name="deletepdf"),
    path("completed_projects/", CompletedProjectView.as_view(), name="projects"),
    path(
        "manage_project/<str:user_id>/",
        ManageProjectView.as_view(),
        name="manage_project",
    ),
    path("preview_pdf/<str:pk>/", views.preview_pdf, name="preview_pdf"),
    path(
        "project_list/<str:project_type>/",
        ProjectListView.as_view(),
        name="projectlist",
    ),
    path("student_request/", StudentRequestView.as_view(), name="student_request"),
    path(
        "student_projects/<str:pk>/",
        StudentProjectCommentView.as_view(),
        name="student_projects",
    ),
    path("project_comment/", CommentListView.as_view(), name="project_comment"),
    
    ######################## ROLES URLS ############################
    path("manage_roles/", views.manageroles, name="manageroles"),
    path("add_roles/", views.addroles, name="addroles"),
    path("delete_roles/<str:pk>/", views.deleteroles, name="deleteroles"),
    path("edit_roles/<str:pk>/", views.editroles, name="editroles"),
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
    # path("level/", views.level, name="level"),
    # path("delete_level/<str:pk>/", views.delete_level, name="delete_level"),
    # path("update_level/<str:pk>/", views.update_level, name="update_level"),
    # path("pdf_upload/", views.pdf_upload, name="pdf_upload"),
    # path("addlevel/", views.addlevel, name="addlevel"),
    # path("editlevel/<str:pk>/", views.editlevel, name="editlevel"),
    # path("deletelevel/<str:pk>/", views.deletelevel, name="deletelevel"),
    # path("q/", views.my_view, name="my_view"),
    # path("student_od/", StudentODView.as_view(), name="student_od"),
]
