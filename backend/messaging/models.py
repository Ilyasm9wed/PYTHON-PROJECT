from django.db import models

class Conversation(models.Model):
    participants = models.ManyToManyField('users.CustomUser',
                                          related_name='conversations')
    property = models.ForeignKey('properties.Property',
                                 on_delete=models.SET_NULL,
                                 null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Conversation #{self.id}"

class Message(models.Model):
    conversation = models.ForeignKey(Conversation,
                                     on_delete=models.CASCADE,
                                     related_name='messages')
    contenu = models.TextField()
    date = models.DateTimeField(auto_now_add=True)
    expediteur = models.ForeignKey('users.CustomUser',
                                   on_delete=models.CASCADE,
                                   related_name='messages_envoyes')
    lu = models.BooleanField(default=False)

    def marquer_lu(self):
        self.lu = True
        self.save()

    def __str__(self):
        return f"Message de {self.expediteur} [{self.date:%d/%m/%Y}]"
