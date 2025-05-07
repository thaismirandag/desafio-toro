
from aws_cdk import App, CfnOutput, Duration, RemovalPolicy, Stack
from aws_cdk import aws_apigateway as apigateway
from aws_cdk import aws_dynamodb as dynamodb
from aws_cdk import aws_iam as iam
from aws_cdk import aws_lambda as _lambda
from aws_cdk import aws_sns as sns
from aws_cdk.aws_sns_subscriptions import LambdaSubscription
from constructs import Construct
import os
from dotenv import load_dotenv

load_dotenv()

OPENAI_API_KEY = os.environ["OPENAI_API_KEY"]
AWS_ACCOUNT_ID  = os.environ["AWS_ACCOUNT_ID"]

class DesafioToroStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)


        questions_table = dynamodb.Table(
            self, "QuestionsTable",
            table_name="questions",
            partition_key=dynamodb.Attribute(
                name="id",
                type=dynamodb.AttributeType.STRING
            ),
            billing_mode=dynamodb.BillingMode.PAY_PER_REQUEST,
            removal_policy=RemovalPolicy.DESTROY,
            time_to_live_attribute="ttl"
        )

        questions_table.add_global_secondary_index(
            index_name="SessionIndex",
            partition_key=dynamodb.Attribute(
                name="session_id",
                type=dynamodb.AttributeType.STRING
            ),
            sort_key=dynamodb.Attribute(
                name="created_at",
                type=dynamodb.AttributeType.STRING
            ),
            projection_type=dynamodb.ProjectionType.ALL
        )

        sessions_table = dynamodb.Table(
            self, "SessionsTable",
            table_name="sessions",
            partition_key=dynamodb.Attribute(
                name="session_id",
                type=dynamodb.AttributeType.STRING
            ),
            billing_mode=dynamodb.BillingMode.PAY_PER_REQUEST,
            removal_policy=RemovalPolicy.DESTROY 
        )

 
        process_question_topic = sns.Topic(
            self, "ProcessQuestionTopic",
            topic_name="process-question",
            display_name="Process Question Topic"
        )

        notify_response_topic = sns.Topic(
            self, "NotifyResponseTopic",
            topic_name="notify-response",
            display_name="Notify Response Topic"
        )

        # IAM Role for Lambda
        lambda_role = iam.Role(
            self, "LambdaRole",
            assumed_by=iam.ServicePrincipal("lambda.amazonaws.com"),
            description="Role for Lambda functions"
        )

        # DynamoDB permissions
        lambda_role.add_to_policy(
            iam.PolicyStatement(
                effect=iam.Effect.ALLOW,
                actions=[
                    "dynamodb:GetItem",
                    "dynamodb:PutItem",
                    "dynamodb:UpdateItem",
                    "dynamodb:DeleteItem",
                    "dynamodb:Query",
                    "dynamodb:Scan"
                ],
                resources=[
                    questions_table.table_arn,
                    f"{questions_table.table_arn}/index/*", 
                    sessions_table.table_arn
                ]
            )
        )

        lambda_role.add_to_policy(
            iam.PolicyStatement(
                effect=iam.Effect.ALLOW,
                actions=["sns:Publish"],
                resources=[
                    process_question_topic.topic_arn,
                    notify_response_topic.topic_arn
                ]
            )
        )


        lambda_role.add_to_policy(
            iam.PolicyStatement(
                effect=iam.Effect.ALLOW,
                actions=[
                    "logs:CreateLogGroup",
                    "logs:CreateLogStream",
                    "logs:PutLogEvents"
                ],
                resources=["arn:aws:logs:*:*:*"]
            )
        )

  
        lambda_role.add_to_policy(
            iam.PolicyStatement(
                effect=iam.Effect.ALLOW,
                actions=[
                    "execute-api:Invoke",
                    "execute-api:ManageConnections"
                ],
                resources=["arn:aws:execute-api:*:*:*"]
            )
        )

        lambda_role.add_to_policy(
            iam.PolicyStatement(
                effect=iam.Effect.ALLOW,
                actions=[
                    "cloudfront:CreateInvalidation",
                    "cloudfront:GetInvalidation",
                    "cloudfront:ListInvalidations"
                ],
                resources=["*"]
            )
        )


        process_question_lambda = _lambda.Function(
            self, "ProcessQuestionFunction",
            runtime=_lambda.Runtime.PYTHON_3_11,
            handler="process_question.handler",
            code=_lambda.Code.from_asset("lambda_package.zip"),
            role=lambda_role,
            environment={
                "DYNAMODB_TABLE_SESSIONS": sessions_table.table_name,
                "DYNAMODB_TABLE_QUESTIONS": questions_table.table_name,
                "SNS_TOPIC_NOTIFY_NAME": notify_response_topic.topic_arn,
                "OPENAI_API_KEY": OPENAI_API_KEY,
                "AWS_ACCOUNT_ID": AWS_ACCOUNT_ID
            },
            timeout=Duration.seconds(30),
            memory_size=256,
            architecture=_lambda.Architecture.ARM_64
        )

        notify_user_lambda = _lambda.Function(
            self, "NotifyUserFunction",
            runtime=_lambda.Runtime.PYTHON_3_11,
            handler="notify_user.handler",
            code=_lambda.Code.from_asset("lambda_package.zip"),
            role=lambda_role,
            environment={
                "DYNAMODB_TABLE_SESSIONS": sessions_table.table_name,
                "DYNAMODB_TABLE_QUESTIONS": questions_table.table_name,
                "SNS_TOPIC_NOTIFY_NAME": notify_response_topic.topic_name,
                "AWS_ACCOUNT_ID": AWS_ACCOUNT_ID,
                "OPENAI_API_KEY": OPENAI_API_KEY
            },
            timeout=Duration.seconds(30),
            memory_size=256,
            architecture=_lambda.Architecture.ARM_64
        )

        fastapi_lambda = _lambda.Function(
            self, "FastApi",
            runtime=_lambda.Runtime.PYTHON_3_11,
            handler="lambda_handler.handler",
            code=_lambda.Code.from_asset("lambda_package.zip"),
            role=lambda_role,
            timeout=Duration.seconds(30),
            memory_size=512,
            environment={
                "DYNAMODB_TABLE_SESSIONS": sessions_table.table_name,
                "DYNAMODB_TABLE_QUESTIONS": questions_table.table_name,                
                "AWS_ACCOUNT_ID": AWS_ACCOUNT_ID,
                "OPENAI_API_KEY": OPENAI_API_KEY,
                "SNS_TOPIC_NOTIFY_NAME": notify_response_topic.topic_name,  
                "SNS_TOPIC_PROCESS_QUESTION_NAME": process_question_topic.topic_name
            }
        )

        api = apigateway.LambdaRestApi(
            self, "FastApiEndpoint",
            handler=fastapi_lambda,
            proxy=True,
            rest_api_name="DesafioToroFastAPI",
            default_cors_preflight_options=apigateway.CorsOptions(
                allow_origins=apigateway.Cors.ALL_ORIGINS,
                allow_methods=apigateway.Cors.ALL_METHODS
            ),
        )

        process_question_topic.add_subscription(
            LambdaSubscription(process_question_lambda)
        )

        notify_response_topic.add_subscription(
            LambdaSubscription(notify_user_lambda)
        )

        # Outputs
        CfnOutput(
            self, "ApiEndpoint",
            value=api.url,
            description="API Gateway endpoint URL"
        )

        CfnOutput(
            self, "QuestionsTableName",
            value=questions_table.table_name,
            description="DynamoDB table name"
        )

app = App()
DesafioToroStack(app, "DesafioToroStack")
app.synth()
