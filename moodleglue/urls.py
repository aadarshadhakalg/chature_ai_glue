from django.urls import path
from .views import ProcessDiscussionView,DiscussionReactionView

urlpatterns = [
    path('process/', ProcessDiscussionView.as_view()),
    path('react/', DiscussionReactionView.as_view()),
]