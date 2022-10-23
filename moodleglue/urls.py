from django.urls import path
from .views import ProcessDiscussionView

urlpatterns = [
    path('process/', ProcessDiscussionView.as_view()),
]