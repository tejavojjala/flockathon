from rest_framework import serializers
from travis.models import User

class UserSerializer(serializers.ModelSerializer):
	class Meta:
		model = User
		fields = ('token','userToken','userId')
			