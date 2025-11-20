#!/usr/bin/env python3
"""
Deploy Design Guidelines CloudFormation Stack
"""

import boto3
import time
import json
from botocore.exceptions import ClientError


def deploy_design_guidelines_stack(stack_name="design-guidelines-stack", bucket_prefix="design-guidelines"):
    """
    Deploy the design guidelines CloudFormation stack
    
    Args:
        stack_name: Name of the CloudFormation stack
        bucket_prefix: Prefix for the S3 bucket name
        
    Returns:
        Dictionary with stack outputs or None if failed
    """
    try:
        # Initialize CloudFormation client
        cf_client = boto3.client('cloudformation')
        
        # Read the CloudFormation template
        with open('cloudformation/design_guidelines_stack.yaml', 'r') as f:
            template_body = f.read()
        
        print(f"Deploying CloudFormation stack: {stack_name}")
        
        # Check if stack already exists
        stack_exists = False
        try:
            cf_client.describe_stacks(StackName=stack_name)
            stack_exists = True
            print(f"Stack {stack_name} already exists, attempting update...")
            
            try:
                # Update existing stack
                cf_client.update_stack(
                    StackName=stack_name,
                    TemplateBody=template_body,
                    Parameters=[
                        {
                            'ParameterKey': 'BucketNamePrefix',
                            'ParameterValue': bucket_prefix
                        }
                    ],
                    Capabilities=['CAPABILITY_IAM', 'CAPABILITY_NAMED_IAM']
                )
                print("Stack update initiated...")
                
            except ClientError as update_error:
                if 'No updates are to be performed' in str(update_error):
                    print("Stack is already up to date, no changes needed.")
                    # Skip waiting, go directly to getting outputs
                    stack_exists = True
                else:
                    raise update_error
            
        except ClientError as e:
            if 'does not exist' in str(e):
                print(f"Creating new stack: {stack_name}")
                stack_exists = False
                
                # Create new stack
                cf_client.create_stack(
                    StackName=stack_name,
                    TemplateBody=template_body,
                    Parameters=[
                        {
                            'ParameterKey': 'BucketNamePrefix',
                            'ParameterValue': bucket_prefix
                        }
                    ],
                    Capabilities=['CAPABILITY_IAM', 'CAPABILITY_NAMED_IAM']
                )
            else:
                raise e
        
        # Wait for stack to complete (only if we actually made changes)
        if stack_exists:
            # Check current stack status
            response = cf_client.describe_stacks(StackName=stack_name)
            current_status = response['Stacks'][0]['StackStatus']
            
            if current_status in ['UPDATE_IN_PROGRESS']:
                print("Waiting for stack update to complete...")
                try:
                    update_waiter = cf_client.get_waiter('stack_update_complete')
                    update_waiter.wait(
                        StackName=stack_name,
                        WaiterConfig={
                            'Delay': 30,
                            'MaxAttempts': 20
                        }
                    )
                    print("Stack update completed")
                except ClientError as e:
                    print(f"Update waiter failed: {str(e)}")
                    print("Checking stack status manually...")
                    time.sleep(30)
            elif current_status in ['CREATE_COMPLETE', 'UPDATE_COMPLETE']:
                print("Stack is already in completed state")
            else:
                print(f"Stack is in status: {current_status}")
        else:
            # New stack creation
            print("Waiting for stack creation to complete...")
            try:
                waiter = cf_client.get_waiter('stack_create_complete')
                waiter.wait(
                    StackName=stack_name,
                    WaiterConfig={
                        'Delay': 30,
                        'MaxAttempts': 20
                    }
                )
                print("Stack creation completed")
            except ClientError as e:
                print(f"Creation waiter failed: {str(e)}")
                print("Checking stack status manually...")
                time.sleep(30)
        
        # Get stack outputs
        response = cf_client.describe_stacks(StackName=stack_name)
        stack = response['Stacks'][0]
        
        if stack['StackStatus'] not in ['CREATE_COMPLETE', 'UPDATE_COMPLETE']:
            print(f"Stack deployment failed with status: {stack['StackStatus']}")
            return None
        
        # Extract outputs
        outputs = {}
        if 'Outputs' in stack:
            for output in stack['Outputs']:
                outputs[output['OutputKey']] = output['OutputValue']
        
        print("Stack deployment completed successfully!")
        print("Stack outputs:")
        for key, value in outputs.items():
            print(f"  {key}: {value}")
        
        return outputs
        
    except Exception as e:
        print(f"Error deploying stack: {str(e)}")
        return None


if __name__ == "__main__":
    # Deploy the stack
    outputs = deploy_design_guidelines_stack()
    
    if outputs:
        print("\nDeployment successful!")
        print(json.dumps(outputs, indent=2))
    else:
        print("\nDeployment failed!")
        exit(1)