# LLM-Based Emotion Analysis for Real-Time Call Analysis

## Overview

The real-time call analysis now uses AWS Bedrock LLM (Claude 3 Haiku) for sophisticated emotion detection instead of hardcoded keyword matching. This provides much more accurate and nuanced emotion analysis.

## Features

### 🤖 AI-Powered Emotion Detection
- **LLM Analysis**: Uses Claude 3 Haiku for natural language understanding
- **Comprehensive Emotions**: 30+ emotion categories including complex emotions
- **Context Awareness**: Understands context and nuance in speech
- **Confidence Scoring**: Provides confidence levels for each emotion detection
- **Reasoning**: Explains why a particular emotion was chosen

### 🔄 Fallback System
- **Graceful Degradation**: Falls back to keyword analysis if LLM fails
- **Reliability**: Ensures system continues working even with LLM issues
- **Hybrid Approach**: Combines AI accuracy with system reliability

## Emotion Categories

### Positive Emotions
- **happy**: joy, cheerful, delighted, pleased, glad, content, satisfied
- **excited**: thrilled, enthusiastic, eager, energetic, pumped, stoked
- **calm**: peaceful, relaxed, serene, quiet, tranquil, composed
- **confident**: assured, certain, sure, positive, optimistic, hopeful
- **focused**: concentrated, attentive, mindful, present, engaged
- **curious**: interested, intrigued, fascinated, wondering, exploring
- **grateful**: thankful, appreciative, blessed, fortunate, lucky
- **inspired**: motivated, encouraged, uplifted, energized, empowered
- **proud**: accomplished, satisfied, achieved, successful, triumphant
- **relieved**: reassured, comforted, soothed, calmed, eased
- **amused**: entertained, delighted, charmed, tickled, pleased

### Negative Emotions
- **angry**: mad, furious, irritated, annoyed, frustrated, upset, outraged
- **sad**: sorrowful, depressed, melancholy, down, blue, gloomy, miserable
- **anxious**: worried, nervous, concerned, stressed, tense, uneasy, fearful
- **frustrated**: irritated, annoyed, bothered, exasperated, fed up
- **confused**: puzzled, perplexed, bewildered, uncertain, unsure, doubtful
- **disappointed**: let down, dissatisfied, unhappy, displeased, discontent
- **embarrassed**: ashamed, humiliated, mortified, self-conscious, awkward
- **lonely**: alone, isolated, abandoned, neglected, forgotten, left out
- **overwhelmed**: stressed, burdened, swamped, drowned, crushed, exhausted
- **scared**: afraid, frightened, terrified, petrified, horrified, alarmed
- **jealous**: envious, covetous, resentful, bitter, spiteful
- **guilty**: remorseful, regretful, sorry, apologetic, blameworthy

### Complex/Neutral Emotions
- **surprised**: shocked, astonished, amazed, stunned, bewildered
- **bored**: uninterested, disengaged, unmotivated, apathetic, indifferent
- **tired**: exhausted, fatigued, weary, drained, worn out, sleepy
- **impatient**: restless, eager, hurried, rushed, pressed for time
- **suspicious**: doubtful, skeptical, distrustful, wary, cautious
- **determined**: resolved, committed, dedicated, persistent, steadfast
- **neutral**: okay, fine, normal, usual, standard, average, balanced

## Technical Implementation

### LLM Prompt Engineering
```python
prompt = f"""Analyze the emotional content of the following text and identify the primary emotion being expressed.

Text: "{text}"

Please identify the primary emotion from this comprehensive list:
[comprehensive emotion list]

Respond with a JSON object containing:
1. primary_emotion: the most dominant emotion (single word from the list above)
2. confidence: confidence level from 0.0 to 1.0
3. reasoning: brief explanation of why this emotion was chosen

Respond only with valid JSON:"""
```

### AWS Bedrock Configuration
- **Model**: `anthropic.claude-3-haiku-20240307-v1:0`
- **Max Tokens**: 300
- **Temperature**: 0.3 (balanced creativity and consistency)
- **Top P**: 0.9
- **Region**: us-east-1

### Response Processing
```python
# Extract JSON from LLM response
json_match = re.search(r'\{.*\}', llm_output, re.DOTALL)
if json_match:
    emotion_result = json.loads(json_match.group())
    
    primary_emotion = emotion_result.get('primary_emotion', 'neutral')
    confidence = emotion_result.get('confidence', 0.5)
    reasoning = emotion_result.get('reasoning', '')
    
    # Validate emotion is from our list
    if primary_emotion not in valid_emotions:
        primary_emotion = 'neutral'
        confidence = 0.5
```

## Fallback System

### When LLM Fails
1. **API Errors**: Network issues, Bedrock service problems
2. **Parsing Errors**: Invalid JSON responses from LLM
3. **Invalid Emotions**: Emotions not in the approved list
4. **Timeout Issues**: Lambda timeout during LLM call

### Fallback Analysis
- **Keyword Matching**: Comprehensive keyword-based emotion detection
- **Same Emotion Categories**: Maintains consistency with LLM analysis
- **Confidence Scoring**: Provides confidence levels for fallback results
- **Seamless Transition**: Users don't notice the fallback

## Performance Characteristics

### Response Time
- **LLM Analysis**: ~500-1500ms (depending on text length)
- **Fallback Analysis**: ~50-100ms
- **Total Processing**: ~600-2000ms per audio chunk

### Accuracy Improvements
- **Context Understanding**: Better understanding of sarcasm and nuance
- **Complex Emotions**: Detection of subtle emotional states
- **Confidence Scoring**: More accurate confidence levels
- **Reasoning**: Explanations for emotion choices

### Cost Considerations
- **Bedrock Pricing**: ~$0.001-0.003 per emotion analysis
- **Token Usage**: ~100-300 tokens per analysis
- **Monthly Cost**: ~$10-30 for 1000-10000 analyses

## Error Handling

### LLM Failures
```python
try:
    response = bedrock.invoke_model(...)
    # Process response
except Exception as e:
    logger.error(f"❌ LLM emotion analysis failed: {str(e)}")
    return fallback_emotion_analysis(text)
```

### Validation
- **Emotion Validation**: Ensures detected emotions are from approved list
- **Confidence Clamping**: Keeps confidence scores within 0.1-0.95 range
- **JSON Parsing**: Robust parsing with regex fallback
- **Response Structure**: Validates required fields are present

## Monitoring & Debugging

### CloudWatch Logs
- **LLM Responses**: Logs first 200 characters of LLM responses
- **Emotion Results**: Logs detected emotion and confidence
- **Reasoning**: Logs LLM reasoning when available
- **Fallback Usage**: Logs when fallback analysis is used

### Debug Information
```json
{
    "emotion": "frustrated",
    "emotion_confidence": 0.85,
    "reasoning": "The text contains expressions of irritation and annoyance",
    "llm_analyzed": true,
    "processing_time_ms": 1200
}
```

## Example Usage

### Input Text
```
"I'm really frustrated with this situation. I've been trying to resolve this issue for days and nothing seems to work."
```

### LLM Analysis
```json
{
    "primary_emotion": "frustrated",
    "confidence": 0.92,
    "reasoning": "The speaker expresses clear frustration through words like 'frustrated' and describes ongoing difficulties that haven't been resolved, indicating a build-up of irritation and annoyance."
}
```

### Fallback Analysis
```json
{
    "primary_emotion": "frustrated",
    "confidence": 0.73,
    "llm_analyzed": false
}
```

## Benefits

### Accuracy
- **Context Awareness**: Understands emotional context beyond keywords
- **Nuance Detection**: Recognizes sarcasm, irony, and subtle emotions
- **Confidence Scoring**: More accurate confidence levels
- **Reasoning**: Provides explanations for emotion choices

### User Experience
- **Real-time Analysis**: Fast emotion detection during calls
- **Comprehensive Emotions**: Wide range of emotional states
- **Reliable System**: Fallback ensures continuous operation
- **Detailed Insights**: Reasoning helps understand emotion detection

### Developer Experience
- **Maintainable**: No need to maintain keyword lists
- **Scalable**: Easy to add new emotions or modify analysis
- **Debuggable**: Clear logging and reasoning
- **Flexible**: Can adjust prompts for different use cases

## Future Enhancements

### Planned Improvements
- **Multi-Emotion Detection**: Identify multiple emotions in single text
- **Emotion Intensity**: Measure emotion strength beyond confidence
- **Context History**: Consider previous emotions in conversation
- **Custom Models**: Fine-tune models for specific domains

### Advanced Features
- **Emotion Trends**: Track emotion changes over time
- **Speaker Identification**: Different emotions for different speakers
- **Cultural Adaptation**: Adjust for cultural emotion expressions
- **Real-time Learning**: Improve accuracy based on user feedback

---

**Note**: The LLM-based emotion analysis provides significantly more accurate and nuanced emotion detection while maintaining system reliability through comprehensive fallback mechanisms. 