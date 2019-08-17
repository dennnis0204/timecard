from django.urls import path
from . import views
from timecardapp.views import IndexView, Preferences, PrivacyEnglish, PrivacyPolish, PrivacyRussian

urlpatterns = [
    path('', IndexView.as_view(), name='index'),
    path('<int:year>/<int:month>/', IndexView.as_view(), name='index'),
    path('preferences/', Preferences.as_view(), name='preferences'),
    path('privacy/en', PrivacyEnglish.as_view(), name='privacy'),
    path('privacy/pl', PrivacyPolish.as_view(), name='privacy'),
    path('privacy/ru', PrivacyRussian.as_view(), name='privacy'),
]