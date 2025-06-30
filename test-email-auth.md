# Email Authentication Test Guide

## Overview
The MindBridge application now uses email-based authentication instead of random user IDs. This ensures users always get their own data consistently.

## Test Steps

### 1. Access the Application
- Open: https://d8zwp3hg28702.cloudfront.net
- You should see the email authentication screen

### 2. Sign In with Email
- Enter a valid email address (e.g., `test@example.com`)
- Click "Sign In"
- You should be redirected to the main application

### 3. Verify User Identification
- Check the header - your email should be displayed
- The email is used as the user identifier for all operations

### 4. Test Mental Health Check-in
- Go to the "Wellness" tab
- Complete a mental health check-in
- The data will be stored with your email as the user ID

### 5. Test Emotion Analytics
- Go to the "Emotion Analytics" tab
- Your check-in data should be retrieved using your email
- Data should persist between sessions

### 6. Test Sign Out
- Click the "Sign Out" button in the header
- You should be redirected back to the authentication screen
- Your email should be cleared from localStorage

### 7. Test Data Persistence
- Sign in again with the same email
- Your previous check-in data should still be available
- Sign in with a different email - you should see different data

## Expected Behavior

### ✅ Success Cases
- Email validation works correctly
- User data is consistently linked to email
- Data persists between sessions
- Sign out clears authentication
- Different emails show different data

### ❌ Error Cases
- Invalid email format shows error message
- Empty email shows validation error
- Network errors are handled gracefully

## Technical Implementation

### Frontend Changes
- `EmailAuth.js` - New authentication component
- `App.js` - Integrated authentication flow
- All components updated to accept `userEmail` prop
- localStorage used for session persistence

### Backend Integration
- Check-in data stored with email as user_id
- Emotion analytics retrieves data by email
- All API calls use email instead of random user IDs

### Data Flow
1. User enters email → EmailAuth component
2. Email stored in localStorage → App.js state
3. Email passed to all components as prop
4. API calls use email as user_id
5. Data stored/retrieved using email identifier

## Troubleshooting

### Common Issues
1. **Email not showing in header**: Check localStorage for `mindbridge_user_email`
2. **Data not persisting**: Verify email is being used as user_id in API calls
3. **Authentication not working**: Clear localStorage and try again
4. **CORS errors**: Check API Gateway configuration

### Debug Commands
```javascript
// Check localStorage
localStorage.getItem('mindbridge_user_email')

// Clear authentication
localStorage.removeItem('mindbridge_user_email')

// Check API calls in browser console
// Look for user_id parameter in requests
```

## Next Steps
1. Test with real users
2. Add password authentication if needed
3. Implement email verification
4. Add user profile management
5. Implement data export functionality 