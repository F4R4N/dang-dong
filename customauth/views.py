from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.views import TokenViewBase
from .serializers import UserLoginSerializer


class UserLoginView(TokenViewBase):
    """ log the user in with username password """
    serializer_class = UserLoginSerializer
    permission_classes = (AllowAny, )
