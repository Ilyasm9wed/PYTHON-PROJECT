from django.contrib import admin
from .models import Message, Conversation

@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('expediteur', 'conversation', 'date', 'lu')

admin.site.register(Conversation)
