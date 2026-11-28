from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers

from .models import WorkflowItem

User = get_user_model()


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, validators=[validate_password])

    class Meta:
        model = User
        fields = ("id", "username", "email", "password")

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)


class WorkflowItemSerializer(serializers.ModelSerializer):
    owner = serializers.ReadOnlyField(source="owner.username")

    TITLE_MIN_LENGTH = 3
    DESCRIPTION_MAX_LENGTH = 500

    class Meta:
        model = WorkflowItem
        fields = ("id", "owner", "title", "description", "status", "created_at", "updated_at")
        read_only_fields = ("id", "owner", "created_at", "updated_at")
        extra_kwargs = {
            "status": {
                "error_messages": {
                    "invalid_choice": f"Status must be one of: {', '.join(WorkflowItem.Status.values)}."
                }
            }
        }

    def validate_title(self, value):
        value = value.strip()
        if len(value) < self.TITLE_MIN_LENGTH:
            raise serializers.ValidationError(
                f"Title must be at least {self.TITLE_MIN_LENGTH} characters long."
            )
        return value

    def validate_description(self, value):
        value = value.strip()
        if len(value) > self.DESCRIPTION_MAX_LENGTH:
            raise serializers.ValidationError(
                f"Description must be {self.DESCRIPTION_MAX_LENGTH} characters or fewer."
            )
        return value