from typing import AnyStr

from rest_framework import serializers

from job_lib.models import Job, RegisteredImage


class JobSerializer(serializers.ModelSerializer):

    image_id = serializers.PrimaryKeyRelatedField(
        queryset=RegisteredImage.objects.all(),
    )

    class Meta:
        model = Job
        exclude = []
        read_only_fields = [
            "instance_uuid",
            "created_time",
            "start_time",
            "finish_time",
            "status",
            "results",
        ]

    @staticmethod
    def _validate_invocation_args(invocation_args: AnyStr, registered_image: RegisteredImage):
        if not registered_image.invocation_validation_regex.match(invocation_args):
            raise serializers.ValidationError(
                f"Invalid arguments supplied for image {registered_image.name}. Expected arg structure is: {str(registered_image.invocation_validation_regex)}"
            )

    def validate(self, attrs):
        invocation_args = attrs.get("invocation_arguments", "")
        self._validate_invocation_args(invocation_args, attrs["image_id"])
        return attrs

    def to_representation(self, instance):
        repr = super().to_representation(instance)
        repr["registered_image"] = RegisteredImageSerializer(instance.image_id).data
        return repr


class RegisteredImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = RegisteredImage
        exclude = []
        read_only_fields = ["created_time"]

    def validate_image_path(self, value):
        # TODO: Find a way to check the existence of the artifact using python
        return value
