from django.contrib.auth.models import User
from rest_framework import generics, serializers
from django.contrib.auth import authenticate
from rest_framework.authtoken.models import Token
from django.shortcuts import get_object_or_404
from rest_framework import generics, views, response, status, permissions
from .models import Message, UserProfile
from .serializers import MessageSerializer, UserProfileSerializer


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'password')
        extra_kwargs = {'password': {'write_only': True, 'min_length': 8}}

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            password=validated_data['password']
        )
        return user

class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer

class LoginView(views.APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):
        username = request.data.get('username')
        password = request.data.get('password')
        
        user = authenticate(request, username=username, password=password)
        if user is not None:
            token, created = Token.objects.get_or_create(user=user)
            return response.Response({'token': token.key}, status=status.HTTP_200_OK)
        else:
            return response.Response({'error': 'Invalid username or password'}, status=status.HTTP_400_BAD_REQUEST)


class MessageList(generics.ListCreateAPIView):
    queryset = Message.objects.all()
    serializer_class = MessageSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        recipient_username = self.request.query_params.get('recipient', None)
        recipient = get_object_or_404(User, username=recipient_username)
        return self.queryset.filter(recipient=recipient, sender=self.request.user)

    def perform_create(self, serializer):
        recipient_username = self.request.data.get('recipient')
        recipient = get_object_or_404(User, username=recipient_username)
        serializer.save(sender=self.request.user, recipient=recipient)

class ProfileView(views.APIView):
    permission_classes = [permissions.IsAuthenticated]

    def patch(self, request):
        user_profile = request.user.userprofile
        serializer = UserProfileSerializer(user_profile, data=request.data, partial=True)

        if serializer.is_valid():
            serializer.save()
            return response.Response(serializer.data, status=status.HTTP_200_OK)

        return response.Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)