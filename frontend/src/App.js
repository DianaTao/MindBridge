import React, { useState } from "react";
import CameraCapture from "./components/CameraCapture";
import TextAnalysis from "./components/TextAnalysis";
import Simple from "./components/Simple";
import AutomatedCallDashboard from "./components/AutomatedCallDashboard";
import RealTimeCallAnalysis from './components/RealTimeCallAnalysis';
import MentalHealthCheckin from './components/MentalHealthCheckin';
import EmotionAnalytics from './components/EmotionAnalytics';
import EmailAuth from './components/EmailAuth';

// UI Component replacements
const Card = ({ children, className, ...props }) => (
  <div className={className} {...props}>
    {children}
  </div>
);

const CardContent = ({ children, className, ...props }) => (
  <div className={className} {...props}>
    {children}
  </div>
);

const CardHeader = ({ children, className, ...props }) => (
  <div className={className} {...props}>
    {children}
  </div>
);

const CardTitle = ({ children, className, ...props }) => (
  <h3 className={className} {...props}>
    {children}
  </h3>
);

const Badge = ({ children, className, ...props }) => (
  <span className={className} {...props}>
    {children}
  </span>
);

const Tabs = ({ children, value, onValueChange, className, ...props }) => (
  <div className={className} {...props}>
    {children}
  </div>
);

const TabsList = ({ children, className, ...props }) => (
  <div className={className} {...props}>
    {children}
  </div>
);

const TabsTrigger = ({ children, value, className, ...props }) => (
  <button className={className} {...props}>
    {children}
  </button>
);

const TabsContent = ({ children, value, className, ...props }) => (
  <div className={className} {...props}>
    {children}
  </div>
);

// Icon components
const Video = ({ className, ...props }) => (
  <svg className={className} fill="none" stroke="currentColor" viewBox="0 0 24 24" {...props}>
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 10l4.553-2.276A1 1 0 0121 8.618v6.764a1 1 0 01-1.447.894L15 14M5 18h8a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v8a2 2 0 002 2z" />
  </svg>
);

const FileText = ({ className, ...props }) => (
  <svg className={className} fill="none" stroke="currentColor" viewBox="0 0 24 24" {...props}>
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
  </svg>
);

const BarChart3 = ({ className, ...props }) => (
  <svg className={className} fill="none" stroke="currentColor" viewBox="0 0 24 24" {...props}>
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
  </svg>
);

const Brain = ({ className, ...props }) => (
  <svg className={className} fill="none" stroke="currentColor" viewBox="0 0 24 24" {...props}>
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
  </svg>
);

const Activity = ({ className, ...props }) => (
  <svg className={className} fill="none" stroke="currentColor" viewBox="0 0 24 24" {...props}>
    <polyline points="22,12 18,12 15,21 9,3 6,12 2,12" strokeWidth={2} />
  </svg>
);

const Camera = ({ className, ...props }) => (
  <svg className={className} fill="none" stroke="currentColor" viewBox="0 0 24 24" {...props}>
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 9a2 2 0 012-2h.93a2 2 0 001.664-.89l.812-1.22A2 2 0 0110.07 4h3.86a2 2 0 011.664.89l.812 1.22A2 2 0 0018.07 7H19a2 2 0 012 2v9a2 2 0 01-2 2H5a2 2 0 01-2-2V9z" />
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 13a3 3 0 11-6 0 3 3 0 016 0z" />
  </svg>
);

const Zap = ({ className, ...props }) => (
  <svg className={className} fill="none" stroke="currentColor" viewBox="0 0 24 24" {...props}>
    <polygon points="13,2 3,14 12,14 11,22 21,10 12,10" strokeWidth={2} />
  </svg>
);

const Sparkles = ({ className, ...props }) => (
  <svg className={className} fill="none" stroke="currentColor" viewBox="0 0 24 24" {...props}>
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 3v4M3 5h4M6 17v4m-2-2h4m5-16l2.286 6.857L21 12l-5.714 2.143L13 21l-2.286-6.857L5 12l5.714-2.143L13 3z" />
  </svg>
);

const Phone = ({ className, ...props }) => (
  <svg className={className} fill="none" stroke="currentColor" viewBox="0 0 24 24" {...props}>
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 5a2 2 0 012-2h3.28a1 1 0 01.948.684l1.498 4.493a1 1 0 01-.502 1.21l-2.257 1.13a11.042 11.042 0 005.516 5.516l1.13-2.257a1 1 0 011.21-.502l4.493 1.498a1 1 0 01.684.949V19a2 2 0 01-2 2h-1C9.716 21 3 14.284 3 6V5z" />
  </svg>
);

const Heart = ({ className, ...props }) => (
  <svg className={className} fill="none" stroke="currentColor" viewBox="0 0 24 24" {...props}>
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M20.84 4.61a5.5 5.5 0 0 0-7.78 0L12 5.67l-1.06-1.06a5.5 5.5 0 0 0-7.78 7.78l1.06 1.06L12 21.23l7.78-7.78 1.06-1.06a5.5 5.5 0 0 0 0-7.78z" />
  </svg>
);

function MindBridgeApp() {
  const [activeTab, setActiveTab] = useState("video");
  const [emotionHistory, setEmotionHistory] = useState([]);
  const [isProcessing, setIsProcessing] = useState(false);
  const [userEmail, setUserEmail] = useState(null);

  const handleAuthChange = (email) => {
    setUserEmail(email);
    console.log('🔐 Authentication changed:', email ? `User: ${email}` : 'No user');
  };

  const handleEmotionDetected = (emotion, modality) => {
    const emotionData = {
      modality: modality || "unknown",
      primary_emotion: emotion.primary_emotion || emotion.emotion || "neutral",
      confidence: emotion.confidence || 0,
      timestamp: new Date().toISOString(),
      emotions: emotion.emotions || [],
      sentiment: emotion.sentiment,
      keywords: emotion.keywords,
      transcript: emotion.transcript,
    };

    setEmotionHistory((prev) => [emotionData, ...prev].slice(0, 20));
    console.log(`${modality} emotion detected:`, emotionData);
  };

  const getEmotionColor = (emotion) => {
    const colors = {
      happy: "bg-gradient-to-r from-yellow-400 to-orange-500 text-black",
      sad: "bg-gradient-to-r from-blue-400 to-indigo-600 text-white",
      angry: "bg-gradient-to-r from-red-500 to-pink-600 text-white",
      fear: "bg-gradient-to-r from-purple-500 to-violet-600 text-white",
      surprise: "bg-gradient-to-r from-orange-400 to-red-500 text-white",
      disgust: "bg-gradient-to-r from-green-400 to-emerald-600 text-white",
      neutral: "bg-gradient-to-r from-gray-400 to-slate-500 text-white",
    };
    return colors[emotion.toLowerCase()] || colors.neutral;
  };

  const recentEmotion = emotionHistory[0];

  // If user is not authenticated, show auth screen
  if (!userEmail) {
    return <EmailAuth onAuthChange={handleAuthChange} />;
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-indigo-100 relative overflow-hidden">
      {/* Artistic Background Elements */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        <div className="absolute top-1/4 left-1/4 w-96 h-96 bg-blue-200/30 rounded-full blur-3xl animate-pulse-slow" />
        <div className="absolute bottom-1/4 right-1/4 w-80 h-80 bg-indigo-200/30 rounded-full blur-3xl animate-pulse-slow delay-1000" />
        <div className="absolute top-1/2 left-1/2 w-64 h-64 bg-purple-200/30 rounded-full blur-3xl animate-pulse-slow delay-2000" />
      </div>

      {/* Floating Particles */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        {[...Array(20)].map((_, i) => (
          <div
            key={i}
            className="absolute w-1 h-1 bg-blue-300/40 rounded-full animate-float"
            style={{
              left: `${Math.random() * 100}%`,
              top: `${Math.random() * 100}%`,
              animationDelay: `${Math.random() * 5}s`,
              animationDuration: `${3 + Math.random() * 4}s`,
            }}
          />
        ))}
      </div>

      {/* Header */}
      <header className="relative z-10 bg-white/80 backdrop-blur-xl border-b border-blue-200/50 sticky top-0">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-6">
            <div className="flex items-center space-x-4">
              <div className="relative">
                <div className="w-12 h-12 bg-gradient-to-r from-blue-500 to-indigo-600 rounded-xl flex items-center justify-center shadow-lg shadow-blue-500/25">
                  <Brain className="h-7 w-7 text-white" />
                </div>
                <div className="absolute -top-1 -right-1 w-4 h-4 bg-green-400 rounded-full animate-pulse shadow-lg shadow-green-400/50" />
                <div className="absolute inset-0 bg-gradient-to-r from-blue-500 to-indigo-600 rounded-xl blur opacity-30 animate-pulse" />
              </div>
              <div>
                <h1 className="text-4xl font-bold bg-gradient-to-r from-slate-800 via-blue-700 to-indigo-700 bg-clip-text text-transparent font-['Courier_New']">
                  MindBridge
                </h1>
                <p className="text-slate-600 font-medium tracking-wide font-['Courier_New']">Multi-Modal Emotion Detection</p>
              </div>
            </div>

            <div className="flex items-center space-x-6">
              {/* User Email Display */}
              <div className="flex items-center space-x-3 bg-white/60 backdrop-blur-sm rounded-full px-4 py-2 border border-blue-200/50">
                <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse shadow-lg shadow-green-500/50" />
                <span className="text-slate-700 text-sm font-medium font-['Courier_New']">
                  {userEmail}
                </span>
              </div>

              {recentEmotion && (
                <div className="flex items-center space-x-3 bg-white/60 backdrop-blur-sm rounded-full px-4 py-2 border border-blue-200/50 animate-neural-scan">
                  <Activity className="h-4 w-4 text-green-500 animate-pulse" />
                  <Badge className={`${getEmotionColor(recentEmotion.primary_emotion)} border-0 shadow-lg text-sm px-2 py-1 font-['Courier_New']`}>
                    {recentEmotion.primary_emotion}
                  </Badge>
                  <span className="text-slate-700 text-sm font-medium font-['Courier_New']">
                    {Math.round((recentEmotion.confidence || 0) * 100)}%
                  </span>
                </div>
              )}

              {emotionHistory.length > 0 && (
                <div className="bg-gradient-to-r from-blue-100/60 to-indigo-100/60 backdrop-blur-sm rounded-full px-4 py-2 border border-blue-300/50">
                  <div className="flex items-center space-x-2">
                    <Zap className="h-4 w-4 text-blue-500" />
                    <span className="text-slate-700 font-medium font-['Courier_New']">{emotionHistory.length}</span>
                    <span className="text-slate-600 text-sm font-['Courier_New']">detections</span>
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>
      </header>

      <main className="relative z-10 max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <Tabs value={activeTab} onValueChange={setActiveTab} className="space-y-8">
          <TabsList className="grid w-full grid-cols-6 bg-white/80 backdrop-blur-xl border border-blue-200/50 rounded-2xl p-2">
            <TabsTrigger
              value="video"
              className={`flex items-center space-x-2 rounded-xl transition-all duration-300 font-['Courier_New'] ${
                activeTab === "video" ? "bg-gradient-to-r from-blue-500 to-indigo-600 text-white" : "text-slate-600 hover:text-slate-800"
              }`}
              onClick={() => setActiveTab("video")}
            >
              <Video className="h-4 w-4" />
              <span className="hidden sm:inline font-medium">Video</span>
            </TabsTrigger>
            <TabsTrigger
              value="text"
              className={`flex items-center space-x-2 rounded-xl transition-all duration-300 font-['Courier_New'] ${
                activeTab === "text" ? "bg-gradient-to-r from-blue-500 to-cyan-600 text-white" : "text-slate-600 hover:text-slate-800"
              }`}
              onClick={() => setActiveTab("text")}
            >
              <FileText className="h-4 w-4" />
              <span className="hidden sm:inline font-medium">Text</span>
            </TabsTrigger>
            <TabsTrigger
              value="simple"
              className={`flex items-center space-x-2 rounded-xl transition-all duration-300 font-['Courier_New'] ${
                activeTab === "simple" ? "bg-gradient-to-r from-indigo-500 to-purple-600 text-white" : "text-slate-600 hover:text-slate-800"
              }`}
              onClick={() => setActiveTab("simple")}
            >
              <Brain className="h-4 w-4" />
              <span className="hidden sm:inline font-medium">Test</span>
            </TabsTrigger>
            <TabsTrigger
              value="realtime-call"
              className={`flex items-center space-x-2 rounded-xl transition-all duration-300 font-['Courier_New'] ${
                activeTab === "realtime-call" ? "bg-gradient-to-r from-green-500 to-emerald-600 text-white" : "text-slate-600 hover:text-slate-800"
              }`}
              onClick={() => setActiveTab("realtime-call")}
            >
              <Phone className="h-4 w-4" />
              <span className="hidden sm:inline font-medium">Live Call</span>
            </TabsTrigger>
            <TabsTrigger
              value="mental-health"
              className={`flex items-center space-x-2 rounded-xl transition-all duration-300 font-['Courier_New'] ${
                activeTab === "mental-health" ? "bg-gradient-to-r from-red-500 to-pink-600 text-white" : "text-slate-600 hover:text-slate-800"
              }`}
              onClick={() => setActiveTab("mental-health")}
            >
              <Heart className="h-4 w-4" />
              <span className="hidden sm:inline font-medium">Wellness</span>
            </TabsTrigger>
            <TabsTrigger
              value="emotion-analytics"
              className={`flex items-center space-x-2 rounded-xl transition-all duration-300 font-['Courier_New'] ${
                activeTab === "emotion-analytics" ? "bg-gradient-to-r from-purple-500 to-pink-600 text-white" : "text-slate-600 hover:text-slate-800"
              }`}
              onClick={() => setActiveTab("emotion-analytics")}
            >
              <BarChart3 className="h-4 w-4" />
              <span className="hidden sm:inline font-medium">Emotion Analytics</span>
            </TabsTrigger>
          </TabsList>

          <div className="grid grid-cols-1 lg:grid-cols-4 gap-8">
            {/* Main Content */}
            <div className="lg:col-span-3">
              <Card className="bg-white/90 backdrop-blur-xl border border-blue-200/50 rounded-3xl shadow-2xl shadow-blue-500/10 overflow-hidden">
                <div className="absolute inset-0 bg-gradient-to-br from-blue-50/30 to-transparent pointer-events-none" />

                {activeTab === "video" && (
                  <div className="relative">
                    <CardHeader className="border-b border-blue-200/50">
                      <CardTitle className="flex items-center space-x-3 text-slate-800 font-['Courier_New']">
                        <div className="w-10 h-10 bg-gradient-to-r from-blue-500 to-indigo-600 rounded-lg flex items-center justify-center">
                          <Camera className="h-5 w-5 text-white" />
                        </div>
                        <span className="text-xl">Video Emotion Detection</span>
                        <div className="flex-1" />
                        <Sparkles className="h-5 w-5 text-blue-500 animate-pulse" />
                      </CardTitle>
                    </CardHeader>
                    <CardContent className="p-8">
                      <CameraCapture
                        onEmotionDetected={(emotion) => handleEmotionDetected(emotion, "video")}
                        onProcessingChange={setIsProcessing}
                        userEmail={userEmail}
                      />
                      
                      {/* Neural Scan Active Status - Moved here from sidebar */}
                      {recentEmotion && (
                        <div className="mt-6 flex items-center justify-between p-4 bg-gradient-to-r from-green-500/20 to-emerald-500/20 rounded-xl border border-green-400/30 animate-neural-scan">
                          <div className="flex items-center space-x-3">
                            <div className="w-3 h-3 bg-green-400 rounded-full animate-pulse shadow-lg shadow-green-400/50" />
                            <span className="text-green-200 font-medium text-lg font-['Courier_New']">Neural Scan Active</span>
                          </div>
                          <div className="flex items-center space-x-3">
                            <Badge className={`${getEmotionColor(recentEmotion.primary_emotion)} border-0 shadow-lg text-sm px-3 py-1`}>
                              {recentEmotion.primary_emotion}
                            </Badge>
                            <span className="text-green-300 text-sm font-medium font-['Courier_New']">
                              {Math.round((recentEmotion.confidence || 0) * 100)}% confidence
                            </span>
                          </div>
                        </div>
                      )}
                    </CardContent>
                  </div>
                )}

                {activeTab === "text" && (
                  <div className="relative">
                    <CardHeader className="border-b border-blue-200/50">
                      <CardTitle className="flex items-center space-x-3 text-slate-800 font-['Courier_New']">
                        <div className="w-10 h-10 bg-gradient-to-r from-blue-500 to-cyan-600 rounded-lg flex items-center justify-center">
                          <FileText className="h-5 w-5 text-white" />
                        </div>
                        <span className="text-xl">Text Sentiment Analysis</span>
                        <div className="flex-1" />
                        <Sparkles className="h-5 w-5 text-blue-500 animate-pulse" />
                      </CardTitle>
                    </CardHeader>
                    <CardContent className="p-8">
                      <TextAnalysis
                        onEmotionDetected={(emotion) => handleEmotionDetected(emotion, "text")}
                        onProcessingChange={setIsProcessing}
                        userEmail={userEmail}
                      />
                    </CardContent>
                  </div>
                )}

                {activeTab === "simple" && (
                  <div className="relative">
                    <CardHeader className="border-b border-blue-200/50">
                      <CardTitle className="flex items-center space-x-3 text-slate-800 font-['Courier_New']">
                        <div className="w-10 h-10 bg-gradient-to-r from-indigo-500 to-purple-600 rounded-lg flex items-center justify-center">
                          <Brain className="h-5 w-5 text-white" />
                        </div>
                        <span className="text-xl">System Test</span>
                        <div className="flex-1" />
                        <Sparkles className="h-5 w-5 text-indigo-500 animate-pulse" />
                      </CardTitle>
                    </CardHeader>
                    <CardContent className="p-8">
                      <Simple />
                    </CardContent>
                  </div>
                )}

                {activeTab === "realtime-call" && (
                  <div className="relative">
                    <CardHeader className="border-b border-blue-200/50">
                      <CardTitle className="flex items-center space-x-3 text-slate-800 font-['Courier_New']">
                        <div className="w-10 h-10 bg-gradient-to-r from-green-500 to-emerald-600 rounded-lg flex items-center justify-center">
                          <Phone className="h-5 w-5 text-white" />
                        </div>
                        <span className="text-xl">Live Call</span>
                        <div className="flex-1" />
                        <Sparkles className="h-5 w-5 text-green-500 animate-pulse" />
                      </CardTitle>
                    </CardHeader>
                    <CardContent className="p-8">
                      <RealTimeCallAnalysis userEmail={userEmail} />
                    </CardContent>
                  </div>
                )}

                {activeTab === "mental-health" && (
                  <div className="relative">
                    <CardHeader className="border-b border-blue-200/50">
                      <CardTitle className="flex items-center space-x-3 text-slate-800 font-['Courier_New']">
                        <div className="w-10 h-10 bg-gradient-to-r from-red-500 to-pink-600 rounded-lg flex items-center justify-center">
                          <Heart className="h-5 w-5 text-white" />
                        </div>
                        <span className="text-xl">Mental Health Check-in</span>
                        <div className="flex-1" />
                        <Sparkles className="h-5 w-5 text-red-500 animate-pulse" />
                      </CardTitle>
                    </CardHeader>
                    <CardContent className="p-8">
                      <MentalHealthCheckin userEmail={userEmail} />
                    </CardContent>
                  </div>
                )}

                {activeTab === "emotion-analytics" && (
                  <div className="relative">
                    <CardHeader className="border-b border-blue-200/50">
                      <CardTitle className="flex items-center space-x-3 text-slate-800 font-['Courier_New']">
                        <div className="w-10 h-10 bg-gradient-to-r from-purple-500 to-pink-600 rounded-lg flex items-center justify-center">
                          <BarChart3 className="h-5 w-5 text-white" />
                        </div>
                        <span className="text-xl">Emotion Analytics</span>
                        <div className="flex-1" />
                        <Sparkles className="h-5 w-5 text-purple-500 animate-pulse" />
                      </CardTitle>
                    </CardHeader>
                    <CardContent className="p-8">
                      <EmotionAnalytics emotionHistory={emotionHistory} userEmail={userEmail} />
                    </CardContent>
                  </div>
                )}
              </Card>
            </div>

            {/* Artistic Sidebar */}
            <div className="space-y-6">
              {/* Processing Status */}
              <Card className="bg-white/90 backdrop-blur-xl border border-blue-200/50 rounded-2xl shadow-xl shadow-blue-500/10 overflow-hidden">
                <div className="absolute inset-0 bg-gradient-to-br from-blue-50/30 to-transparent pointer-events-none" />
                <CardHeader className="pb-3 relative">
                  <CardTitle className="text-slate-800 text-lg flex items-center space-x-2 font-['Courier_New']">
                    <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse shadow-lg shadow-green-500/50" />
                    <span>System Status</span>
                  </CardTitle>
                </CardHeader>
                <CardContent className="space-y-4 relative">
                  <div className="flex items-center justify-between p-3 bg-blue-50/50 rounded-xl border border-blue-200/50">
                    <span className="text-slate-700 font-['Courier_New']">Neural Processing</span>
                    <div
                      className={`w-3 h-3 rounded-full ${isProcessing ? "bg-green-500 animate-pulse shadow-lg shadow-green-500/50" : "bg-gray-400"}`}
                    />
                  </div>
                  <div className="flex items-center justify-between p-3 bg-blue-50/50 rounded-xl border border-blue-200/50">
                    <span className="text-slate-700 font-['Courier_New']">Models Active</span>
                    <Badge className="bg-gradient-to-r from-blue-500 to-indigo-600 text-white border-0 shadow-lg font-['Courier_New']">
                      3/3
                    </Badge>
                  </div>
                  <div className="flex items-center justify-between p-3 bg-blue-50/50 rounded-xl border border-blue-200/50">
                    <span className="text-slate-700 font-['Courier_New']">API Connection</span>
                    <div className="w-3 h-3 bg-green-500 rounded-full animate-pulse shadow-lg shadow-green-500/50" />
                  </div>
                </CardContent>
              </Card>

              {/* Recent Emotions */}
              <Card className="bg-white/90 backdrop-blur-xl border border-blue-200/50 rounded-2xl shadow-xl shadow-blue-500/10 overflow-hidden">
                <div className="absolute inset-0 bg-gradient-to-br from-blue-50/30 to-transparent pointer-events-none" />
                <CardHeader className="pb-3 relative">
                  <CardTitle className="text-slate-800 text-lg flex items-center space-x-2 font-['Courier_New']">
                    <Activity className="h-5 w-5 text-blue-500" />
                    <span>Recent Detections</span>
                  </CardTitle>
                </CardHeader>
                <CardContent className="space-y-3 relative">
                  {emotionHistory.slice(0, 5).map((emotion, index) => (
                    <div
                      key={index}
                      className="flex items-center justify-between p-3 bg-blue-50/50 rounded-xl border border-blue-200/50 hover:bg-blue-100/50 transition-all duration-300"
                    >
                      <div className="flex items-center space-x-3 min-w-0 flex-1">
                        <Badge className={`${getEmotionColor(emotion.primary_emotion)} border-0 shadow-lg text-xs flex-shrink-0 font-['Courier_New']`}>
                          {emotion.primary_emotion}
                        </Badge>
                        <span className="text-slate-600 text-xs capitalize truncate font-['Courier_New']">{emotion.modality}</span>
                      </div>
                      <span className="text-slate-700 text-xs font-medium flex-shrink-0 ml-2 font-['Courier_New']">
                        {Math.round((emotion.confidence || 0) * 100)}%
                      </span>
                    </div>
                  ))}
                  {emotionHistory.length === 0 && (
                    <div className="text-center py-8">
                      <div className="w-12 h-12 bg-gradient-to-r from-blue-200 to-indigo-200 rounded-full flex items-center justify-center mx-auto mb-3">
                        <Brain className="h-6 w-6 text-blue-500" />
                      </div>
                      <p className="text-slate-600 text-sm font-['Courier_New']">Awaiting neural signals...</p>
                    </div>
                  )}
                </CardContent>
              </Card>

              {/* Artistic Stats */}
              {emotionHistory.length > 0 && (
                <Card className="bg-white/90 backdrop-blur-xl border border-blue-200/50 rounded-2xl shadow-xl shadow-blue-500/10 overflow-hidden">
                  <div className="absolute inset-0 bg-gradient-to-br from-blue-50/30 to-transparent pointer-events-none" />
                  <CardHeader className="pb-3 relative">
                    <CardTitle className="text-slate-800 text-lg flex items-center space-x-2 font-['Courier_New']">
                      <BarChart3 className="h-5 w-5 text-blue-500" />
                      <span>Neural Analytics</span>
                    </CardTitle>
                  </CardHeader>
                  <CardContent className="space-y-4 relative">
                    <div className="flex justify-between items-center p-3 bg-blue-50/50 rounded-xl border border-blue-200/50">
                      <span className="text-slate-700 text-sm font-['Courier_New']">Total Signals</span>
                      <span className="text-slate-800 font-bold text-lg font-['Courier_New']">{emotionHistory.length}</span>
                    </div>
                    <div className="flex justify-between items-center p-3 bg-blue-50/50 rounded-xl border border-blue-200/50">
                      <span className="text-slate-700 text-sm font-['Courier_New']">Avg Confidence</span>
                      <span className="text-slate-800 font-bold text-lg font-['Courier_New']">
                        {Math.round(
                          (emotionHistory.reduce((acc, e) => acc + (e.confidence || 0), 0) / emotionHistory.length) * 100,
                        )}
                        %
                      </span>
                    </div>
                    <div className="flex justify-between items-center p-3 bg-blue-50/50 rounded-xl border border-blue-200/50">
                      <span className="text-slate-700 text-sm font-['Courier_New']">Dominant State</span>
                      <Badge
                        className={`${getEmotionColor(
                          Object.entries(
                            emotionHistory.reduce(
                              (acc, e) => {
                                acc[e.primary_emotion] = (acc[e.primary_emotion] || 0) + 1
                                return acc
                              },
                              {},
                            ),
                          ).sort(([, a], [, b]) => b - a)[0]?.[0] || "neutral",
                        )} border-0 shadow-lg text-xs font-['Courier_New']`}
                      >
                        {Object.entries(
                          emotionHistory.reduce(
                            (acc, e) => {
                              acc[e.primary_emotion] = (acc[e.primary_emotion] || 0) + 1
                              return acc
                            },
                            {},
                          ),
                        ).sort(([, a], [, b]) => b - a)[0]?.[0] || "neutral"}
                      </Badge>
                    </div>
                  </CardContent>
                </Card>
              )}
            </div>
          </div>
        </Tabs>
      </main>
    </div>
  );
}

export default MindBridgeApp; 