from django.urls import path
from .views import InboxView, ConversationView, SendMessageView

urlpatterns = [
    path('inbox/', InboxView.as_view(), name='inbox'),
    path('conversation/<int:pk>/', ConversationView.as_view(), name='conversation'),
    path('send/<int:property_id>/', SendMessageView.as_view(), name='send_message'),
]
