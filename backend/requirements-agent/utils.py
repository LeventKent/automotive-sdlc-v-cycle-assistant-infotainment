import boto3
import json
import time
import os
from boto3.session import Session

USER_NAME = "testuser"
PASSWORD = "MyPassword123!"
TEMP_ADMIN_PASSWORD = "Temp123!"


def setup_cognito_user_pool():
    boto_session = Session(profile_name=os.environ.get('AWS_PROFILE'))
    region = boto_session.region_name
    # Initialize Cognito client
    cognito_client = boto3.client("cognito-idp", region_name=region)
    
    try:
        # First, try to find existing user pool
        existing_pools = cognito_client.list_user_pools(MaxResults=50)
        pool_id = None
        client_id = None
        
        for pool in existing_pools['UserPools']:
            if pool['Name'] == "AutomotiveMCPServerPool":
                pool_id = pool['Id']
                print(f"Found existing user pool: {pool_id}")
                
                # Get existing app client
                clients = cognito_client.list_user_pool_clients(
                    UserPoolId=pool_id,
                    MaxResults=50
                )
                for client in clients['UserPoolClients']:
                    if client['ClientName'] == "AutomotiveMCPServerPoolClient":
                        client_id = client['ClientId']
                        print(f"Found existing app client: {client_id}")
                        break
                break
        
        # If no existing pool found, create new one
        if not pool_id:
            print("Creating new user pool...")
            user_pool_response = cognito_client.create_user_pool(
                PoolName="AutomotiveMCPServerPool", 
                Policies={"PasswordPolicy": {"MinimumLength": 8}}
            )
            pool_id = user_pool_response["UserPool"]["Id"]
            print(f"Created new user pool: {pool_id}")
        
        # If no existing client found, create new one
        if not client_id:
            print("Creating new app client...")
            app_client_response = cognito_client.create_user_pool_client(
                UserPoolId=pool_id,
                ClientName="AutomotiveMCPServerPoolClient",
                GenerateSecret=False,
                ExplicitAuthFlows=["ALLOW_USER_PASSWORD_AUTH", "ALLOW_REFRESH_TOKEN_AUTH"],
            )
            client_id = app_client_response["UserPoolClient"]["ClientId"]
            print(f"Created new app client: {client_id}")
        
        # Check if user exists, create if not
        try:
            cognito_client.admin_get_user(
                UserPoolId=pool_id,
                Username=USER_NAME
            )
            print(f"User {USER_NAME} already exists")
        except cognito_client.exceptions.UserNotFoundException:
            print(f"Creating user {USER_NAME}...")
            # Create User
            cognito_client.admin_create_user(
                UserPoolId=pool_id,
                Username=USER_NAME,
                TemporaryPassword=TEMP_ADMIN_PASSWORD,
                MessageAction="SUPPRESS",
            )
            
            # Set Permanent Password
            cognito_client.admin_set_user_password(
                UserPoolId=pool_id, Username=USER_NAME, Password=PASSWORD, Permanent=True
            )
            print(f"User {USER_NAME} created successfully")
        
        # Authenticate User and get Access Token
        auth_response = cognito_client.initiate_auth(
            ClientId=client_id,
            AuthFlow="USER_PASSWORD_AUTH",
            AuthParameters={"USERNAME": USER_NAME, "PASSWORD": PASSWORD},
        )
        bearer_token = auth_response["AuthenticationResult"]["AccessToken"]
        refresh_token = auth_response["AuthenticationResult"]["RefreshToken"]
        
        # Output the required values
        print(f"Pool id: {pool_id}")
        print(
            f"Discovery URL: https://cognito-idp.{region}.amazonaws.com/{pool_id}/.well-known/openid-configuration"
        )
        print(f"Client ID: {client_id}")
        print(f"Bearer Token: {bearer_token}")
        print(f"Refresh Token: {refresh_token}")

        # Return values if needed for further processing
        return {
            "pool_id": pool_id,
            "client_id": client_id,
            "bearer_token": bearer_token,
            "refresh_token": refresh_token,
            "discovery_url": f"https://cognito-idp.{region}.amazonaws.com/{pool_id}/.well-known/openid-configuration",
        }
    except Exception as e:
        print(f"Error: {e}")
        return None


def reauthenticate_user(client_id):
    boto_session = Session()
    region = boto_session.region_name
    # Initialize Cognito client
    cognito_client = boto3.client("cognito-idp", region_name=region)
    # Authenticate User and get Access Token
    auth_response = cognito_client.initiate_auth(
        ClientId=client_id,
        AuthFlow="USER_PASSWORD_AUTH",
        AuthParameters={"USERNAME": USER_NAME, "PASSWORD": PASSWORD},
    )
    bearer_token = auth_response["AuthenticationResult"]["AccessToken"]
    return bearer_token


def create_agentcore_role(agent_name):
    iam_client = boto3.client("iam")
    agentcore_role_name = f"agentcore-{agent_name}-role"
    boto_session = Session()
    region = boto_session.region_name
    account_id = boto3.client("sts").get_caller_identity()["Account"]
    
    role_policy = {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Sid": "BedrockPermissions",
                "Effect": "Allow",
                "Action": [
                    "bedrock:InvokeModel",
                    "bedrock:InvokeModelWithResponseStream",
                ],
                "Resource": "*",
            },
            {
                "Sid": "ECRImageAccess",
                "Effect": "Allow",
                "Action": [
                    "ecr:BatchGetImage",
                    "ecr:GetDownloadUrlForLayer",
                    "ecr:GetAuthorizationToken",
                    "ecr:BatchGetImage",
                    "ecr:GetDownloadUrlForLayer",
                ],
                "Resource": [f"arn:aws:ecr:{region}:{account_id}:repository/*"],
            },
            {
                "Effect": "Allow",
                "Action": ["logs:DescribeLogStreams", "logs:CreateLogGroup"],
                "Resource": [
                    f"arn:aws:logs:{region}:{account_id}:log-group:/aws/bedrock-agentcore/runtimes/*"
                ],
            },
            {
                "Effect": "Allow",
                "Action": ["logs:DescribeLogGroups"],
                "Resource": [f"arn:aws:logs:{region}:{account_id}:log-group:*"],
            },
            {
                "Effect": "Allow",
                "Action": ["logs:CreateLogStream", "logs:PutLogEvents"],
                "Resource": [
                    f"arn:aws:logs:{region}:{account_id}:log-group:/aws/bedrock-agentcore/runtimes/*:log-stream:*"
                ],
            },
            {
                "Sid": "ECRTokenAccess",
                "Effect": "Allow",
                "Action": ["ecr:GetAuthorizationToken"],
                "Resource": "*",
            },
            {
                "Effect": "Allow",
                "Action": [
                    "xray:PutTraceSegments",
                    "xray:PutTelemetryRecords",
                    "xray:GetSamplingRules",
                    "xray:GetSamplingTargets",
                ],
                "Resource": ["*"],
            },
            {
                "Effect": "Allow",
                "Resource": "*",
                "Action": "cloudwatch:PutMetricData",
                "Condition": {
                    "StringEquals": {"cloudwatch:namespace": "bedrock-agentcore"}
                },
            },
            {
                "Sid": "GetAgentAccessToken",
                "Effect": "Allow",
                "Action": [
                    "bedrock-agentcore:GetWorkloadAccessToken",
                    "bedrock-agentcore:GetWorkloadAccessTokenForJWT",
                    "bedrock-agentcore:GetWorkloadAccessTokenForUserId",
                ],
                "Resource": [
                    f"arn:aws:bedrock-agentcore:{region}:{account_id}:workload-identity-directory/default",
                    f"arn:aws:bedrock-agentcore:{region}:{account_id}:workload-identity-directory/default/workload-identity/{agent_name}-*",
                ],
            },
        ],
    }
    
    assume_role_policy_document = {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Sid": "AssumeRolePolicy",
                "Effect": "Allow",
                "Principal": {"Service": "bedrock-agentcore.amazonaws.com"},
                "Action": "sts:AssumeRole",
                "Condition": {
                    "StringEquals": {"aws:SourceAccount": f"{account_id}"},
                    "ArnLike": {
                        "aws:SourceArn": f"arn:aws:bedrock-agentcore:{region}:{account_id}:*"
                    },
                },
            }
        ],
    }

    assume_role_policy_document_json = json.dumps(assume_role_policy_document)
    role_policy_document = json.dumps(role_policy)
    
    # Create IAM Role for the Lambda function
    try:
        agentcore_iam_role = iam_client.create_role(
            RoleName=agentcore_role_name,
            AssumeRolePolicyDocument=assume_role_policy_document_json,
        )
        # Pause to make sure role is created
        time.sleep(10)
    except iam_client.exceptions.EntityAlreadyExistsException:
        print("Role already exists -- deleting and creating it again")
        policies = iam_client.list_role_policies(
            RoleName=agentcore_role_name, MaxItems=100
        )
        print("policies:", policies)
        for policy_name in policies["PolicyNames"]:
            iam_client.delete_role_policy(
                RoleName=agentcore_role_name, PolicyName=policy_name
            )
        print(f"deleting {agentcore_role_name}")
        iam_client.delete_role(RoleName=agentcore_role_name)
        print(f"recreating {agentcore_role_name}")
        agentcore_iam_role = iam_client.create_role(
            RoleName=agentcore_role_name,
            AssumeRolePolicyDocument=assume_role_policy_document_json,
        )

    # Attach the policy
    print(f"attaching role policy {agentcore_role_name}")
    try:
        iam_client.put_role_policy(
            PolicyDocument=role_policy_document,
            PolicyName="AgentCorePolicy",
            RoleName=agentcore_role_name,
        )
    except Exception as e:
        print(e)

    return agentcore_iam_role