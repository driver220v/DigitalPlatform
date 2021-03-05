from django.conf import settings
from django.conf.urls.static import static
from django.urls import path
from .views import SignUpView, SingInView, LogoutView, StartPointView, UserCabinView

urlpatterns = [
                  path('sign_up/', SignUpView.as_view(), name='SignUpView'),
                  path('sign_in/', SingInView.as_view(), name='SignIpView'),
                  path('logout/', LogoutView.as_view(), name='LogoutView'),
                  path('cabin/', UserCabinView.as_view(), name='UserCabinView'),
                  path('', StartPointView.as_view(), name='HomeView')
              ] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
