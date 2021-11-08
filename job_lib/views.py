import logging

from rest_framework import status
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from rest_framework.views import APIView

from job_lib.authentication import IsAuthorizedPubSubRequest
from job_lib.models import Job, RegisteredImage, JobStatusEnum
from job_lib.pubsub import extract_message_from_pubsub_request
from job_lib.serializers import JobSerializer, RegisteredImageSerializer
from job_lib.gce_resources.virtual_machine import VirtualMachineForJob


logger = logging.getLogger("api")  # TODO: Better logger structure


class JobsViewSet(ModelViewSet):
    queryset = Job.objects.all().order_by("-created_time")
    serializer_class = JobSerializer

    def perform_create(self, serializer):
        super(JobsViewSet, self).perform_create(serializer)
        serializer.instance.refresh_from_db()
        VirtualMachineForJob(
            job_id=str(serializer.instance.instance_uuid),
            image_url=serializer.instance.image_id.image_path,
            full_command=serializer.instance.invocation_arguments,
            zone=serializer.instance.zone,
            instance_type=serializer.instance.instance_type,
            disk_size_gb=serializer.instance.disk_size_gb,
            env_vars=serializer.instance.environment,
        ).create_instance()


class RegisteredImagesViewSet(ModelViewSet):
    queryset = RegisteredImage.objects.all().order_by("-created_time")
    serializer_class = RegisteredImageSerializer


class JobStatusChangesView(APIView):
    permission_classes = (IsAuthorizedPubSubRequest,)
    authentication_classes = []

    def post(self, request, *args, **kwargs):
        event_payload = extract_message_from_pubsub_request(request)
        job_id = event_payload.get("job_id")
        try:
            job = Job.objects.get(instance_uuid=job_id)
        except Job.DoesNotExist:
            logger.warning(f"Received status change for unknown Job: {job_id}")
            return Response({"status": "Non-retryable failure"})
        new_status = event_payload["status"]
        job.status = new_status
        if new_status in [JobStatusEnum.FINISHED.value, JobStatusEnum.FAILED.value]:
            logger.info(f"Shutting down VM for job: {job_id}")
            VirtualMachineForJob.delete_instance(job_id)  # TODO: Better error handling

        return Response(status=status.HTTP_200_OK, data={"status": "received"})
