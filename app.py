#!/usr/bin/env python3
import os
from aws_cdk import App, Environment
from src.classes.st_iac.client import Client

app = App()

# Get client config from context
client_name = app.node.try_get_context("client")
if not client_name:
    raise ValueError("Please provide a client name using -c client=NAME")

# Get client-specific configuration
client_config = {
    "name": client_name,
    "vpc_cidr": app.node.try_get_context("vpc_cidr") or "10.0.0.0/16",
    "directory_name": app.node.try_get_context("directory_name") or "workspace.local",
    "admin_password": app.node.try_get_context("admin_password"),
    "bundle_id": app.node.try_get_context("bundle_id") or "wsb-bh8rsxt14",
    "pool_size": int(app.node.try_get_context("pool_size") or "2"),
}
region = app.node.try_get_context("region") or os.getenv('CDK_DEFAULT_REGION')

# Validate required parameters
# The password must be between 8 and 64 characters, not contain the word "admin", and must have at least one character from three of these four categories: lowercase, uppercase, numeric, and special characters.

if not client_config["admin_password"]:
    raise ValueError("Please provide an admin password using -c admin_password=PASSWORD")

# validate password length and complexity
if len(client_config["admin_password"]) < 8 or len(client_config["admin_password"]) > 64:
    raise ValueError("The password must be between 8 and 64 characters")
if "admin" in client_config["admin_password"].lower():
    raise ValueError("The password cannot contain the word 'admin'")
if not any(c.islower() for c in client_config["admin_password"]):
    raise ValueError("The password must contain at least one lowercase character")
if not any(c.isupper() for c in client_config["admin_password"]):
    raise ValueError("The password must contain at least one uppercase character")
if not any(c.isdigit() for c in client_config["admin_password"]):
    raise ValueError("The password must contain at least one numeric character")
if not any(c in "!@#$%^&*()-_=+[]{}|;:,.<>?/~" for c in client_config["admin_password"]):
    raise ValueError("The password must contain at least one special character")


# Create the stack
Client(
    app,
    f"ClientInfra-{client_name}",
    client_config=client_config,
    env=Environment(
        account=os.getenv('CDK_DEFAULT_ACCOUNT'),
        region=region
    )
)

app.synth()