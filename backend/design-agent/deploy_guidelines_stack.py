#!/usr/bin/env python3
"""
Deploy CloudFormation stack for Design Guidelines infrastructure
"""

import boto3
import json
import logging
import time
from pathlib import Path
from typing import Tuple, Optional

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def deploy_guidelines_stack(
    stack_name: str,
    template_file: str,
    region: str,
    cf_client: boto3.client,
    bucket_prefix: str = "design-guidelines"
) -> Tuple[str, str, str, str, str]:
    """
    Deploy the CloudFormation stack for design guidelines infrastructure.
    
    Args:
        stack_name: Name of the CloudFormation stack
        template_file: Path to the CloudFormation template
        region: AWS region
        cf_client: CloudFormation boto3 client
        bucket_prefix: Prefix for the S3 bucket name
        
    Returns:
        Tuple of (bucket_name, lambda_arn, gateway_role_arn, runtime_role_arn, bucket_arn)
    """
    try:
        # Read the CloudFormation template
        template_path = Path(template_file)
        if not template_path.exists():
            raise FileNotFoundError(f"Template file not found: {template_file}")
            
        with open(template_path, 'r') as f:
            template_body = f.read()

        # Check if stack already exists
        try:
            cf_client.describe_stacks(StackName=stack_name)
            logger.info(f"Stack {stack_name} already exists. Updating...")
            
            # Update the stack
            cf_client.update_stack(
                StackName=stack_name,
                TemplateBody=template_body,
                Parameters=[
                    {
                        'ParameterKey': 'BucketNamePrefix',
                        'ParameterValue': bucket_prefix
                    }
                ],
                Capabilities=['CAPABILITY_NAMED_IAM']
            )
            
            # Wait for update to complete
            waiter = cf_client.get_waiter('stack_update_complete')
            logger.info("Waiting for stack update to complete...")
            waiter.wait(StackName=stack_name)
            
        except cf_client.exceptions.ClientError as e:
            if 'does not exist' in str(e):
                logger.info(f"Creating new stack: {stack_name}")
                
                # Create the stack
                cf_client.create_stack(
                    StackName=stack_name,
                    TemplateBody=template_body,
                    Parameters=[
                        {
                            'ParameterKey': 'BucketNamePrefix',
                            'ParameterValue': bucket_prefix
                        }
                    ],
                    Capabilities=['CAPABILITY_NAMED_IAM']
                )
                
                # Wait for creation to complete
                waiter = cf_client.get_waiter('stack_create_complete')
                logger.info("Waiting for stack creation to complete...")
                waiter.wait(StackName=stack_name)
            elif 'No updates are to be performed' in str(e):
                logger.info("Stack is already up to date, no changes needed")
            else:
                raise e

        # Get stack outputs
        response = cf_client.describe_stacks(StackName=stack_name)
        stack = response['Stacks'][0]
        
        outputs = {}
        for output in stack.get('Outputs', []):
            outputs[output['OutputKey']] = output['OutputValue']

        bucket_name = outputs.get('S3BucketName')
        lambda_arn = outputs.get('LambdaFunctionArn')
        gateway_role_arn = outputs.get('GatewayRoleArn')
        runtime_role_arn = outputs.get('RuntimeExecutionRoleArn')
        bucket_arn = outputs.get('S3BucketArn')

        logger.info(f"Stack deployment completed successfully")
        logger.info(f"S3 Bucket: {bucket_name}")
        logger.info(f"Lambda ARN: {lambda_arn}")
        logger.info(f"Gateway Role ARN: {gateway_role_arn}")
        logger.info(f"Runtime Role ARN: {runtime_role_arn}")

        return bucket_name, lambda_arn, gateway_role_arn, runtime_role_arn, bucket_arn

    except Exception as e:
        logger.error(f"Error deploying stack: {e}")
        raise


def delete_guidelines_stack(
    stack_name: str,
    region: str,
    cf_client: boto3.client,
    wait: bool = True
) -> bool:
    """
    Delete the CloudFormation stack for design guidelines infrastructure.
    
    Args:
        stack_name: Name of the CloudFormation stack
        region: AWS region
        cf_client: CloudFormation boto3 client
        wait: Whether to wait for deletion to complete
        
    Returns:
        True if successful, False otherwise
    """
    try:
        logger.info(f"Deleting stack: {stack_name}")
        
        # Check if stack exists
        try:
            cf_client.describe_stacks(StackName=stack_name)
        except cf_client.exceptions.ClientError as e:
            if 'does not exist' in str(e):
                logger.warning(f"Stack {stack_name} does not exist")
                return True
            else:
                raise e

        # Delete the stack
        cf_client.delete_stack(StackName=stack_name)
        
        if wait:
            # Wait for deletion to complete
            waiter = cf_client.get_waiter('stack_delete_complete')
            logger.info("Waiting for stack deletion to complete...")
            waiter.wait(StackName=stack_name)
            
        logger.info(f"Stack {stack_name} deleted successfully")
        return True

    except Exception as e:
        logger.error(f"Error deleting stack: {e}")
        return False


def upload_guidelines_to_s3(
    bucket_name: str,
    guidelines_file: str,
    s3_client: boto3.client,
    object_key: Optional[str] = None
) -> str:
    """
    Upload additional guidelines file to S3 bucket.
    
    Args:
        bucket_name: Name of the S3 bucket
        guidelines_file: Path to the guidelines file
        s3_client: S3 boto3 client
        object_key: S3 object key (defaults to filename)
        
    Returns:
        S3 URI of the uploaded file
    """
    try:
        guidelines_path = Path(guidelines_file)
        if not guidelines_path.exists():
            raise FileNotFoundError(f"Guidelines file not found: {guidelines_file}")
            
        if object_key is None:
            object_key = guidelines_path.name
            
        logger.info(f"Uploading {guidelines_file} to s3://{bucket_name}/{object_key}")
        
        with open(guidelines_path, 'rb') as f:
            s3_client.put_object(
                Bucket=bucket_name,
                Key=object_key,
                Body=f,
                ContentType='text/markdown'
            )
            
        s3_uri = f"s3://{bucket_name}/{object_key}"
        logger.info(f"Successfully uploaded to {s3_uri}")
        return s3_uri
        
    except Exception as e:
        logger.error(f"Error uploading guidelines to S3: {e}")
        raise


if __name__ == "__main__":
    # Example usage
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python deploy_guidelines_stack.py <deploy|delete>")
        sys.exit(1)
        
    action = sys.argv[1].lower()
    
    # Configuration
    stack_name = "design-guidelines-stack"
    template_file = "cloudformation/design_guidelines_stack.yaml"
    region = "us-west-2"  # Change as needed
    
    # Initialize AWS clients
    session = boto3.Session()
    cf_client = session.client("cloudformation", region_name=region)
    s3_client = session.client("s3", region_name=region)
    
    if action == "deploy":
        try:
            bucket_name, lambda_arn, gateway_role_arn, runtime_role_arn, bucket_arn = deploy_guidelines_stack(
                stack_name=stack_name,
                template_file=template_file,
                region=region,
                cf_client=cf_client
            )
            
            # Upload additional guidelines if they exist
            guidelines_file = "../guidelines/technical-design-guidelines.md"
            if Path(guidelines_file).exists():
                upload_guidelines_to_s3(
                    bucket_name=bucket_name,
                    guidelines_file=guidelines_file,
                    s3_client=s3_client,
                    object_key="technical-design-guidelines.md"
                )
            
            print(f"\nDeployment completed successfully!")
            print(f"S3 Bucket: {bucket_name}")
            print(f"Lambda ARN: {lambda_arn}")
            print(f"Gateway Role ARN: {gateway_role_arn}")
            print(f"Runtime Role ARN: {runtime_role_arn}")
            
        except Exception as e:
            print(f"Deployment failed: {e}")
            sys.exit(1)
            
    elif action == "delete":
        try:
            success = delete_guidelines_stack(
                stack_name=stack_name,
                region=region,
                cf_client=cf_client
            )
            
            if success:
                print("Stack deleted successfully!")
            else:
                print("Stack deletion failed!")
                sys.exit(1)
                
        except Exception as e:
            print(f"Deletion failed: {e}")
            sys.exit(1)
            
    else:
        print("Invalid action. Use 'deploy' or 'delete'")
        sys.exit(1)