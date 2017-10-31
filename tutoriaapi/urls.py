from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^auth/login$', views.authLogin),
    url(r'^auth/logout$', views.authLogout),

    url(r'^user(?:\/(?P<username>\w+))?/sessions$', views.UserSessionsView.as_view())
]