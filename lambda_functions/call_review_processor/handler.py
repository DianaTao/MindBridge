import json
import boto3
import os
import uuid
from datetime import datetime
import logging

# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Initialize AWS clients
s3 = boto3.client('s3')
transcribe = boto3.client('transcribe')
comprehend = boto3.client('comprehend')
dynamodb = boto3.resource('dynamodb')
bedrock = boto3.client('bedrock-runtime')

# Get table references
call_reviews_table = dynamodb.Table(os.environ['CALL_REVIEWS_TABLE'])
emotions_table = dynamodb.Table(os.environ['EMOTIONS_TABLE'])

def lambda_handler(event, context):
    """
    Automated call processing triggered by S3 events
    Processes new call recordings and generates comprehensive analysis
    """
    try:
        # Extract S3 event information
        s3_event = event['Records'][0]['s3']
        bucket_name = s3_event['bucket']['name']
        object_key = s3_event['object']['key']
        
        logger.info(f"Processing call recording: s3://{bucket_name}/{object_key}")
        
        # Extract metadata from S3 key path
        # Expected format: incoming/{agentId}/{callId}.mp3
        path_parts = object_key.split('/')
        if len(path_parts) >= 3:
            agent_id = path_parts[1]
            call_id = path_parts[2].split('.')[0]
        else:
            # Fallback: generate IDs
            agent_id = "unknown_agent"
            call_id = str(uuid.uuid4())
        
        # Step 1: Start transcription with speaker identification
        transcription_job_name = f"call-review-{call_id}-{int(datetime.now().timestamp())}"
        
        transcribe_response = transcribe.start_transcription_job(
            TranscriptionJobName=transcription_job_name,
            Media={'MediaFileUri': f's3://{bucket_name}/{object_key}'},
            MediaFormat='mp3',
            LanguageCode='en-US',
            Settings={
                'ShowSpeakerLabels': True,
                'MaxSpeakerLabels': 2,  # Agent and Customer
                'ChannelIdentification': True
            },
            OutputBucketName=bucket_name,
            OutputKey=f'transcriptions/{call_id}/transcript.json'
        )
        
        # Step 2: Wait for transcription to complete (in production, use Step Functions)
        # For now, we'll process immediately and update when transcription is ready
        call_data = {
            'callId': call_id,
            'agentId': agent_id,
            'recordingUrl': f's3://{bucket_name}/{object_key}',
            'transcriptionJobName': transcription_job_name,
            'status': 'processing',
            'timestamp': datetime.now().isoformat(),
            'analysis': {
                'customerSentiment': 'analyzing',
                'agentEmpathyScore': 0.0,
                'emotionTimeline': [],
                'summary': 'Analysis in progress...',
                'keyPhrases': [],
                'qualityScore': 0.0
            }
        }
        
        # Store initial call data
        call_reviews_table.put_item(Item=call_data)
        
        # Step 3: Generate initial analysis (will be updated when transcription completes)
        initial_analysis = generate_initial_analysis(call_id, agent_id, object_key)
        
        # Update call data with initial analysis
        call_data['analysis'].update(initial_analysis)
        call_reviews_table.put_item(Item=call_data)
        
        # Step 4: Trigger async processing for detailed analysis
        # In production, this would be handled by Step Functions
        process_detailed_analysis(call_id, bucket_name, object_key, transcription_job_name)
        
        return {
            'statusCode': 200,
            'body': json.dumps({
                'message': 'Call processing initiated successfully',
                'callId': call_id,
                'agentId': agent_id,
                'status': 'processing'
            })
        }
        
    except Exception as e:
        logger.error(f"Error processing call: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps({
                'error': 'Failed to process call',
                'message': str(e)
            })
        }

def generate_initial_analysis(call_id, agent_id, object_key):
    """
    Generate initial analysis while transcription is processing
    """
    return {
        'customerSentiment': 'analyzing',
        'agentEmpathyScore': 0.0,
        'emotionTimeline': [
            {
                'time': '00:00',
                'agent': 'processing',
                'customer': 'processing',
                'note': 'Transcription in progress'
            }
        ],
        'summary': f'Call {call_id} is being processed. Agent {agent_id} will receive analysis shortly.',
        'keyPhrases': ['processing'],
        'qualityScore': 0.0,
        'processingStage': 'transcription'
    }

def process_detailed_analysis(call_id, bucket_name, object_key, transcription_job_name):
    """
    Process detailed analysis once transcription is complete
    This would typically be triggered by a Step Function or EventBridge
    """
    try:
        # Check transcription status
        job_status = transcribe.get_transcription_job(TranscriptionJobName=transcription_job_name)
        
        if job_status['TranscriptionJob']['TranscriptionJobStatus'] == 'COMPLETED':
            # Get transcription results
            transcript_uri = job_status['TranscriptionJob']['Transcript']['TranscriptFileUri']
            
            # Download and parse transcript
            transcript_data = download_and_parse_transcript(transcript_uri)
            
            # Analyze sentiment and emotions
            analysis = analyze_call_content(transcript_data)
            
            # Generate AI summary
            summary = generate_ai_summary(transcript_data, analysis)
            
            # Update call review data
            update_call_analysis(call_id, analysis, summary)
            
        else:
            # Schedule retry or use Step Functions for better orchestration
            logger.info(f"Transcription still in progress: {transcription_job_name}")
            
    except Exception as e:
        logger.error(f"Error in detailed analysis: {str(e)}")

def download_and_parse_transcript(transcript_uri):
    """
    Download and parse the transcription JSON
    """
    # This would download the transcript from S3 and parse the JSON
    # For now, return a mock structure
    return {
        'transcript': 'Mock transcript data',
        'speaker_labels': [
            {'speaker_label': 'spk_0', 'start_time': 0.0, 'end_time': 5.0, 'text': 'Hello, how can I help you?'},
            {'speaker_label': 'spk_1', 'start_time': 5.5, 'end_time': 10.0, 'text': 'I have a billing issue.'}
        ]
    }

def analyze_call_content(transcript_data):
    """
    Analyze the call content for sentiment, emotions, and key phrases
    """
    # Analyze sentiment using Comprehend
    sentiment_response = comprehend.detect_sentiment(
        Text=transcript_data['transcript'],
        LanguageCode='en'
    )
    
    # Extract key phrases
    phrases_response = comprehend.detect_key_phrases(
        Text=transcript_data['transcript'],
        LanguageCode='en'
    )
    
    # Generate emotion timeline
    emotion_timeline = generate_emotion_timeline(transcript_data['speaker_labels'])
    
    return {
        'customerSentiment': sentiment_response['Sentiment'],
        'sentimentScores': sentiment_response['SentimentScore'],
        'keyPhrases': [phrase['Text'] for phrase in phrases_response['KeyPhrases']],
        'emotionTimeline': emotion_timeline,
        'agentEmpathyScore': calculate_empathy_score(transcript_data),
        'qualityScore': calculate_quality_score(transcript_data, sentiment_response)
    }

def generate_emotion_timeline(speaker_labels):
    """
    Generate emotion timeline from speaker labels
    """
    timeline = []
    for i, segment in enumerate(speaker_labels):
        timeline.append({
            'time': f"{int(segment['start_time']//60):02d}:{int(segment['start_time']%60):02d}",
            'agent': 'calm' if segment['speaker_label'] == 'spk_0' else 'neutral',
            'customer': 'neutral' if segment['speaker_label'] == 'spk_0' else 'concerned',
            'text': segment['text'][:50] + '...' if len(segment['text']) > 50 else segment['text']
        })
    return timeline

def calculate_empathy_score(transcript_data):
    """
    Calculate empathy score based on agent responses
    """
    # This would use more sophisticated analysis
    # For now, return a mock score
    return 7.5

def calculate_quality_score(transcript_data, sentiment_response):
    """
    Calculate overall call quality score
    """
    # This would use multiple factors
    # For now, return a mock score
    return 8.2

def generate_ai_summary(transcript_data, analysis):
    """
    Generate AI-powered summary using Bedrock
    """
    try:
        prompt = f"""
        Analyze this customer service call and provide a concise summary:
        
        Transcript: {transcript_data['transcript'][:1000]}...
        
        Analysis:
        - Customer Sentiment: {analysis['customerSentiment']}
        - Key Phrases: {', '.join(analysis['keyPhrases'][:5])}
        - Agent Empathy Score: {analysis['agentEmpathyScore']}/10
        
        Provide a 2-3 sentence summary focusing on:
        1. Customer's main concern
        2. Agent's response quality
        3. Overall outcome
        """
        
        response = bedrock.invoke_model(
            modelId='anthropic.claude-3-sonnet-20240229-v1:0',
            body=json.dumps({
                'prompt': f'\n\nHuman: {prompt}\n\nAssistant:',
                'max_tokens': 300,
                'temperature': 0.7
            })
        )
        
        response_body = json.loads(response['body'].read())
        return response_body['completion'].strip()
        
    except Exception as e:
        logger.error(f"Error generating AI summary: {str(e)}")
        return "AI summary generation failed. Manual review recommended."

def update_call_analysis(call_id, analysis, summary):
    """
    Update the call analysis in DynamoDB
    """
    try:
        call_reviews_table.update_item(
            Key={'callId': call_id},
            UpdateExpression='SET analysis = :analysis, #status = :status, updatedAt = :updatedAt',
            ExpressionAttributeNames={'#status': 'status'},
            ExpressionAttributeValues={
                ':analysis': {
                    'customerSentiment': analysis['customerSentiment'],
                    'agentEmpathyScore': analysis['agentEmpathyScore'],
                    'emotionTimeline': analysis['emotionTimeline'],
                    'summary': summary,
                    'keyPhrases': analysis['keyPhrases'],
                    'qualityScore': analysis['qualityScore'],
                    'sentimentScores': analysis['sentimentScores']
                },
                ':status': 'completed',
                ':updatedAt': datetime.now().isoformat()
            }
        )
        
        logger.info(f"Call analysis updated for callId: {call_id}")
        
    except Exception as e:
        logger.error(f"Error updating call analysis: {str(e)}") 