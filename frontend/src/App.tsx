import { useState, useEffect } from 'react';
import axios from 'axios';
import ReactMarkdown from 'react-markdown';
import {
  Loader2, TrendingUp, TrendingDown, DollarSign, Activity,
  Newspaper, BarChart3, PieChart, ShieldCheck, AlertTriangle
} from 'lucide-react';
import clsx from 'clsx';

// Types
interface JobStatus {
  status: 'pending' | 'running' | 'completed' | 'failed';
  result?: string;
  error?: string;
}

const API_URL = 'http://localhost:8000';

// --- Text Parsing Helpers (Regex) ---
// Note: This relies on the specific format output by the agents.
// If agents change format, this might break, but fallback is raw markdown.

function parseMetric(text: string, regex: RegExp): string | null {
  const match = text.match(regex);
  return match ? match[1] : null;
}

function extractSection(text: string, header: string): string {
  const parts = text.split(header);
  if (parts.length > 1) {
    // Return content until next header or end
    return parts[1].split(/#{1,3} /)[0].trim();
  }
  return '';
}

function App() {
  const [symbol, setSymbol] = useState('');
  const [taskId, setTaskId] = useState<string | null>(null);
  const [status, setStatus] = useState<JobStatus['status']>('pending');
  const [rawResult, setRawResult] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  // Parsed State
  const [parsedData, setParsedData] = useState<{
    price?: string;
    recommendation?: string;
    confidence?: string;
    target?: string;
    rsi?: string;
    pe?: string;
    news?: string[];
  }>({});

  const startAnalysis = async () => {
    if (!symbol) return;
    try {
      setStatus('running');
      setRawResult(null);
      setError(null);
      setParsedData({});
      const res = await axios.post(`${API_URL}/analyze`, { symbol });
      setTaskId(res.data.task_id);
    } catch (err) {
      setError('Failed to start analysis. Is the backend running?');
      setStatus('failed');
    }
  };

  useEffect(() => {
    let interval: any;
    if (taskId && (status === 'running' || status === 'pending')) {
      interval = setInterval(async () => {
        try {
          const res = await axios.get(`${API_URL}/status/${taskId}`);
          const job = res.data;
          setStatus(job.status);

          if (job.status === 'completed' && job.result) {
            setRawResult(job.result);
            parseResults(job.result);
            clearInterval(interval);
          } else if (job.status === 'failed') {
            setStatus('failed');
            setError(job.error || 'Analysis failed');
            clearInterval(interval);
          }
        } catch (err) {
          console.error("Polling error", err);
        }
      }, 3000);
    }
    return () => clearInterval(interval);
  }, [taskId, status]);

  const parseResults = (text: string) => {
    // 1. Current Price
    const price = parseMetric(text, /Current Price:.*\$([\d,]+\.?\d*)/i);

    // 2. Recommendation
    const rec = parseMetric(text, /## RECOMMENDATION:\s*(.*)/i) ||
      parseMetric(text, /RECOMMENDATION:\s*(.*)/i);

    // 3. Price Target
    const target = parseMetric(text, /Price Target:.*\$([\d,]+\.?\d*)/i);

    // 4. Confidence
    const confidence = parseMetric(text, /Confidence(?: Level)?:.*?(\d+%?)/i);

    // 5. RSI
    const rsi = parseMetric(text, /RSI:.*?([\d.]+)/i);

    // 6. P/E
    const pe = parseMetric(text, /P\/E Ratio:.*?([\d.]+)/i);

    setParsedData({
      price: price || undefined,
      recommendation: rec?.replace(/[\[\]]/g, '').trim() || undefined,
      target: target || undefined,
      confidence: confidence || undefined,
      rsi: rsi || undefined,
      pe: pe || undefined,
    });
  };

  // Status Badge Logic
  const getStatusColor = () => {
    switch (status) {
      case 'running': return 'bg-blue-100 text-blue-700 border-blue-200';
      case 'completed': return 'bg-green-100 text-green-700 border-green-200';
      case 'failed': return 'bg-red-100 text-red-700 border-red-200';
      default: return 'bg-gray-100 text-gray-700 border-gray-200';
    }
  };

  return (
    <div className="min-h-screen bg-slate-50 font-sans text-slate-800">
      {/* Navbar */}
      <nav className="bg-white border-b border-slate-200 px-6 py-4 sticky top-0 z-10 shadow-sm">
        <div className="max-w-7xl mx-auto flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="bg-blue-600 p-2 rounded-lg text-white">
              <TrendingUp size={24} />
            </div>
            <h1 className="text-2xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-blue-700 to-indigo-600">
              Finance Analysis Crew
            </h1>
          </div>
          <div className={`px-4 py-1.5 rounded-full text-sm font-medium border flex items-center gap-2 ${getStatusColor()}`}>
            <Activity size={16} />
            <span className="capitalize">{status}</span>
          </div>
        </div>
      </nav>

      <main className="max-w-7xl mx-auto px-6 py-8">
        {/* Input Hero */}
        <div className="bg-white rounded-2xl shadow-sm border border-slate-200 p-1 bg-gradient-to-br from-white to-slate-50 mb-8">
          <div className="flex gap-2 p-2">
            <input
              type="text"
              value={symbol}
              onChange={(e) => setSymbol(e.target.value.toUpperCase())}
              placeholder="Enter Ticker (e.g., NVDA)..."
              className="flex-1 px-6 py-4 text-xl bg-transparent outline-none placeholder:text-slate-300 font-semibold uppercase tracking-wider"
              onKeyDown={(e) => e.key === 'Enter' && startAnalysis()}
            />
            <button
              onClick={startAnalysis}
              disabled={status === 'running' || !symbol}
              className="bg-blue-600 hover:bg-blue-700 text-white px-8 py-3 rounded-xl font-bold transition-all disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2 shadow-lg shadow-blue-600/20"
            >
              {status === 'running' ? <Loader2 className="animate-spin" /> : <TrendingUp />}
              Analyze
            </button>
          </div>
        </div>

        {error && (
          <div className="bg-red-50 border border-red-200 text-red-700 p-4 rounded-xl mb-6 flex items-center gap-3">
            <AlertTriangle /> {error}
          </div>
        )}

        {/* Dashboard Grid - Only show if we have some results or are complete */}
        {(status === 'completed' && rawResult) && (
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6 animate-in slide-in-from-bottom-4 duration-500">

            {/* 1. Main Recommendation Card */}
            <div className={clsx(
              "md:col-span-2 rounded-2xl p-6 text-white shadow-xl relative overflow-hidden",
              parsedData.recommendation?.toUpperCase().includes('BUY') ? "bg-gradient-to-br from-green-600 to-emerald-600" :
                parsedData.recommendation?.toUpperCase().includes('SELL') ? "bg-gradient-to-br from-red-600 to-rose-600" :
                  "bg-gradient-to-br from-yellow-500 to-amber-600"
            )}>
              <div className="relative z-10 flex justify-between items-start">
                <div>
                  <p className="text-white/80 font-medium mb-1">Recommendation</p>
                  <h2 className="text-4xl font-extrabold tracking-tight mb-2">
                    {parsedData.recommendation || "HOLD"}
                  </h2>
                  <div className="flex items-center gap-2 text-white/90">
                    <ShieldCheck size={18} />
                    <span className="font-semibold">Confidence: {parsedData.confidence || "N/A"}</span>
                  </div>
                </div>
                <div className="text-right">
                  <p className="text-white/80 font-medium mb-1">Target Price</p>
                  <div className="text-4xl font-mono font-bold">
                    ${parsedData.target || "??"}
                  </div>
                  <p className="text-sm text-white/60 mt-1">6-12 Month Forecast</p>
                </div>
              </div>
              {/* Decorative Circle */}
              <div className="absolute -bottom-10 -right-10 w-48 h-48 bg-white/10 rounded-full blur-2xl"></div>
            </div>

            {/* 2. Current Price Card */}
            <div className="bg-white rounded-2xl p-6 shadow-sm border border-slate-200 flex flex-col justify-center">
              <div className="flex items-center gap-3 mb-2 text-slate-500">
                <DollarSign size={20} />
                <span className="font-medium text-sm uppercase">Currently Trading</span>
              </div>
              <div className="text-5xl font-mono font-bold text-slate-800 tracking-tighter">
                ${parsedData.price || "---"}
              </div>
              <div className="mt-4 flex items-center gap-2 text-sm text-slate-400">
                Last close data
              </div>
            </div>

            {/* 3. Key Metrics Grid */}
            <div className="md:col-span-3 grid grid-cols-2 md:grid-cols-4 gap-4">
              <div className="bg-white p-5 rounded-xl border border-slate-100 shadow-sm hover:border-blue-200 transition-colors group">
                <div className="flex items-center gap-2 text-slate-400 mb-2 group-hover:text-blue-500">
                  <Activity size={18} /> RSI (14)
                </div>
                <div className={clsx("text-2xl font-bold", parseFloat(parsedData.rsi || '50') > 70 ? "text-red-500" : parseFloat(parsedData.rsi || '50') < 30 ? "text-green-500" : "text-slate-700")}>
                  {parsedData.rsi || "N/A"}
                </div>
              </div>
              <div className="bg-white p-5 rounded-xl border border-slate-100 shadow-sm hover:border-blue-200 transition-colors group">
                <div className="flex items-center gap-2 text-slate-400 mb-2 group-hover:text-blue-500">
                  <PieChart size={18} /> P/E Ratio
                </div>
                <div className="text-2xl font-bold text-slate-700">
                  {parsedData.pe || "N/A"}
                </div>
              </div>
              <div className="bg-white p-5 rounded-xl border border-slate-100 shadow-sm hover:border-blue-200 transition-colors group">
                <div className="flex items-center gap-2 text-slate-400 mb-2 group-hover:text-blue-500">
                  <BarChart3 size={18} /> Sector
                </div>
                <div className="text-xl font-bold text-slate-700 truncate">
                  Technology
                </div>
              </div>
              <div className="bg-white p-5 rounded-xl border border-slate-100 shadow-sm hover:border-blue-200 transition-colors group">
                <div className="flex items-center gap-2 text-slate-400 mb-2 group-hover:text-blue-500">
                  <Newspaper size={18} /> News Sentiment
                </div>
                <div className="text-xl font-bold text-green-600">
                  Bullish
                </div>
              </div>
            </div>

            {/* 4. Full Report (Markdown) */}
            <div className="md:col-span-3 bg-white rounded-2xl shadow-sm border border-slate-200 overflow-hidden mt-4">
              <div className="bg-slate-50 px-6 py-4 border-b border-slate-100">
                <h3 className="font-bold text-slate-700 flex items-center gap-2">
                  <FileText size={20} className="text-blue-500" />
                  Detailed Analyst Report
                </h3>
              </div>
              <article className="prose prose-slate max-w-none p-8 prose-headings:font-bold prose-h1:text-3xl prose-h2:text-2xl prose-a:text-blue-600 hover:prose-a:text-blue-500 overflow-x-auto break-words">
                <ReactMarkdown>{rawResult || ''}</ReactMarkdown>
              </article>
            </div>

          </div>
        )}

        {/* Loading State */}
        {status === 'running' && (
          <div className="flex flex-col items-center justify-center py-20 text-slate-400 animate-pulse">
            <div className="relative">
              <div className="absolute inset-0 bg-blue-500 blur-xl opacity-20 rounded-full"></div>
              <Loader2 size={64} className="text-blue-600 animate-spin relative z-10" />
            </div>
            <p className="mt-8 text-xl font-medium text-slate-600">Orchestrating AI Agents...</p>
            <div className="flex gap-2 mt-4 text-sm">
              <span className="bg-white px-3 py-1 rounded-full border border-slate-200">Market Researcher</span>
              <span className="bg-white px-3 py-1 rounded-full border border-slate-200">Technical Analyst</span>
              <span className="bg-white px-3 py-1 rounded-full border border-slate-200">Fundamental Specialist</span>
            </div>
          </div>
        )}

        {/* Empty State */}
        {status === 'pending' && !rawResult && (
          <div className="text-center py-20 opacity-50">
            <div className="inline-block p-6 bg-slate-100 rounded-full mb-4">
              <TrendingUp size={48} className="text-slate-400" />
            </div>
            <h2 className="text-2xl font-bold text-slate-400">Ready to Analyze</h2>
            <p className="text-slate-400 mt-2">Enter a stock symbol above to begin the deep dive.</p>
          </div>
        )}

      </main>
    </div>
  );
}

function FileText({ size, className }: { size?: number, className?: string }) {
  return (
    <svg xmlns="http://www.w3.org/2000/svg" width={size || 24} height={size || 24} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className={className}>
      <path d="M14.5 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V7.5L14.5 2z" />
      <polyline points="14 2 14 8 20 8" />
      <line x1="16" x2="8" y1="13" y2="13" />
      <line x1="16" x2="8" y1="17" y2="17" />
      <line x1="10" x2="8" y1="9" y2="9" />
    </svg>
  )
}

export default App;
