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


def empty_s3_bucket(bucket_name):
    """
    Empty all objects and versions from an S3 bucket
    
    Args:
        bucket_name: Name of the S3 bucket to empty
        
    Returns:
        True if successful, False otherwise
    """
    try:
        s3_client = boto3.client('s3')
        s3_resource = boto3.resource('s3')
        bucket = s3_resource.Bucket(bucket_name)
        
        print(f"Emptying S3 bucket: {bucket_name}")
        
        # Delete all object versions
        bucket.object_versions.all().delete()
        
        # Delete all objects (in case versioning is not enabled)
        bucket.objects.all().delete()
        
        print(f"Successfully emptied bucket: {bucket_name}")
        return True
        
    except ClientError as e:
        if e.response['Error']['Code'] == 'NoSuchBucket':
            print(f"Bucket {bucket_name} does not exist")
            return True
        else:
            print(f"Error emptying bucket {bucket_name}: {str(e)}")
            return False
    except Exception as e:
        print(f"Error emptying bucket {bucket_name}: {str(e)}")
        return False


def delete_design_guidelines_stack(stack_name="design-guidelines-stack"):
    """
    Delete the design guidelines CloudFormation stack
    
    Args:
        stack_name: Name of the CloudFormation stack to delete
        
    Returns:
        True if deletion was successful, False otherwise
    """
    try:
        # Initialize CloudFormation client
        cf_client = boto3.client('cloudformation')
        
        print(f"Checking if stack {stack_name} exists...")
        
        # Check if stack exists and get bucket name from outputs
        bucket_name = None
        try:
            response = cf_client.describe_stacks(StackName=stack_name)
            stack_status = response['Stacks'][0]['StackStatus']
            print(f"Stack found with status: {stack_status}")
            
            # Extract bucket name from stack outputs
            if 'Outputs' in response['Stacks'][0]:
                for output in response['Stacks'][0]['Outputs']:
                    if output['OutputKey'] == 'BucketName':
                        bucket_name = output['OutputValue']
                        print(f"Found S3 bucket: {bucket_name}")
                        break
            
            # Check if stack is already being deleted or doesn't exist
            if stack_status in ['DELETE_IN_PROGRESS', 'DELETE_COMPLETE']:
                print(f"Stack is already in {stack_status} state")
                if stack_status == 'DELETE_IN_PROGRESS':
                    print("Waiting for deletion to complete...")
                    waiter = cf_client.get_waiter('stack_delete_complete')
                    waiter.wait(
                        StackName=stack_name,
                        WaiterConfig={
                            'Delay': 30,
                            'MaxAttempts': 20
                        }
                    )
                    print("Stack deletion completed")
                return True
                
        except ClientError as e:
            if 'does not exist' in str(e):
                print(f"Stack {stack_name} does not exist")
                return True
            else:
                raise e
        
        # Empty the S3 bucket before deleting the stack
        if bucket_name:
            print(f"Emptying S3 bucket before stack deletion...")
            if not empty_s3_bucket(bucket_name):
                print("Warning: Failed to empty S3 bucket, stack deletion may fail")
        
        # Delete the stack
        print(f"Initiating deletion of stack: {stack_name}")
        cf_client.delete_stack(StackName=stack_name)
        
        # Wait for stack deletion to complete
        print("Waiting for stack deletion to complete...")
        try:
            waiter = cf_client.get_waiter('stack_delete_complete')
            waiter.wait(
                StackName=stack_name,
                WaiterConfig={
                    'Delay': 30,
                    'MaxAttempts': 20
                }
            )
            print(f"Stack {stack_name} deleted successfully!")
            return True
            
        except ClientError as e:
            print(f"Deletion waiter failed: {str(e)}")
            print("Checking stack status manually...")
            time.sleep(30)
            
            # Check final status
            try:
                response = cf_client.describe_stacks(StackName=stack_name)
                final_status = response['Stacks'][0]['StackStatus']
                print(f"Stack final status: {final_status}")
                
                if final_status == 'DELETE_FAILED':
                    print("Stack deletion failed. Check AWS Console for details.")
                    return False
                    
            except ClientError as check_error:
                if 'does not exist' in str(check_error):
                    print("Stack successfully deleted")
                    return True
                else:
                    raise check_error
        
        return True
        
    except Exception as e:
        print(f"Error deleting stack: {str(e)}")
        return False


if __name__ == "__main__":
    import sys
    
    # Check command line arguments
    if len(sys.argv) > 1 and sys.argv[1] == "delete":
        # Delete the stack
        print("Deleting design guidelines stack...")
        success = delete_design_guidelines_stack()
        
        if success:
            print("\nDeletion successful!")
        else:
            print("\nDeletion failed!")
            exit(1)
    else:
        # Deploy the stack
        outputs = deploy_design_guidelines_stack()
        
        if outputs:
            print("\nDeployment successful!")
            print(json.dumps(outputs, indent=2))
        else:
            print("\nDeployment failed!")
            exit(1)