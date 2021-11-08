import yaml

from io import StringIO
from typing import Dict, Any, AnyStr, Optional
from uuid import uuid4

import frozendict

from django.conf import settings
import googleapiclient.discovery

from job_lib.models import VMInstanceTypeEnum, VMZoneEnum

DEFAULT_INSTANCE_TYPE = VMInstanceTypeEnum.E2_MICRO.value
DEFAULT_INSTANCE_ZONE = VMZoneEnum.EU_WEST_3A.value
SHARED_ENV_VARS = frozendict.frozendict(
    {
        "GCS_WRITER_CREDENTIALS": settings.GCS_WRITER_CREDENTIALS,
        "STATUS_CHANGE_PUBSUB_TOPIC": settings.STATUS_CHANGE_PUBSUB_TOPIC,
    }
)


class VirtualMachineForJob:
    def __init__(
        self,
        job_id: uuid4,
        image_url: AnyStr,
        full_command: AnyStr,
        zone: AnyStr = DEFAULT_INSTANCE_ZONE,
        instance_type: AnyStr = DEFAULT_INSTANCE_TYPE,
        disk_size_gb: int = 10,
        env_vars: Optional[Dict[str, Any]] = None,
        export_logs: bool = True,
    ):
        self.custom_environment_variables = env_vars or {}
        self.job_id = str(job_id)
        self.vm_id = self._build_vm_id_from_job_id(
            self.job_id
        )  # GCE VM names must have alphanumeric first character
        self.image_url = image_url
        self.zone = zone
        self.disk_size_gb = disk_size_gb
        self.instance_type = instance_type
        self.command_executable = [full_command.split()[0]]
        self.export_logs = export_logs
        self.region = self.zone[:-2]
        self.command_args = full_command.split()[1:]
        self.containers_spec = {
            "spec": {
                "containers": [
                    {
                        "name": self.vm_id,
                        "image": self.image_url,
                        "command": self.command_executable,
                        "args": self.command_args,
                        "securityContext": {
                            "privileged": True,
                        },
                        "tty": True,
                        "stdin": True,
                        "env": [
                            {"name": k, "value": v}
                            for k, v in {
                                "JOB_ID": self.job_id,  # So the job can shut itself down via Pub/Sub
                                **self.custom_environment_variables,
                                **SHARED_ENV_VARS,
                            }.items()
                        ],
                        "restartPolicy": "OnFailure",
                    }
                ],
            }
        }
        self.machine_spec = {
            "name": self.vm_id,
            "minCpuPlatform": "Automatic",
            "machineType": f"projects/{settings.GCP_PROJECT_ID}/zones/{self.zone}/machineTypes/{self.instance_type}",
            "labels": {"container-vm": "cos-93-16623-39-6"},
            "networkInterfaces": [
                {
                    "subnetwork": f"projects/{settings.GCP_PROJECT_ID}/regions/{self.region}/subnetworks/default",
                    "accessConfigs": [{"name": "External NAT", "type": "ONE_TO_ONE_NAT"}],
                }
            ],
            "disks": [
                {
                    "boot": True,
                    "type": "PERSISTENT",
                    "mode": "READ_WRITE",
                    "initializeParams": {
                        "sourceImage": "https://www.googleapis.com/compute/v1/projects/cos-cloud/global/images/cos-93-16623-39-6",
                        "diskSizeGb": str(self.disk_size_gb),
                    },
                }
            ],
            "metadata": {
                "items": [
                    {"key": "gce-container-declaration", "value": self._dump_containers_to_yaml()},
                    {
                        "key": "google_logging-enabled",
                        "value": "true" if self.export_logs else "false",
                    },
                ]
            },
            "serviceAccounts": [
                {
                    "email": f"{settings.GCP_PROJECT_NUMBER}-compute@developer.gserviceaccount.com",
                    "scopes": ["https://www.googleapis.com/auth/cloud-platform"],
                }
            ],
        }
        self.compute_client = self.init_compute_client()

    @staticmethod
    def init_compute_client():
        return googleapiclient.discovery.build("compute", version="v1", cache_discovery=False)

    def _dump_containers_to_yaml(self):
        buffer = StringIO()
        yaml.dump(self.containers_spec, buffer, indent=2, default_flow_style=False)
        return buffer.getvalue()

    def create_instance(self):
        dp = (
            self.compute_client.instances()
            .insert(project=settings.GCP_PROJECT_ID, zone=self.zone, body=self.machine_spec)
            .execute()
        )
        return dp

    @classmethod
    def delete_instance(cls, job_uuid: uuid4, zone: AnyStr = DEFAULT_INSTANCE_ZONE):
        return (
            cls.init_compute_client()
            .instances()
            .delete(
                project=settings.GCP_PROJECT_ID,
                zone=zone,
                instance=cls._build_vm_id_from_job_id(job_uuid),
            )
            .execute()
        )

    @classmethod
    def _build_vm_id_from_job_id(cls, job_uuid: uuid4):
        return f"job-{job_uuid}-runner"
