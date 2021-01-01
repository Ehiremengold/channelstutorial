from django.urls import path
from .views import account_view, edit_profile_view, crop_image, follow_user
app_name = "account"


urlpatterns = [
	path('switch_follow/<user_id>/', follow_user, name='follow-user'),
    path('<user_id>/', account_view, name='account-view'),
    path('<user_id>/edit/', edit_profile_view, name='edit'),
    path('<user_id>/edit/cropImage', crop_image, name='crop_image'),
]


