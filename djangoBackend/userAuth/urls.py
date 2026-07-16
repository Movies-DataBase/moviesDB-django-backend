from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("check-username/", views.check_username, name="check_username"),
    path("check-email/", views.check_email, name="check_email"),
    path("send-otp/", views.send_otp, name="send_otp"),
    path("signup/", views.signup, name="signup"),
    path("login/", views.login, name="login"),
    path("logout/", views.logout, name="logout"),
    path("profile/", views.get_profile, name="get_profile"),
    path("profile/update/", views.update_profile, name="update_profile"),
    path("change-password/", views.change_password, name="change_password"),
]