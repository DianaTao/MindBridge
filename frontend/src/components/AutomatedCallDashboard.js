import React, { useState, useEffect, useCallback } from 'react';
import { Card, CardContent } from './ui/card';
import { Badge } from './ui/badge';
import { Button } from './ui/button';
import { Input } from './ui/input';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from './ui/select';
import {
  Play,
  Download,
  Search,
  Clock,
  Phone,
  MessageSquare,
  AlertCircle,
  CheckCircle,
  XCircle,
  TrendingUp,
} from 'lucide-react';

const AutomatedCallDashboard = () => {
  const [calls, setCalls] = useState([]);
  const [filteredCalls, setFilteredCalls] = useState([]);
  const [loading, setLoading] = useState(true);
  const [filters, setFilters] = useState({
    status: 'all',
    agentId: 'all',
    sentiment: 'all',
    dateRange: '7d',
  });
  const [searchTerm, setSearchTerm] = useState('');
  const [stats, setStats] = useState({
    totalCalls: 0,
    completedCalls: 0,
    processingCalls: 0,
    averageEmpathyScore: 0,
    averageQualityScore: 0,
  });

  // Mock data for demonstration
  const generateMockCalls = useCallback(() => {
    const mockCalls = [
      {
        callId: 'call_001',
        agentId: 'agent_123',
        customerId: 'cust_456',
        timestamp: new Date(Date.now() - 2 * 60 * 60 * 1000).toISOString(),
        duration: '5:32',
        status: 'completed',
        recordingUrl: 's3://mindbridge-call-recordings-dev/incoming/agent_123/call_001.mp3',
        analysis: {
          customerSentiment: 'positive',
          agentEmpathyScore: 8.5,
          qualityScore: 9.2,
          summary:
            'Agent successfully resolved billing dispute with excellent empathy. Customer satisfaction improved from frustrated to satisfied.',
          keyPhrases: ['billing error', 'refund', 'apology', 'resolution'],
          emotionTimeline: [
            {
              time: '00:00',
              agent: 'calm',
              customer: 'frustrated',
              text: 'Hello, I have a billing issue...',
            },
            {
              time: '01:30',
              agent: 'empathetic',
              customer: 'concerned',
              text: 'I understand your frustration...',
            },
            {
              time: '03:45',
              agent: 'helpful',
              customer: 'relieved',
              text: 'I can help you with that...',
            },
            {
              time: '05:00',
              agent: 'satisfied',
              customer: 'satisfied',
              text: 'Thank you for your help!',
            },
          ],
        },
      },
      {
        callId: 'call_002',
        agentId: 'agent_456',
        customerId: 'cust_789',
        timestamp: new Date(Date.now() - 1 * 60 * 60 * 1000).toISOString(),
        duration: '3:15',
        status: 'processing',
        recordingUrl: 's3://mindbridge-call-recordings-dev/incoming/agent_456/call_002.mp3',
        analysis: {
          customerSentiment: 'analyzing',
          agentEmpathyScore: 0,
          qualityScore: 0,
          summary: 'Call is being processed. Analysis will be available shortly.',
          keyPhrases: ['processing'],
          emotionTimeline: [
            {
              time: '00:00',
              agent: 'processing',
              customer: 'processing',
              text: 'Analysis in progress...',
            },
          ],
        },
      },
      {
        callId: 'call_003',
        agentId: 'agent_123',
        customerId: 'cust_101',
        timestamp: new Date(Date.now() - 30 * 60 * 1000).toISOString(),
        duration: '7:45',
        status: 'completed',
        recordingUrl: 's3://mindbridge-call-recordings-dev/incoming/agent_123/call_003.mp3',
        analysis: {
          customerSentiment: 'neutral',
          agentEmpathyScore: 6.8,
          qualityScore: 7.1,
          summary:
            'Standard technical support call. Agent provided adequate assistance but could improve empathy.',
          keyPhrases: ['technical issue', 'password reset', 'account access'],
          emotionTimeline: [
            {
              time: '00:00',
              agent: 'professional',
              customer: 'neutral',
              text: 'I need help with my account...',
            },
            {
              time: '02:15',
              agent: 'helpful',
              customer: 'slightly frustrated',
              text: 'Let me guide you through this...',
            },
            {
              time: '05:30',
              agent: 'patient',
              customer: 'relieved',
              text: 'I see the issue now...',
            },
            {
              time: '07:30',
              agent: 'satisfied',
              customer: 'satisfied',
              text: 'Thank you for your patience!',
            },
          ],
        },
      },
    ];
    return mockCalls;
  }, []);

  useEffect(() => {
    // Simulate loading data
    setTimeout(() => {
      const mockCalls = generateMockCalls();
      setCalls(mockCalls);
      setFilteredCalls(mockCalls);
      setLoading(false);

      // Calculate stats
      const completed = mockCalls.filter(call => call.status === 'completed').length;
      const processing = mockCalls.filter(call => call.status === 'processing').length;
      const avgEmpathy =
        mockCalls
          .filter(call => call.status === 'completed')
          .reduce((sum, call) => sum + call.analysis.agentEmpathyScore, 0) / completed || 0;
      const avgQuality =
        mockCalls
          .filter(call => call.status === 'completed')
          .reduce((sum, call) => sum + call.analysis.qualityScore, 0) / completed || 0;

      setStats({
        totalCalls: mockCalls.length,
        completedCalls: completed,
        processingCalls: processing,
        averageEmpathyScore: avgEmpathy,
        averageQualityScore: avgQuality,
      });
    }, 1000);
  }, [generateMockCalls]);

  useEffect(() => {
    // Apply filters and search
    let filtered = calls;

    // Apply status filter
    if (filters.status !== 'all') {
      filtered = filtered.filter(call => call.status === filters.status);
    }

    // Apply agent filter
    if (filters.agentId !== 'all') {
      filtered = filtered.filter(call => call.agentId === filters.agentId);
    }

    // Apply sentiment filter
    if (filters.sentiment !== 'all') {
      filtered = filtered.filter(call => call.analysis.customerSentiment === filters.sentiment);
    }

    // Apply search
    if (searchTerm) {
      filtered = filtered.filter(
        call =>
          call.callId.toLowerCase().includes(searchTerm.toLowerCase()) ||
          call.agentId.toLowerCase().includes(searchTerm.toLowerCase()) ||
          call.analysis.summary.toLowerCase().includes(searchTerm.toLowerCase())
      );
    }

    setFilteredCalls(filtered);
  }, [calls, filters, searchTerm]);

  const getStatusIcon = status => {
    switch (status) {
      case 'completed':
        return <CheckCircle className="w-4 h-4 text-green-500" />;
      case 'processing':
        return <Clock className="w-4 h-4 text-yellow-500" />;
      case 'failed':
        return <XCircle className="w-4 h-4 text-red-500" />;
      default:
        return <AlertCircle className="w-4 h-4 text-gray-500" />;
    }
  };

  const getSentimentColor = sentiment => {
    switch (sentiment) {
      case 'positive':
        return 'bg-green-100 text-green-800';
      case 'negative':
        return 'bg-red-100 text-red-800';
      case 'neutral':
        return 'bg-gray-100 text-gray-800';
      default:
        return 'bg-yellow-100 text-yellow-800';
    }
  };

  const formatDuration = duration => {
    return duration;
  };

  const formatTimestamp = timestamp => {
    return new Date(timestamp).toLocaleString();
  };

  const getQualityColor = score => {
    if (score >= 8) return 'text-green-600';
    if (score >= 6) return 'text-yellow-600';
    return 'text-red-600';
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header Stats */}
      <div className="grid grid-cols-1 md:grid-cols-5 gap-4">
        <Card>
          <CardContent className="p-4">
            <div className="flex items-center space-x-2">
              <Phone className="w-5 h-5 text-blue-600" />
              <div>
                <p className="text-sm text-gray-600">Total Calls</p>
                <p className="text-2xl font-bold">{stats.totalCalls}</p>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-4">
            <div className="flex items-center space-x-2">
              <CheckCircle className="w-5 h-5 text-green-600" />
              <div>
                <p className="text-sm text-gray-600">Completed</p>
                <p className="text-2xl font-bold">{stats.completedCalls}</p>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-4">
            <div className="flex items-center space-x-2">
              <Clock className="w-5 h-5 text-yellow-600" />
              <div>
                <p className="text-sm text-gray-600">Processing</p>
                <p className="text-2xl font-bold">{stats.processingCalls}</p>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-4">
            <div className="flex items-center space-x-2">
              <TrendingUp className="w-5 h-5 text-purple-600" />
              <div>
                <p className="text-sm text-gray-600">Avg Empathy</p>
                <p className="text-2xl font-bold">{stats.averageEmpathyScore.toFixed(1)}</p>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-4">
            <div className="flex items-center space-x-2">
              <TrendingUp className="w-5 h-5 text-indigo-600" />
              <div>
                <p className="text-sm text-gray-600">Avg Quality</p>
                <p className="text-2xl font-bold">{stats.averageQualityScore.toFixed(1)}</p>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Filters and Search */}
      <Card>
        <CardContent className="p-6">
          <div className="flex flex-col md:flex-row gap-4">
            <div className="flex-1">
              <div className="relative">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-4 h-4" />
                <Input
                  placeholder="Search calls, agents, or content..."
                  value={searchTerm}
                  onChange={e => setSearchTerm(e.target.value)}
                  className="pl-10"
                />
              </div>
            </div>

            <Select
              value={filters.status}
              onValueChange={value => setFilters({ ...filters, status: value })}
            >
              <SelectTrigger className="w-full md:w-40">
                <SelectValue placeholder="Status" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">All Status</SelectItem>
                <SelectItem value="completed">Completed</SelectItem>
                <SelectItem value="processing">Processing</SelectItem>
                <SelectItem value="failed">Failed</SelectItem>
              </SelectContent>
            </Select>

            <Select
              value={filters.sentiment}
              onValueChange={value => setFilters({ ...filters, sentiment: value })}
            >
              <SelectTrigger className="w-full md:w-40">
                <SelectValue placeholder="Sentiment" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">All Sentiment</SelectItem>
                <SelectItem value="positive">Positive</SelectItem>
                <SelectItem value="negative">Negative</SelectItem>
                <SelectItem value="neutral">Neutral</SelectItem>
              </SelectContent>
            </Select>

            <Select
              value={filters.dateRange}
              onValueChange={value => setFilters({ ...filters, dateRange: value })}
            >
              <SelectTrigger className="w-full md:w-40">
                <SelectValue placeholder="Date Range" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="1d">Last 24h</SelectItem>
                <SelectItem value="7d">Last 7 days</SelectItem>
                <SelectItem value="30d">Last 30 days</SelectItem>
                <SelectItem value="90d">Last 90 days</SelectItem>
              </SelectContent>
            </Select>
          </div>
        </CardContent>
      </Card>

      {/* Calls List */}
      <div className="space-y-4">
        {filteredCalls.map(call => (
          <Card key={call.callId} className="hover:shadow-md transition-shadow">
            <CardContent className="p-6">
              <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between space-y-4 lg:space-y-0">
                {/* Call Info */}
                <div className="flex-1 space-y-3">
                  <div className="flex items-center space-x-4">
                    <div className="flex items-center space-x-2">
                      {getStatusIcon(call.status)}
                      <span className="font-semibold">{call.callId}</span>
                    </div>
                    <Badge variant={call.status === 'completed' ? 'default' : 'secondary'}>
                      {call.status}
                    </Badge>
                    <Badge className={getSentimentColor(call.analysis.customerSentiment)}>
                      {call.analysis.customerSentiment}
                    </Badge>
                  </div>

                  <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
                    <div>
                      <p className="text-gray-600">Agent</p>
                      <p className="font-medium">{call.agentId}</p>
                    </div>
                    <div>
                      <p className="text-gray-600">Duration</p>
                      <p className="font-medium">{formatDuration(call.duration)}</p>
                    </div>
                    <div>
                      <p className="text-gray-600">Empathy Score</p>
                      <p
                        className={`font-medium ${getQualityColor(call.analysis.agentEmpathyScore)}`}
                      >
                        {call.analysis.agentEmpathyScore}/10
                      </p>
                    </div>
                    <div>
                      <p className="text-gray-600">Quality Score</p>
                      <p className={`font-medium ${getQualityColor(call.analysis.qualityScore)}`}>
                        {call.analysis.qualityScore}/10
                      </p>
                    </div>
                  </div>

                  <div>
                    <p className="text-gray-600 text-sm">Summary</p>
                    <p className="text-sm">{call.analysis.summary}</p>
                  </div>

                  <div className="flex flex-wrap gap-2">
                    {call.analysis.keyPhrases.slice(0, 3).map((phrase, index) => (
                      <Badge key={index} variant="outline" className="text-xs">
                        {phrase}
                      </Badge>
                    ))}
                  </div>
                </div>

                {/* Actions */}
                <div className="flex flex-col space-y-2">
                  <div className="text-xs text-gray-500">{formatTimestamp(call.timestamp)}</div>
                  <div className="flex space-x-2">
                    <Button size="sm" variant="outline">
                      <Play className="w-4 h-4 mr-1" />
                      Review
                    </Button>
                    <Button size="sm" variant="outline">
                      <Download className="w-4 h-4 mr-1" />
                      Download
                    </Button>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      {/* Empty State */}
      {filteredCalls.length === 0 && !loading && (
        <Card>
          <CardContent className="p-12 text-center">
            <MessageSquare className="w-12 h-12 text-gray-400 mx-auto mb-4" />
            <h3 className="text-lg font-medium text-gray-900 mb-2">No calls found</h3>
            <p className="text-gray-600">Try adjusting your filters or search terms.</p>
          </CardContent>
        </Card>
      )}
    </div>
  );
};

export default AutomatedCallDashboard;
