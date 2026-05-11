from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, AuditLog, UserNotification


@admin.register(UserNotification)
class UserNotificationAdmin(admin.ModelAdmin):
    list_display = ('created_at', 'recipient', 'kind', 'read', 'reservation')
    list_filter = ('kind', 'read')
    search_fields = ('message', 'recipient__username')
    readonly_fields = ('created_at',)


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ('created_at', 'actor', 'action', 'target_model', 'target_id')
    list_filter = ('action', 'target_model')
    search_fields = ('detail', 'target_id')
    readonly_fields = ('created_at', 'actor', 'action', 'target_model', 'target_id', 'detail')

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (
        ('Profil', {'fields': ('phone', 'address', 'note_moyenne',
                               'is_proprietaire', 'identity_verified', 'identity_document', 
                               'identity_document_submitted', 'avatar', 'bio')}),
    )
    list_display = UserAdmin.list_display + ('is_proprietaire', 'identity_verified', 
                                            'identity_document_submitted')
    list_filter = UserAdmin.list_filter + ('is_proprietaire', 'identity_verified', 
                                           'identity_document_submitted')
    actions = ['approve_identity_verification', 'reject_identity_verification']
    
    def approve_identity_verification(self, request, queryset):
        updated = queryset.filter(identity_document_submitted=True).update(identity_verified=True)
        self.message_user(request, f'{updated} utilisateur(s) vérifié(s) avec succès.')
    approve_identity_verification.short_description = 'Approuver la vérification d\'identité'
    
    def reject_identity_verification(self, request, queryset):
        updated = queryset.update(identity_verified=False, identity_document_submitted=False)
        self.message_user(request, f'{updated} utilisateur(s) rejeté(s).')
    reject_identity_verification.short_description = 'Rejeter la vérification d\'identité'
