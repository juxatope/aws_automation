import aws_cdk as core
import aws_cdk.assertions as assertions

from src.classes.st_iac.st_iac_stack import StIacStack

# example tests. To run these tests, uncomment this file along with the example
# resource in st_iac/st_iac_stack.py
def test_sqs_queue_created():
    app = core.App()
    stack = StIacStack(app, "st-iac")
    template = assertions.Template.from_stack(stack)

#     template.has_resource_properties("AWS::SQS::Queue", {
#         "VisibilityTimeout": 300
#     })
