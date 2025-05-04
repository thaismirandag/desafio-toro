from aws_cdk import App, Stack, RemovalPolicy
from aws_cdk.aws_dynamodb import Table, AttributeType, BillingMode
from aws_cdk.aws_sns import Topic, TopicSubscription, SubscriptionProtocol
from aws_cdk.aws_lambda import Function, Runtime, Code
from aws_cdk.aws_apigateway import RestApi, LambdaIntegration
from aws_cdk.aws_iam import Role, ServicePrincipal, PolicyStatement
from constructs import Construct

class DesafioToroStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        questions_table = Table(
            self, "QuestionsTable",
            table_name="questions",
            partition_key=Attribute(name="id", type=AttributeType.STRING),
            billing_mode=BillingMode.PAY_PER_REQUEST,
            removal_policy=RemovalPolicy.DESTROY  # Para ambiente de desenvolvimento
        )

        process_question_topic = Topic(
            self, "ProcessQuestionTopic",
            topic_name="process-question"
        )

        notify_response_topic = Topic(
            self, "NotifyResponseTopic",
            topic_name="notify-response"
        )

        lambda_role = Role(
            self, "LambdaRole",
            assumed_by=ServicePrincipal("lambda.amazonaws.com")
        )

        lambda_role.add_to_policy(
            PolicyStatement(
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

        lambda_role.add_to_policy(
            PolicyStatement(
                actions=[
                    "sns:Publish"
                ],
                resources=[
                    process_question_topic.topic_arn,
                    notify_response_topic.topic_arn
                ]
            )
        )

        process_question_lambda = Function(
            self, "ProcessQuestionFunction",
            runtime=Runtime.PYTHON_3_11,
            handler="app.lambdas.process_question.handler",
            code=Code.from_asset(".."),
            role=lambda_role,
            environment={
                "QUESTIONS_TABLE": questions_table.table_name,
                "NOTIFY_TOPIC": notify_response_topic.topic_arn
            }
        )

        notify_user_lambda = Function(
            self, "NotifyUserFunction",
            runtime=Runtime.PYTHON_3_11,
            handler="app.lambdas.notify_user.handler",
            code=Code.from_asset(".."),
            role=lambda_role,
            environment={
                "QUESTIONS_TABLE": questions_table.table_name
            }
        )

        api = RestApi(
            self, "DesafioToroApi",
            rest_api_name="Desafio Toro API",
            description="API para o Desafio Toro"
        )

        questions = api.root.add_resource("questions")
        questions.add_method(
            "POST",
            LambdaIntegration(process_question_lambda)
        )

        process_question_topic.add_subscription(
            TopicSubscription(
                endpoint=process_question_lambda.function_arn,
                protocol=SubscriptionProtocol.LAMBDA
            )
        )

        notify_response_topic.add_subscription(
            TopicSubscription(
                endpoint=notify_user_lambda.function_arn,
                protocol=SubscriptionProtocol.LAMBDA
            )
        )

app = App()
DesafioToroStack(app, "DesafioToroStack")
app.synth() 