import boto3
from unittest import TestCase

from tests.integration.utils.patcher import patch_client


class PatchBotoIntegBase(TestCase):
    @classmethod
    def setUpclass(cls):
        client_to_be_patched = getattr(boto3.session.Session, "client")
        boto3.session.Session = patch_client(client_to_be_patched=client_to_be_patched)
