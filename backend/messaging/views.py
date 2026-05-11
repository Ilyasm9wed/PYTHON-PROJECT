from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from django.views.generic import ListView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.urls import reverse_lazy
from .models import Conversation, Message
from properties.models import Property

class InboxView(LoginRequiredMixin, ListView):
    model = Conversation
    template_name = 'messaging/inbox.html'
    context_object_name = 'conversations'
    
    def get_queryset(self):
        return Conversation.objects.filter(
            participants=self.request.user
        ).distinct().select_related('property')

class ConversationView(LoginRequiredMixin, View):
    def get(self, request, pk):
        conversation = get_object_or_404(Conversation, pk=pk)
        
        if request.user not in conversation.participants.all():
            messages.error(request, 'Non autorisé.')
            return redirect('inbox')
        
        # Mark messages as read
        conversation.messages.filter(
            expediteur__ne=request.user
        ).update(lu=True)
        
        return render(request, 'messaging/conversation.html', {
            'conversation': conversation,
            'messages': conversation.messages.all().order_by('date'),
        })
    
    def post(self, request, pk):
        conversation = get_object_or_404(Conversation, pk=pk)
        
        if request.user not in conversation.participants.all():
            messages.error(request, 'Non autorisé.')
            return redirect('inbox')
        
        contenu = request.POST.get('contenu')
        if contenu:
            Message.objects.create(
                conversation=conversation,
                contenu=contenu,
                expediteur=request.user
            )
        
        return redirect('conversation', pk=pk)

class SendMessageView(LoginRequiredMixin, View):
    def get(self, request, property_id):
        property_obj = get_object_or_404(Property, pk=property_id)
        return render(request, 'messaging/send_message.html', {
            'property': property_obj,
        })
    
    def post(self, request, property_id):
        property_obj = get_object_or_404(Property, pk=property_id)
        contenu = request.POST.get('contenu')
        
        if not contenu:
            messages.error(request, 'Le message ne peut pas être vide.')
            return render(request, 'messaging/send_message.html', {
                'property': property_obj,
            })
        
        # Check if conversation already exists
        conversation = Conversation.objects.filter(
            participants=request.user
        ).filter(
            participants=property_obj.proprietaire
        ).filter(
            property=property_obj
        ).first()
        
        if not conversation:
            conversation = Conversation.objects.create(property=property_obj)
            conversation.participants.add(request.user, property_obj.proprietaire)
        
        Message.objects.create(
            conversation=conversation,
            contenu=contenu,
            expediteur=request.user
        )
        
        messages.success(request, 'Message envoyé.')
        return redirect('inbox')
