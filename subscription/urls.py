from django.urls import path, include
from . import views

app_name = 'subscription'

urlpatterns = [
    # path('subscription/', include('subscription.urls')),
    path('weixin/', views.weixin_check, name='weixin_check'),
    path('auth', views.AuthView.as_view()),
    path('index', views.GetInfoView.as_view()),
]
