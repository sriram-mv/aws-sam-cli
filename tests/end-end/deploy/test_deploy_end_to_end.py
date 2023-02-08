import json
import os
import shutil
from pathlib import Path

from botocore.config import Config

from samcli.lib.bootstrap.bootstrap import SAM_CLI_STACK_NAME
from tests.integration.buildcmd.build_integ_base import BuildIntegGoBase, BuildIntegPythonBase, BuildIntegBase
from tests.integration.deploy.deploy_integ_base import DeployIntegBase
from tests.integration.list.stack_outputs.stack_outputs_integ_base import StackOutputsIntegBase

from unittest import TestCase

from tests.integration.package.package_integ_base import PackageIntegBase
from tests.testing_utils import run_command


import boto3


class MinimalCompiledEndtoEndTest(BuildIntegGoBase, PackageIntegBase, DeployIntegBase, StackOutputsIntegBase):
    template = "template-only-function.yaml"

    @classmethod
    def setUpClass(cls):
        BuildIntegGoBase.setUpClass()
        PackageIntegBase.setUpClass()
        DeployIntegBase.setUpClass()
        StackOutputsIntegBase.setUpClass()

    def setUp(self):
        self.stacks = []
        self.lambda_client = boto3.client("lambda")
        self.cfn_client = boto3.client("cloudformation")
        super().setUp()

    def tearDown(self):
        for stack in self.stacks:
            # because of the termination protection, do not delete aws-sam-cli-managed-default stack
            stack_name = stack["name"]
            if stack_name != SAM_CLI_STACK_NAME:
                region = stack.get("region")
                cfn_client = (
                    self.cfn_client if not region else boto3.client("cloudformation", config=Config(region_name=region))
                )
                cfn_client.delete_stack(StackName=stack_name)
        super().tearDown()

    def test_build_deploy_invoke_go(self):
        self.template_path = str(Path(self.test_data_path, self.template)) if self.template else None
        newenv = os.environ.copy()

        newenv["GOPROXY"] = "direct"
        newenv["GOPATH"] = str(self.working_dir)
        overrides = self.get_override("go1.x", "Go", None, "hello-world")
        cmdlist = self.get_command_list(parameter_overrides=overrides)
        build_result = run_command(cmdlist, cwd=self.working_dir, env=newenv)

        # Verify Successful Build
        self.assertEqual(build_result.process.returncode, 0)

        stack_name = self._method_to_stack_name(self.id())
        self.stacks.append({"name": stack_name})
        parameter_overrides = " ".join(["{key}={value}".format(key=key, value=value) for key, value in overrides.items()])
        deploy_command_list = self.get_deploy_command_list(
            stack_name=stack_name,
            capabilities="CAPABILITY_IAM",
            s3_bucket=self.s3_bucket.name,
            parameter_overrides=parameter_overrides,
            force_upload=True,
            confirm_changeset=False,
        )
        deploy_process_execute = run_command(deploy_command_list, cwd=self.working_dir)
        # Verify Successful Deploy
        self.assertEqual(deploy_process_execute.process.returncode, 0)

        # List Lambda Resource that was deployed
        list_command_list = self.get_stack_outputs_command_list(stack_name=stack_name, output="json")
        list_command_execute = run_command(list_command_list, cwd=self.working_dir)

        # Verify Successful list
        self.assertEqual(list_command_execute.process.returncode, 0)
        json_output = json.loads(list_command_execute.stdout.decode())
        lambda_function_name = None
        for resource in json_output:
            output_key, output_value, _ = resource.get("OutputKey"), resource.get("OutputValue"), resource.get("Description")
            if output_key == self.FUNCTION_LOGICAL_ID:
                lambda_function_name = output_value
                break
        if not lambda_function_name:
            raise Exception("baah Broke!")

        # Verify Invoked Lambda
        lambda_output = self.lambda_client.invoke(FunctionName=lambda_function_name)
        self.assertEqual(lambda_output.get("StatusCode"), 200)
        self.assertEqual(lambda_output.get("FunctionError", ""), "")
