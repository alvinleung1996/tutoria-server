from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^auth/login$', views.LoginView.as_view()),
    url(r'^auth/logout$', views.LogoutView.as_view()),

    url(r'^user/events$', views.UserEventsView.as_view()),

    # search tutors
    url(r'^tutors$', views.SearchTutorsView.as_view()),

    # show tutor detail
    url(r'^tutor\/(?P<tutorUsername>\w+)$', views.TutorProfileView.as_view()),

    # Get tutorial fee
    url(r'^tutor\/(?P<tutorUsername>\w+)\/tutorial\-fee$', views.TutorialFeeView.as_view()),

    # Book Tutorial Session
    url(r'^tutor\/(?P<tutorUsername>\w+)\/tutorials$', views.BookTutorialView.as_view()),

    # Cancel Event
    url(r'^event/(?P<eventId>\d+)', views.CancelEventView.as_view())
]