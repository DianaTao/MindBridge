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
    aws_s3_notifications as s3n,
    aws_iam as iam,
    aws_logs as logs,
    Duration,
    RemovalPolicy,
    CfnOutput,
    Tags,
    App,
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

        # DynamoDB table for call reviews
        call_reviews_table = dynamodb.Table(
            self, "CallReviewsTable",
            table_name=f"mindbridge-call-reviews-{stage}",
            partition_key=dynamodb.Attribute(
                name="call_id", 
                type=dynamodb.AttributeType.STRING
            ),
            billing_mode=dynamodb.BillingMode.PAY_PER_REQUEST,
            time_to_live_attribute="ttl",
            point_in_time_recovery=environment == "production",
            removal_policy=RemovalPolicy.RETAIN if environment == "production" else RemovalPolicy.DESTROY,
        )

        # Add GSI for agent-based queries
        call_reviews_table.add_global_secondary_index(
            index_name="agent-index",
            partition_key=dynamodb.Attribute(
                name="agent_id", 
                type=dynamodb.AttributeType.STRING
            ),
            sort_key=dynamodb.Attribute(
                name="timestamp", 
                type=dynamodb.AttributeType.STRING
            ),
        )

        # Add GSI for call type queries
        call_reviews_table.add_global_secondary_index(
            index_name="call-type-index",
            partition_key=dynamodb.Attribute(
                name="call_type", 
                type=dynamodb.AttributeType.STRING
            ),
            sort_key=dynamodb.Attribute(
                name="timestamp", 
                type=dynamodb.AttributeType.STRING
            ),
        )

        # DynamoDB table for mental health check-ins
        checkins_table = dynamodb.Table(
            self, "CheckinsTable",
            table_name=f"mindbridge-checkins-{stage}",
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
        checkins_table.add_global_secondary_index(
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

        # S3 bucket for call recordings
        call_recordings_bucket = s3.Bucket(
            self, "CallRecordingsBucket",
            bucket_name=f"mindbridge-call-recordings-{stage}-{self.account}",
            lifecycle_rules=[
                s3.LifecycleRule(
                    id="DeleteOldRecordings",
                    expiration=Duration.days(90),  # Keep recordings for 90 days
                    abort_incomplete_multipart_upload_after=Duration.days(1),
                ),
            ],
            public_read_access=False,
            block_public_access=s3.BlockPublicAccess.BLOCK_ALL,
            encryption=s3.BucketEncryption.S3_MANAGED,
            removal_policy=RemovalPolicy.DESTROY,
        )

        # S3 bucket for real-time audio chunks
        audio_chunks_bucket = s3.Bucket(
            self, "AudioChunksBucket",
            bucket_name=f"mindbridge-audio-chunks-{stage}-{self.account}",
            lifecycle_rules=[
                s3.LifecycleRule(
                    id="DeleteOldChunks",
                    expiration=Duration.days(1),  # Auto-delete chunks after 1 day
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
                                call_reviews_table.table_arn,
                                f"{call_reviews_table.table_arn}/index/*",
                                checkins_table.table_arn,
                                f"{checkins_table.table_arn}/index/*",
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
                                f"arn:aws:bedrock:{self.region}::foundation-model/anthropic.claude-3-haiku-20240307-v1:0",
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
                            resources=[
                                f"{media_bucket.bucket_arn}/*",
                                f"{call_recordings_bucket.bucket_arn}/*",
                                f"{audio_chunks_bucket.bucket_arn}/*",
                            ],
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

        # Text Analysis Lambda
        text_analysis_lambda = _lambda.Function(
            self, "TextAnalysisLambda",
            function_name=f"mindbridge-text-analysis-{stage}",
            runtime=_lambda.Runtime.PYTHON_3_9,
            handler="handler.lambda_handler",
            code=_lambda.Code.from_asset("../lambda_functions/text_analysis"),
            timeout=Duration.seconds(30),
            memory_size=512,
            role=lambda_role,
            environment={
                "EMOTIONS_TABLE": emotions_table.table_name,
                "STAGE": stage,
                "FUSION_LAMBDA_ARN": emotion_fusion_lambda.function_arn,
                "BEDROCK_MODEL_ID": "anthropic.claude-3-haiku-20240307-v1:0",
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

        # Health Check Lambda
        health_check_lambda = _lambda.Function(
            self, "HealthCheckLambda",
            function_name=f"mindbridge-health-check-{stage}",
            runtime=_lambda.Runtime.PYTHON_3_9,
            handler="handler.lambda_handler",
            code=_lambda.Code.from_asset("../lambda_functions/health_check"),
            timeout=Duration.seconds(10),
            memory_size=128,
            role=lambda_role,
            environment={
                "STAGE": stage,
            },
            log_retention=logs.RetentionDays.ONE_WEEK,
        )

        # Call Review Lambda
        call_review_lambda = _lambda.Function(
            self, "CallReviewLambda",
            function_name=f"mindbridge-call-review-{stage}",
            runtime=_lambda.Runtime.PYTHON_3_9,
            handler="handler.lambda_handler",
            code=_lambda.Code.from_asset("../lambda_functions/call_review"),
            timeout=Duration.minutes(5),  # Longer timeout for transcription
            memory_size=1024,
            role=lambda_role,
            environment={
                "CALL_REVIEW_TABLE": call_reviews_table.table_name,
                "CALL_AUDIO_BUCKET": call_recordings_bucket.bucket_name,
                "STAGE": stage,
            },
            log_retention=logs.RetentionDays.ONE_WEEK,
        )

        # Automated Call Processing Lambda (triggered by S3 events)
        call_processor_lambda = _lambda.Function(
            self, "CallProcessorLambda",
            function_name=f"mindbridge-call-processor-{stage}",
            runtime=_lambda.Runtime.PYTHON_3_9,
            handler="handler.lambda_handler",
            code=_lambda.Code.from_asset("../lambda_functions/call_review_processor"),
            timeout=Duration.minutes(10),  # Longer timeout for transcription and analysis
            memory_size=2048,
            role=lambda_role,
            environment={
                "CALL_REVIEWS_TABLE": call_reviews_table.table_name,
                "EMOTIONS_TABLE": emotions_table.table_name,
                "CALL_AUDIO_BUCKET": call_recordings_bucket.bucket_name,
                "STAGE": stage,
            },
            log_retention=logs.RetentionDays.ONE_WEEK,
        )

        # Real-Time Call Analysis Lambda
        realtime_call_analysis_lambda = _lambda.Function(
            self, "RealtimeCallAnalysisLambda",
            function_name=f"mindbridge-realtime-call-analysis-{stage}",
            runtime=_lambda.Runtime.PYTHON_3_9,
            handler="handler.lambda_handler",
            code=_lambda.Code.from_asset("../lambda_functions/realtime_call_analysis"),
            timeout=Duration.seconds(60),  # 60 seconds for real-time processing
            memory_size=1024,
            role=lambda_role,
            environment={
                "EMOTIONS_TABLE": emotions_table.table_name,
                "CALL_ANALYSIS_TABLE": call_reviews_table.table_name,
                "AUDIO_BUCKET": audio_chunks_bucket.bucket_name,
                "STAGE": stage,
            },
            log_retention=logs.RetentionDays.ONE_WEEK,
        )

        # Check-in Processor Lambda
        checkin_processor_lambda = _lambda.Function(
            self, "CheckinProcessorLambda",
            function_name=f"mindbridge-checkin-processor-{stage}",
            runtime=_lambda.Runtime.PYTHON_3_9,
            handler="handler.lambda_handler",
            code=_lambda.Code.from_asset("../lambda_functions/checkin_processor"),
            timeout=Duration.seconds(30),
            memory_size=512,
            role=lambda_role,
            environment={
                "CHECKINS_TABLE": f"mindbridge-checkins-{stage}",
                "BEDROCK_MODEL_ID": "anthropic.claude-3-sonnet-20240229-v1:0",
                "STAGE": stage,
            },
            log_retention=logs.RetentionDays.ONE_WEEK,
        )

        # Check-in Retriever Lambda
        checkin_retriever_lambda = _lambda.Function(
            self, "CheckinRetrieverLambda",
            function_name=f"mindbridge-checkin-retriever-{stage}",
            runtime=_lambda.Runtime.PYTHON_3_9,
            handler="handler.lambda_handler",
            code=_lambda.Code.from_asset("../lambda_functions/checkin_retriever"),
            timeout=Duration.seconds(30),
            memory_size=512,
            role=lambda_role,
            environment={
                "CHECKINS_TABLE": f"mindbridge-checkins-{stage}",
                "BEDROCK_MODEL_ID": "anthropic.claude-3-sonnet-20240229-v1:0",
                "STAGE": stage,
            },
            log_retention=logs.RetentionDays.ONE_WEEK,
        )

        # HR Wellness Data Lambda
        hr_wellness_data_lambda = _lambda.Function(
            self, "HRWellnessDataLambda",
            function_name=f"mindbridge-hr-wellness-data-{stage}",
            runtime=_lambda.Runtime.PYTHON_3_9,
            handler="handler.lambda_handler",
            code=_lambda.Code.from_asset("../lambda_functions/hr_wellness_data"),
            timeout=Duration.seconds(60),  # Longer timeout for data aggregation
            memory_size=1024,
            role=lambda_role,
            environment={
                "CHECKINS_TABLE": f"mindbridge-checkins-{stage}",
                "USERS_TABLE": f"mindbridge-users-{stage}",
                "STAGE": stage,
            },
            log_retention=logs.RetentionDays.ONE_WEEK,
        )

        # ==============================================
        # API GATEWAY
        # ==============================================

        # REST API for HTTP endpoints with enhanced CORS configuration
        rest_api = apigateway.RestApi(
            self, "MindBridgeApi",
            rest_api_name=f"mindbridge-api-{stage}",
            description="MindBridge AI REST API",
            default_cors_preflight_options=apigateway.CorsOptions(
                allow_origins=["*"],  # Allow all origins for now
                allow_methods=apigateway.Cors.ALL_METHODS,
                allow_headers=[
                    "Content-Type",
                    "Authorization",
                    "X-Amz-Date",
                    "X-Api-Key",
                    "X-Amz-Security-Token",
                    "X-Amz-User-Agent",
                    "X-Requested-With"
                ],
                allow_credentials=True,
                max_age=Duration.seconds(300),
            ),
        )

        # Create Lambda integrations (CORS headers must be set in Lambda response)
        def create_lambda_integration(lambda_function):
            return apigateway.LambdaIntegration(
                lambda_function,
                request_templates={"application/json": '{ "statusCode": "200" }'}
            )

        # Add API resources and methods
        video_resource = rest_api.root.add_resource("video-analysis")
        video_resource.add_method("POST", create_lambda_integration(video_analysis_lambda))

        # Add stop endpoint for video analysis
        video_stop_resource = video_resource.add_resource("stop")
        video_stop_resource.add_method("POST", create_lambda_integration(video_analysis_lambda))

        text_resource = rest_api.root.add_resource("text-analysis")
        text_resource.add_method("POST", create_lambda_integration(text_analysis_lambda))

        fusion_resource = rest_api.root.add_resource("emotion-fusion")
        fusion_resource.add_method("POST", create_lambda_integration(emotion_fusion_lambda))

        dashboard_resource = rest_api.root.add_resource("dashboard")
        dashboard_resource.add_method("GET", create_lambda_integration(dashboard_lambda))
        dashboard_resource.add_method("POST", create_lambda_integration(dashboard_lambda))

        health_resource = rest_api.root.add_resource("health")
        health_resource.add_method("GET", create_lambda_integration(health_check_lambda))

        # Call Review endpoint
        call_review_resource = rest_api.root.add_resource("call-review")
        call_review_resource.add_method("POST", create_lambda_integration(call_review_lambda))

        # Real-Time Call Analysis endpoint
        realtime_call_analysis_resource = rest_api.root.add_resource("realtime-call-analysis")
        realtime_call_analysis_resource.add_method("POST", create_lambda_integration(realtime_call_analysis_lambda))

        # Check-in Processor endpoint
        checkin_processor_resource = rest_api.root.add_resource("checkin-processor")
        checkin_processor_resource.add_method("POST", create_lambda_integration(checkin_processor_lambda))

        # Check-in Retriever endpoint
        checkin_retriever_resource = rest_api.root.add_resource("checkin-retriever")
        checkin_retriever_resource.add_method("GET", create_lambda_integration(checkin_retriever_lambda))
        checkin_retriever_resource.add_method("POST", create_lambda_integration(checkin_retriever_lambda))

        # HR Wellness Data endpoint
        hr_wellness_data_resource = rest_api.root.add_resource("hr-wellness-data")
        hr_wellness_data_resource.add_method("GET", create_lambda_integration(hr_wellness_data_lambda))

        # Add root endpoint
        rest_api.root.add_method("GET", create_lambda_integration(dashboard_lambda))

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

        CfnOutput(
            self, "CallReviewsTableName",
            value=call_reviews_table.table_name,
            description="DynamoDB table name for call reviews data",
            export_name=f"MindBridge-CallReviewsTable-{stage}",
        )

        CfnOutput(
            self, "CallRecordingsBucketName",
            value=call_recordings_bucket.bucket_name,
            description="S3 bucket name for call recordings storage",
            export_name=f"MindBridge-CallRecordingsBucket-{stage}",
        )

        CfnOutput(
            self, "AudioChunksBucketName",
            value=audio_chunks_bucket.bucket_name,
            description="S3 bucket name for real-time audio chunks storage",
            export_name=f"MindBridge-AudioChunksBucket-{stage}",
        )

        CfnOutput(
            self, "CheckinsTableName",
            value=checkins_table.table_name,
            description="DynamoDB table name for mental health check-ins data",
            export_name=f"MindBridge-CheckinsTable-{stage}",
        )

        # ==============================================
        # TAGS
        # ==============================================

        # Tag all resources
        Tags.of(self).add("Project", "MindBridge")
        Tags.of(self).add("Environment", environment)
        Tags.of(self).add("Stage", stage) 

        # Add S3 event trigger for automated call processing
        # This triggers when new call recordings are uploaded to the incoming/ folder
        call_recordings_bucket.add_event_notification(
            s3.EventType.OBJECT_CREATED,
            s3n.LambdaDestination(call_processor_lambda),
            s3.NotificationKeyFilter(prefix="incoming/", suffix=".mp3")
        )

        # Add S3 event trigger for .wav files as well
        call_recordings_bucket.add_event_notification(
            s3.EventType.OBJECT_CREATED,
            s3n.LambdaDestination(call_processor_lambda),
            s3.NotificationKeyFilter(prefix="incoming/", suffix=".wav")
        )

app = App()
MindBridgeStack(app, "MindBridgeStack")
app.synth() 