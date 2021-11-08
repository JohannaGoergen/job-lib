from enum import Enum
import uuid

from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from regex_field.fields import RegexField


class JobStatusEnum(Enum):
    PROCESSING = "processing"
    FINISHED = "finished"
    WAITING = "waiting"
    FAILED = "failed"
    ABORTED = "aborted"


class VMInstanceTypeEnum(Enum):
    E2_MICRO = "e2-micro"
    E2_SMALL = "e2-small"
    E2_MEDIUM = "e2-medium"


class VMZoneEnum(Enum):
    EU_WEST_3A = "europe-west3-a"
    EU_WEST_3B = "europe-west3-b"
    EU_WEST_3C = "europe-west3-c"


class RegisteredImage(models.Model):
    name = models.CharField(max_length=200)
    image_path = models.CharField(max_length=200)
    tag = models.CharField(max_length=100, default="latest")
    version = models.PositiveIntegerField(default=1)
    invocation_validation_regex = RegexField(max_length=200, default="")
    created_time = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "registered_image"
        verbose_name = "Registered Image"


class Job(models.Model):

    image_id = models.ForeignKey(RegisteredImage, on_delete=models.PROTECT)

    # Human-readable name for display purposes
    name = models.CharField(max_length=100)

    # UUID to be set used as the instance ID of the VM running the job
    instance_uuid = models.UUIDField(default=uuid.uuid4)

    created_time = models.DateTimeField(auto_now_add=True)
    instance_type = models.CharField(
        choices=((itype.value, itype.name) for itype in VMInstanceTypeEnum), max_length=30
    )
    start_time = models.DateTimeField(blank=True, null=True)
    finish_time = models.DateTimeField(blank=True, null=True)
    disk_size_gb = models.PositiveIntegerField(
        default=10, validators=[MaxValueValidator(100), MinValueValidator(1)]
    )
    zone = models.CharField(choices=((z.value, z.name) for z in VMZoneEnum), max_length=30)
    status = models.CharField(
        choices=((status.value, status.name) for status in JobStatusEnum),
        default=JobStatusEnum.WAITING.value,
        max_length=10,
    )
    results = models.JSONField(default=dict, blank=True)
    invocation_arguments = models.CharField(
        max_length=500, blank=True
    )  # String such as: "python run_script.py --arg=1234"
    environment = models.JSONField(default=dict, blank=True)

    class Meta:
        db_table = "job"
        verbose_name = "Job"
        constraints = [
            models.CheckConstraint(
                name="job_status_valid", check=models.Q(status__in=[s.value for s in JobStatusEnum])
            )
        ]
