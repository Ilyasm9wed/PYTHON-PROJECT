from .notifications import staff_pending_user_reservations_count
from .models import UserNotification


def nav_notification_counts(request):
    ctx = {
        'staff_pending_user_reservations_count': 0,
        'user_unread_notifications_count': 0,
    }
    u = request.user
    if not u.is_authenticated:
        return ctx
    ctx['user_unread_notifications_count'] = UserNotification.objects.filter(
        recipient=u, read=False
    ).count()
    if u.is_staff or u.is_superuser:
        ctx['staff_pending_user_reservations_count'] = staff_pending_user_reservations_count()
    return ctx
