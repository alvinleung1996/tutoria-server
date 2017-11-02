from django.conf.urls import url

from . import views

urlpatterns = [

    #
    # users.py
    #
    # HEAD/GET users/{username}
    url(r'^users/(?P<username>\w+)$', views.users.ProfileView.as_view()),

    # PUT/DELETE users/{username}/login-session
    url(r'^users/(?P<username>\w+)/login\-session$', views.users.LoginSessionView.as_view()),

    # GET users/{username}/events
    url(r'^users/(?P<username>\w+)/events$', views.users.EventsView.as_view()),

    # POST users/{username}/tutorials
    # { "preview": true } -> no booking, only preview the charge
    # other book th tutorial
    url(r'^users/(?P<username>\w+)/tutorials$', views.users.TutorialCollectionView.as_view()),

    # DELETE users/{username}/tutorials/{tutorialId}
    url(r'^users/(?P<username>\w+)/tutorials/(?P<tutorial_id>\w+)$', views.users.TutorialView.as_view()),

    #
    # tutors.py
    #
    # GET tutors?query-params=...
    url(r'^tutors$', views.tutors.SearchView.as_view()),

    # GET tutors/{username}
    url(r'^tutors\/(?P<tutor_username>\w+)$', views.tutors.ProfileView.as_view())

]
