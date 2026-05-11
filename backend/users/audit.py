import threading

_thread_locals = threading.local()


def set_audit_actor(user):
    _thread_locals.user = user


def clear_audit_actor():
    _thread_locals.user = None


def get_audit_actor():
    return getattr(_thread_locals, 'user', None)


def write_audit(action, target_model, target_id, detail=''):
    """Enregistre une ligne d’audit (utilisé par les signaux)."""
    from .models import AuditLog

    actor = get_audit_actor()
    AuditLog.objects.create(
        actor=actor if actor and actor.is_authenticated else None,
        action=action,
        target_model=target_model,
        target_id=str(target_id),
        detail=(detail or '')[:2000],
    )
