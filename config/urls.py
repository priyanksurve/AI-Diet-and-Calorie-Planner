

from django.contrib import admin
from django.contrib.auth.views import LoginView, LogoutView
from django.urls import path, reverse_lazy
from planner.views import calculator, home, plan, register

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', home, name='home'),
    path('register/', register, name='register'),
    path(
        'login/',
        LoginView.as_view(
            template_name='registration/login.html',
            redirect_authenticated_user=True,
            next_page=reverse_lazy('calculator'),
        ),
        name='login',
    ),
    path('logout/', LogoutView.as_view(next_page=reverse_lazy('home')), name='logout'),
    path('calculator/', calculator, name='calculator'),
    path('plan/', plan, name='plan'),
]