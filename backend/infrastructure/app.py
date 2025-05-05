from aws_cdk import (
    App,
    Stack,
    RemovalPolicy,
    aws_dynamodb as dynamodb,
    aws_iam as iam,
    aws_sns as sns,
    aws_lambda as _lambda,
    aws_sqs as sqs,
    aws_s3 as s3,
    aws_apigateway as apigateway,
    Duration,
    CfnOutput
)
from constructs import Construct
from aws_cdk.aws_apigateway import LambdaIntegration
from aws_cdk.aws_sns_subscriptions import LambdaSubscription

class DesafioToroStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # DynamoDB Table
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

        # SNS Topics
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
            description="Role for Lambda functions in Desafio Toro"
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
                resources=[questions_table.table_arn]
            )
        )

        # SNS permissions
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

        # CloudWatch Logs permissions
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

        # Lambda Functions
        process_question_lambda = _lambda.Function(
            self, "ProcessQuestionFunction",
            runtime=_lambda.Runtime.PYTHON_3_11,
            handler="process_question.handler",
            code=_lambda.Code.from_asset("../lambdas"),
            role=lambda_role,
            environment={
                "QUESTIONS_TABLE": questions_table.table_name,
                "NOTIFY_TOPIC": notify_response_topic.topic_arn
            },
            timeout=Duration.seconds(30),
            memory_size=256,
            architecture=_lambda.Architecture.ARM_64
        )

        notify_user_lambda = _lambda.Function(
            self, "NotifyUserFunction",
            runtime=_lambda.Runtime.PYTHON_3_11,
            handler="notify_user.handler",
            code=_lambda.Code.from_asset("../lambdas"),
            role=lambda_role,
            environment={
                "QUESTIONS_TABLE": questions_table.table_name
            },
            timeout=Duration.seconds(30),
            memory_size=256,
            architecture=_lambda.Architecture.ARM_64
        )

        # API Gateway
        api = apigateway.RestApi(
            self, "DesafioToroApi",
            rest_api_name="Desafio Toro API",
            description="API para o Desafio Toro",
            default_cors_preflight_options=apigateway.CorsOptions(
                allow_origins=apigateway.Cors.ALL_ORIGINS,
                allow_methods=apigateway.Cors.ALL_METHODS,
                allow_headers=apigateway.Cors.DEFAULT_HEADERS
            )
        )

        questions = api.root.add_resource("questions")
        questions.add_method(
            "POST",
            LambdaIntegration(process_question_lambda)
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
