from .audit import clear_audit_actor, set_audit_actor


class AuditActorMiddleware:
    """Associe l’utilisateur courant au thread pour les signaux d’audit."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        user = request.user if request.user.is_authenticated else None
        set_audit_actor(user)
        try:
            return self.get_response(request)
        finally:
            clear_audit_actor()
