#!/usr/bin/env python3
"""
MindBridge AI - AWS CDK Infrastructure Stack (Python)
"""

from aws_cdk import (
    Stack,
    aws_lambda as _lambda,
    aws_apigateway as apigateway,
    aws_dynamodb as dynamodb,
    aws_s3 as s3,
    aws_iam as iam,
    aws_logs as logs,
    Duration,
    RemovalPolicy,
    CfnOutput,
    Tags,
)
from constructs import Construct


class MindBridgeStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Environment configuration
        environment = self.node.try_get_context("environment") or "development"
        stage = "prod" if environment == "production" else "dev"

        # ==============================================
        # STORAGE LAYER
        # ==============================================

        # DynamoDB table for emotions data
        emotions_table = dynamodb.Table(
            self, "EmotionsTable",
            table_name=f"mindbridge-emotions-{stage}",
            partition_key=dynamodb.Attribute(
                name="user_id", 
                type=dynamodb.AttributeType.STRING
            ),
            sort_key=dynamodb.Attribute(
                name="timestamp", 
                type=dynamodb.AttributeType.STRING
            ),
            billing_mode=dynamodb.BillingMode.PAY_PER_REQUEST,
            time_to_live_attribute="ttl",
            point_in_time_recovery=environment == "production",
            removal_policy=RemovalPolicy.RETAIN if environment == "production" else RemovalPolicy.DESTROY,
        )

        # Add GSI for session-based queries
        emotions_table.add_global_secondary_index(
            index_name="session-index",
            partition_key=dynamodb.Attribute(
                name="session_id", 
                type=dynamodb.AttributeType.STRING
            ),
            sort_key=dynamodb.Attribute(
                name="timestamp", 
                type=dynamodb.AttributeType.STRING
            ),
        )

        # DynamoDB table for user profiles
        users_table = dynamodb.Table(
            self, "UsersTable",
            table_name=f"mindbridge-users-{stage}",
            partition_key=dynamodb.Attribute(
                name="user_id", 
                type=dynamodb.AttributeType.STRING
            ),
            billing_mode=dynamodb.BillingMode.PAY_PER_REQUEST,
            point_in_time_recovery=environment == "production",
            removal_policy=RemovalPolicy.RETAIN if environment == "production" else RemovalPolicy.DESTROY,
        )

        # S3 bucket for temporary audio/video storage
        media_bucket = s3.Bucket(
            self, "MediaBucket",
            bucket_name=f"mindbridge-media-{stage}-{self.account}",
            lifecycle_rules=[
                s3.LifecycleRule(
                    id="DeleteOldMedia",
                    expiration=Duration.days(7),  # Auto-delete after 7 days
                    abort_incomplete_multipart_upload_after=Duration.days(1),
                ),
            ],
            public_read_access=False,
            block_public_access=s3.BlockPublicAccess.BLOCK_ALL,
            encryption=s3.BucketEncryption.S3_MANAGED,
            removal_policy=RemovalPolicy.DESTROY,
        )

        # ==============================================
        # IAM ROLES AND POLICIES
        # ==============================================

        # Common Lambda execution role with necessary permissions
        lambda_role = iam.Role(
            self, "LambdaExecutionRole",
            assumed_by=iam.ServicePrincipal("lambda.amazonaws.com"),
            managed_policies=[
                iam.ManagedPolicy.from_aws_managed_policy_name(
                    "service-role/AWSLambdaBasicExecutionRole"
                ),
            ],
            inline_policies={
                "EmotionAnalysisPolicy": iam.PolicyDocument(
                    statements=[
                        # DynamoDB permissions
                        iam.PolicyStatement(
                            effect=iam.Effect.ALLOW,
                            actions=[
                                "dynamodb:PutItem",
                                "dynamodb:GetItem",
                                "dynamodb:Query",
                                "dynamodb:Scan",
                                "dynamodb:UpdateItem",
                                "dynamodb:DeleteItem",
                            ],
                            resources=[
                                emotions_table.table_arn,
                                f"{emotions_table.table_arn}/index/*",
                                users_table.table_arn,
                            ],
                        ),
                        # Rekognition permissions
                        iam.PolicyStatement(
                            effect=iam.Effect.ALLOW,
                            actions=[
                                "rekognition:DetectFaces",
                                "rekognition:RecognizeCelebrities",
                                "rekognition:DetectModerationLabels",
                            ],
                            resources=["*"],
                        ),
                        # Transcribe permissions
                        iam.PolicyStatement(
                            effect=iam.Effect.ALLOW,
                            actions=[
                                "transcribe:StartTranscriptionJob",
                                "transcribe:GetTranscriptionJob",
                                "transcribe:StartStreamTranscription",
                            ],
                            resources=["*"],
                        ),
                        # Comprehend permissions
                        iam.PolicyStatement(
                            effect=iam.Effect.ALLOW,
                            actions=[
                                "comprehend:DetectSentiment",
                                "comprehend:DetectEntities",
                                "comprehend:DetectKeyPhrases",
                            ],
                            resources=["*"],
                        ),
                        # Bedrock permissions
                        iam.PolicyStatement(
                            effect=iam.Effect.ALLOW,
                            actions=[
                                "bedrock:InvokeModel",
                                "bedrock:InvokeModelWithResponseStream",
                            ],
                            resources=[
                                f"arn:aws:bedrock:{self.region}::foundation-model/anthropic.claude-3-sonnet-20240229-v1:0",
                            ],
                        ),
                        # S3 permissions
                        iam.PolicyStatement(
                            effect=iam.Effect.ALLOW,
                            actions=[
                                "s3:GetObject",
                                "s3:PutObject",
                                "s3:DeleteObject",
                            ],
                            resources=[f"{media_bucket.bucket_arn}/*"],
                        ),
                    ],
                ),
            },
        )

        # ==============================================
        # LAMBDA FUNCTIONS
        # ==============================================

        # Video Analysis Lambda
        video_analysis_lambda = _lambda.Function(
            self, "VideoAnalysisLambda",
            function_name=f"mindbridge-video-analysis-{stage}",
            runtime=_lambda.Runtime.PYTHON_3_9,
            handler="handler.lambda_handler",
            code=_lambda.Code.from_asset("../lambda_functions/video_analysis"),
            timeout=Duration.seconds(30),
            memory_size=1024,
            role=lambda_role,
            environment={
                "EMOTIONS_TABLE": emotions_table.table_name,
                "STAGE": stage,
            },
            log_retention=logs.RetentionDays.ONE_WEEK,
        )

        # Audio Analysis Lambda
        audio_analysis_lambda = _lambda.Function(
            self, "AudioAnalysisLambda",
            function_name=f"mindbridge-audio-analysis-{stage}",
            runtime=_lambda.Runtime.PYTHON_3_9,
            handler="handler.lambda_handler",
            code=_lambda.Code.from_asset("../lambda_functions/audio_analysis"),
            timeout=Duration.seconds(30),
            memory_size=1024,
            role=lambda_role,
            environment={
                "EMOTIONS_TABLE": emotions_table.table_name,
                "AUDIO_BUCKET": media_bucket.bucket_name,
                "STAGE": stage,
            },
            log_retention=logs.RetentionDays.ONE_WEEK,
        )

        # Emotion Fusion Lambda
        emotion_fusion_lambda = _lambda.Function(
            self, "EmotionFusionLambda",
            function_name=f"mindbridge-emotion-fusion-{stage}",
            runtime=_lambda.Runtime.PYTHON_3_9,
            handler="handler.lambda_handler",
            code=_lambda.Code.from_asset("../lambda_functions/emotion_fusion"),
            timeout=Duration.minutes(2),
            memory_size=1024,
            role=lambda_role,
            environment={
                "EMOTIONS_TABLE": emotions_table.table_name,
                "STAGE": stage,
            },
            log_retention=logs.RetentionDays.ONE_WEEK,
        )

        # Dashboard Lambda
        dashboard_lambda = _lambda.Function(
            self, "DashboardLambda",
            function_name=f"mindbridge-dashboard-{stage}",
            runtime=_lambda.Runtime.PYTHON_3_9,
            handler="handler.lambda_handler",
            code=_lambda.Code.from_asset("../lambda_functions/dashboard"),
            timeout=Duration.seconds(30),
            memory_size=512,
            role=lambda_role,
            environment={
                "EMOTIONS_TABLE": emotions_table.table_name,
                "STAGE": stage,
            },
            log_retention=logs.RetentionDays.ONE_WEEK,
        )

        # ==============================================
        # API GATEWAY
        # ==============================================

        # REST API for HTTP endpoints
        rest_api = apigateway.RestApi(
            self, "MindBridgeApi",
            rest_api_name=f"mindbridge-api-{stage}",
            description="MindBridge AI REST API",
            default_cors_preflight_options=apigateway.CorsOptions(
                allow_origins=apigateway.Cors.ALL_ORIGINS,
                allow_methods=apigateway.Cors.ALL_METHODS,
                allow_headers=apigateway.Cors.DEFAULT_HEADERS,
            ),
        )

        # Add API resources and methods
        video_resource = rest_api.root.add_resource("video-analysis")
        video_resource.add_method("POST", apigateway.LambdaIntegration(video_analysis_lambda))

        audio_resource = rest_api.root.add_resource("audio-analysis")
        audio_resource.add_method("POST", apigateway.LambdaIntegration(audio_analysis_lambda))

        fusion_resource = rest_api.root.add_resource("emotion-fusion")
        fusion_resource.add_method("POST", apigateway.LambdaIntegration(emotion_fusion_lambda))

        dashboard_resource = rest_api.root.add_resource("dashboard")
        dashboard_resource.add_method("GET", apigateway.LambdaIntegration(dashboard_lambda))
        dashboard_resource.add_method("POST", apigateway.LambdaIntegration(dashboard_lambda))

        health_resource = rest_api.root.add_resource("health")
        health_resource.add_method("GET", apigateway.LambdaIntegration(dashboard_lambda))

        # ==============================================
        # OUTPUTS
        # ==============================================

        # Output important resource information
        CfnOutput(
            self, "ApiURL",
            value=rest_api.url,
            description="REST API endpoint for MindBridge AI",
            export_name=f"MindBridge-ApiURL-{stage}",
        )

        CfnOutput(
            self, "EmotionsTableName",
            value=emotions_table.table_name,
            description="DynamoDB table name for emotions data",
            export_name=f"MindBridge-EmotionsTable-{stage}",
        )

        CfnOutput(
            self, "MediaBucketName",
            value=media_bucket.bucket_name,
            description="S3 bucket name for temporary media storage",
            export_name=f"MindBridge-MediaBucket-{stage}",
        )

        # ==============================================
        # TAGS
        # ==============================================

        # Tag all resources
        Tags.of(self).add("Project", "MindBridge")
        Tags.of(self).add("Environment", environment)
        Tags.of(self).add("Stage", stage) 