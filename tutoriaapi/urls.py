from django.conf.urls import url

from . import views

urlpatterns = [

    #
    # users.py
    #
    # GET|PUT users/{username}
    url(r'^users/(?P<username>\w+)$', views.users.UserView.as_view()),

    # PUT/DELETE users/{username}/login-session
    url(r'^users/(?P<username>\w+)/login\-session$', views.users.UserLoginSessionView.as_view()),

    # GET|POST users/{username}/events
    url(r'^users/(?P<username>\w+)/events$', views.users.UserEventsView.as_view()),

    # GET users/{username}/wallet/transactions
    url(r'^users/(?P<username>\w+)/wallet/transactions$', views.users.UserWalletTransactionsView.as_view()),

    # PUT users/{username}/wallet
    url(r'^users/(?P<username>\w+)/wallet$', views.users.UserWalletView.as_view()),

    # GET|POST users/{username}/messages
    url(r'^users/(?P<username>\w+)/messages$', views.users.UserMessagesView.as_view()),

    # PUT users/{username}/access-token
    url(r'^users/(?P<username>\w+)/access\-token$', views.users.UserAccessTokenView.as_view()),

    # PUT users/{username}/password
    url(r'^users/(?P<username>\w+)/password$', views.users.UserPasswordView.as_view()),



    # POST users/{username}/tutorials
    # { "preview": true } -> no booking, only preview the charge
    # other book th tutorial
    url(r'^tutorials$', views.tutorials.TutorialSetView.as_view()),

    # GET|DELETE tutorials/{tutorialId}
    url(r'^tutorials/(?P<tutorial_id>\w+)$', views.tutorials.TutorialView.as_view()),

    # PUT tutorials/{tutorialId}/review
    url(r'^tutorials/(?P<tutorial_id>\w+)/review$', views.tutorials.TutorialReviewView.as_view()),

    #
    # tutors.py
    #
    # GET tutors?query-params=...
    url(r'^tutors$', views.tutors.TutorSetSearchView.as_view()),

    # GET|PUT tutors/{username}
    url(r'^tutors\/(?P<tutor_username>\w+)$', views.tutors.TutorView.as_view()),

    # POST tutors/{username}/unavailable-periods
    url(r'^tutors\/(?P<tutor_username>\w+)\/unavailable\-periods$', views.tutors.TutorUnavailablePeriodSetView.as_view()),

    #
    # unavailable_period.py
    #
    # GET unavailable-periods/:period_pk
    url(r'^unavailable\-periods\/(?P<period_pk>\w+)$', views.unavailable_periods.UnavailablePeriodView.as_view()),

    #
    # messages.py
    #
    # GET messages/:message_pk
    url(r'^messages\/(?P<message_pk>\w+)$', views.messages.MessageView.as_view()),

    # PUT students/{username}
    url(r'^students\/(?P<student_username>\w+)$', views.students.StudentView.as_view())
    
]
