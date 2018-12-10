from django.urls import path, include
from . import views

app_name = 'subscription'

urlpatterns = [
    # path('subscription/', include('subscription.urls')),
    path('weixin/', views.weixin_check, name='weixin_check'),
    path('auth/', views.AuthView.as_view()),
    path('index/', views.GetInfoView.as_view()),
    path('account', views.AccountListView.as_view()),
    path('detail', views.GetAccountDetailView.as_view()),
    path('pay', views.AccountPay.as_view()),
    path('add/', views.account_add, name='account_add'),
    path('update/', views.account_update, name='account_update'),
    path('check', views.account_check, name='account_check'),
]
