from aws_cdk import (
    Stack,
    aws_ec2 as ec2,
    aws_workspaces as workspaces,
    aws_directoryservice as directory,
    CfnOutput,
)
from constructs import Construct

class Client(Stack):
    def __init__(self, scope: Construct, construct_id: str, *, client_config: dict, **kwargs):
        super().__init__(scope, construct_id, **kwargs)

        # Extract config values with defaults
        vpc_cidr = client_config.get('vpc_cidr', '10.0.0.0/16')
        directory_name = client_config.get('directory_name', 'workspace.local')
        admin_password = client_config.get('admin_password')
        bundle_id = client_config.get('bundle_id')
        pool_size = client_config.get('pool_size', 2)

        # Create VPC
        self.vpc = ec2.Vpc(
            self,
            f"{client_config['name']}-VPC",
            ip_addresses=ec2.IpAddresses.cidr(vpc_cidr),
            max_azs=2,
            nat_gateways=1,
            subnet_configuration=[
                ec2.SubnetConfiguration(
                    name="Public",
                    subnet_type=ec2.SubnetType.PUBLIC,
                    cidr_mask=24
                ),
                ec2.SubnetConfiguration(
                    name="Private",
                    subnet_type=ec2.SubnetType.PRIVATE_WITH_EGRESS,
                    cidr_mask=24
                ),
            ],
        )

        # Create Directory Service
        directory_service = directory.CfnMicrosoftAD(
            self,
            f"{client_config['name']}-Directory",
            name=directory_name,
            password=admin_password,
            vpc_settings=directory.CfnMicrosoftAD.VpcSettingsProperty(
                subnet_ids=[
                    self.vpc.private_subnets[0].subnet_id,
                    self.vpc.private_subnets[1].subnet_id
                ],
                vpc_id=self.vpc.vpc_id
            ),
            edition='Standard'
        )

        # Create WorkSpaces Pool
        workspace_pool = workspaces.CfnWorkspacesPool(
            self,
            f"{client_config['name']}-WorkspacePool",
            bundle_id=bundle_id,
            capacity=workspaces.CfnWorkspacesPool.CapacityProperty(
                desired_user_sessions=pool_size
            ),
            directory_id=directory_service.attr_id ,  # This gets the directory ID
            pool_name=f"{client_config['name']}-pool",
            description=f"Workspace Pool for {client_config['name']}",
            timeout_settings=workspaces.CfnWorkspacesPool.TimeoutSettingsProperty(
                disconnect_timeout_in_seconds=60,
            ),
        )

        # Add dependencies
        workspace_pool.node.add_dependency(directory_service)

        # Outputs
        CfnOutput(
            self,
            "VPCId",
            value=self.vpc.vpc_id,
            description=f"VPC ID for {client_config['name']}"
        )
        
        CfnOutput(
            self,
            "DirectoryId",
            value=directory_service.attr_alias,
            description=f"Directory ID for {client_config['name']}"
        )
        
        CfnOutput(
            self,
            "WorkspacePoolId",
            value=workspace_pool.attr_pool_id,
            description=f"Workspace Pool ID for {client_config['name']}"
        )