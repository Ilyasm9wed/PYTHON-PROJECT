from django.contrib import messages
from django.contrib.auth.mixins import UserPassesTestMixin
from django.shortcuts import redirect
from django.urls import reverse_lazy


class StaffRequiredMixin(UserPassesTestMixin):
    """Accès réservé aux comptes staff ou superuser."""

    login_url = reverse_lazy('login')

    def test_func(self):
        u = self.request.user
        return u.is_authenticated and (u.is_staff or u.is_superuser)

    def handle_no_permission(self):
        if self.request.user.is_authenticated:
            messages.error(self.request, 'Accès réservé aux administrateurs.')
            return redirect('home')
        return super().handle_no_permission()
