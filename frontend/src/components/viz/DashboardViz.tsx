import React, { useState, useEffect, useCallback } from 'react'
import { 
  TrendingUp, 
  Clock, 
  Zap, 
  Database, 
  RefreshCcw, 
  AlertCircle, 
  Activity, 
  PieChart, 
  BarChart, 
  Layers, 
  Cpu,
  Search,
  History
} from 'lucide-react'

interface AnalyticsData {
  generated_at: string
  total_requests: number
  requests_by_endpoint: Record<string, number>
  tool_usage_counts: Record<string, number>
  query_category_counts: Record<string, number>
  response_times: {
    avg: number
    min: number
    max: number
    p95: number
  }
  recent_queries: Array<{
    query: string
    tool_used: string
    response_time_ms: number
    category: string
    timestamp: string
  }>
  popular_queries: Array<{
    query: string
    count: number
  }>
  hourly_distribution: Record<string, number>
  model_usage: Record<string, number>
  pinecone_vector_count: number
  pinecone_index_name: string
}

const DashboardViz = () => {
  const [data, setData] = useState<AnalyticsData | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const fetchAnalytics = useCallback(async () => {
    setLoading(true)
    setError(null)
    try {
      const response = await fetch('http://localhost:8000/api/v1/analytics')
      if (!response.ok) throw new Error('Failed to fetch analytics')
      const result = await response.json()
      setData(result)
    } catch (err: any) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => {
    fetchAnalytics()
  }, [fetchAnalytics])

  if (loading && !data) {
    return (
      <div className="flex flex-col items-center justify-center h-full space-y-4 animate-pulse">
        <RefreshCcw className="w-12 h-12 text-primary-500 animate-spin" />
        <p className="text-slate-500 font-medium">Gathering Intelligence...</p>
      </div>
    )
  }

  if (error) {
    return (
      <div className="flex flex-col items-center justify-center h-full p-6 text-center space-y-4">
        <AlertCircle className="w-16 h-16 text-red-500" />
        <h3 className="text-xl font-bold text-slate-800 dark:text-slate-100">Analytics Offline</h3>
        <p className="text-slate-500 max-w-xs">{error}</p>
        <button 
          onClick={fetchAnalytics}
          className="px-6 py-2 bg-primary-600 text-white rounded-xl shadow-lg hover:bg-primary-700 transition-all font-semibold"
        >
          Try Again
        </button>
      </div>
    )
  }

  if (!data) return null

  const maxToolCount = Math.max(...Object.values(data.tool_usage_counts), 1)
  const maxCategoryCount = Math.max(...Object.values(data.query_category_counts), 1)
  const maxHourCount = Math.max(...Object.values(data.hourly_distribution), 1)

  return (
    <div className="p-6 space-y-8 animate-in fade-in slide-in-from-bottom-4 duration-700 pb-20">
      {/* Header */}
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4 border-b border-slate-200 dark:border-slate-800 pb-6 mb-2">
        <div>
          <h2 className="text-2xl font-bold text-slate-800 dark:text-slate-100">System Analytics</h2>
          <p className="text-sm text-slate-500">Real-time performance and query intelligence</p>
        </div>
        <div className="flex items-center gap-3">
           <span className="text-[10px] bg-slate-100 dark:bg-slate-800 text-slate-500 px-2 py-1 rounded-md font-mono">
             Last Sync: {new Date(data.generated_at).toLocaleTimeString()}
           </span>
           <button 
            onClick={fetchAnalytics}
            disabled={loading}
            className="p-2.5 bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-xl text-slate-600 dark:text-slate-300 hover:text-primary-600 dark:hover:text-primary-400 hover:shadow-md transition-all disabled:opacity-50"
          >
            <RefreshCcw className={`w-5 h-5 ${loading ? 'animate-spin' : ''}`} />
          </button>
        </div>
      </div>

      {/* Section 1: Overview Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <MetricCard label="Total Requests" value={data.total_requests} icon={<Activity className="w-4 h-4" />} color="bg-blue-500" />
        <MetricCard label="Avg Latency" value={`${data.response_times.avg}ms`} icon={<Clock className="w-4 h-4" />} color="bg-emerald-500" />
        <MetricCard label="P95 Response" value={`${data.response_times.p95}ms`} icon={<Zap className="w-4 h-4" />} color="bg-amber-500" />
        <MetricCard label="Knowledge Base" value={data.pinecone_vector_count} subValue={data.pinecone_index_name} icon={<Database className="w-4 h-4" />} color="bg-indigo-500" />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        {/* Section 2: Tool Usage */}
        <ChartSection title="Tool Distribution" icon={<PieChart className="w-4 h-4" />}>
          <div className="space-y-4">
            {Object.entries(data.tool_usage_counts).sort((a, b) => b[1] - a[1]).map(([tool, count]) => (
              <div key={tool} className="space-y-1">
                <div className="flex justify-between text-xs font-medium">
                  <span className="text-slate-600 dark:text-slate-400 capitalize">{tool.replace(/_/g, ' ')}</span>
                  <span className="text-slate-800 dark:text-slate-200">{count}</span>
                </div>
                <div className="h-2 bg-slate-100 dark:bg-slate-700/50 rounded-full overflow-hidden">
                  <div 
                    className={`h-full rounded-full transition-all duration-1000 ${count === maxToolCount ? 'bg-primary-500' : 'bg-slate-400 dark:bg-slate-500'}`}
                    style={{ width: `${(count / maxToolCount) * 100}%` }}
                  />
                </div>
              </div>
            ))}
          </div>
        </ChartSection>

        {/* Section 3: Query Categories */}
        <ChartSection title="Topic Intelligence" icon={<Layers className="w-4 h-4" />}>
           <div className="space-y-4">
            {['regulations', 'flight_ops', 'business_roi', 'drone_specs', 'companies', 'training', 'general'].map(cat => {
              const count = data.query_category_counts[cat] || 0;
              return (
                <div key={cat} className="space-y-1">
                  <div className="flex justify-between text-xs font-medium">
                    <span className="text-slate-600 dark:text-slate-400 capitalize">{cat.replace(/_/g, ' ')}</span>
                    <span className="text-slate-800 dark:text-slate-200">{count}</span>
                  </div>
                  <div className="h-2 bg-slate-100 dark:bg-slate-700/50 rounded-full overflow-hidden">
                    <div 
                      className={`h-full rounded-full bg-indigo-500 transition-all duration-1000`}
                      style={{ width: `${(count / maxCategoryCount) * 100}%` }}
                    />
                  </div>
                </div>
              );
            })}
          </div>
        </ChartSection>
      </div>

      {/* Section 4: Popular Queries */}
      <ChartSection title="Popular Queries" icon={<TrendingUp className="w-4 h-4" />}>
        {data.popular_queries.length > 0 ? (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead className="text-slate-400 font-bold uppercase tracking-wider border-b border-slate-100 dark:border-slate-800">
                <tr>
                  <th className="pb-3 px-2">Query</th>
                  <th className="pb-3 px-2 text-right">Frequency</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-50 dark:divide-slate-800/50">
                {data.popular_queries.map((q, i) => (
                  <tr key={i} className="hover:bg-slate-50 dark:hover:bg-slate-800/30 transition-colors">
                    <td className="py-3 px-2 text-slate-700 dark:text-slate-300 italic">"{q.query}"</td>
                    <td className="py-3 px-2 text-right font-bold text-primary-600">{q.count}x</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        ) : (
          <div className="flex items-center justify-center h-32 text-slate-400 text-xs italic">
            No repeated queries yet
          </div>
        )}
      </ChartSection>

      {/* Section 6: Hourly Distribution */}
      <ChartSection title="Temporal Activity (24h)" icon={<BarChart className="w-4 h-4" />}>
        <div className="flex items-end justify-between h-40 gap-1 pt-4">
          {Object.entries(data.hourly_distribution).map(([hour, count]) => (
            <div key={hour} className="group flex-1 flex flex-col items-center gap-2">
              <div 
                className="w-full bg-primary-100 dark:bg-primary-900/20 group-hover:bg-primary-500 transition-all rounded-t-sm relative"
                style={{ height: `${(count / maxHourCount) * 100}%`, minHeight: '2px' }}
              >
                {count > 0 && (
                  <div className="absolute -top-6 left-1/2 -translate-x-1/2 bg-slate-800 text-white text-[8px] px-1 rounded opacity-0 group-hover:opacity-100 whitespace-nowrap">
                    {count} req
                  </div>
                )}
              </div>
              {['00', '04', '08', '12', '16', '20'].includes(hour) && (
                <span className="text-[8px] text-slate-400 font-mono">{hour}h</span>
              )}
            </div>
          ))}
        </div>
      </ChartSection>

      {/* Section 5: Recent Activity */}
      <ChartSection title="Live Request Log" icon={<History className="w-4 h-4" />}>
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead className="text-slate-400 font-bold uppercase tracking-wider border-b border-slate-100 dark:border-slate-800">
              <tr>
                <th className="pb-3 px-2">Time</th>
                <th className="pb-3 px-2">Query</th>
                <th className="pb-3 px-2">Tool</th>
                <th className="pb-3 px-2">Category</th>
                <th className="pb-3 px-2 text-right">Latency</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-50 dark:divide-slate-800/50">
              {data.recent_queries.map((q, i) => (
                <tr key={i} className="hover:bg-slate-50 dark:hover:bg-slate-800/30 transition-colors">
                  <td className="py-3 px-2 text-slate-500 whitespace-nowrap">
                    {new Date(q.timestamp).toLocaleTimeString([], { hour12: false, hour: '2-digit', minute: '2-digit' })}
                  </td>
                  <td className="py-3 px-2 text-slate-800 dark:text-slate-200 font-medium truncate max-w-[200px]" title={q.query}>
                    {q.query}
                  </td>
                  <td className="py-3 px-2">
                    <span className="px-2 py-0.5 rounded-full bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-400 text-[10px]">
                      {q.tool_used}
                    </span>
                  </td>
                  <td className="py-3 px-2">
                    <span className="capitalize">{q.category}</span>
                  </td>
                  <td className="py-3 px-2 text-right font-mono text-slate-500">
                    {q.response_time_ms}ms
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </ChartSection>

      {/* Section 7: Model Usage */}
      <div className="bg-gradient-to-br from-primary-600 to-indigo-700 rounded-3xl p-6 text-white shadow-xl shadow-primary-500/20">
         <div className="flex items-center gap-3 mb-6">
           <Cpu className="w-6 h-6 opacity-80" />
           <h3 className="text-lg font-bold">LLM Intelligence Origin</h3>
         </div>
         <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {Object.entries(data.model_usage).map(([model, count]) => (
              <div key={model} className="bg-white/10 backdrop-blur-md rounded-2xl p-4 border border-white/10">
                <p className="text-[10px] text-white/60 mb-1 uppercase tracking-widest font-bold">Engine</p>
                <div className="flex justify-between items-end">
                  <h4 className="text-sm font-semibold truncate pr-2">{model}</h4>
                  <span className="text-2xl font-black">{count}</span>
                </div>
              </div>
            ))}
         </div>
      </div>
    </div>
  )
}

const MetricCard = ({ label, value, icon, color, subValue }: any) => (
  <div className="bg-white dark:bg-slate-800 p-5 rounded-3xl border border-slate-100 dark:border-slate-800 shadow-sm transition-all hover:shadow-lg group">
    <div className={`w-10 h-10 ${color} rounded-2xl flex items-center justify-center text-white mb-4 shadow-lg shadow-current/20 group-hover:scale-110 transition-transform`}>
      {icon}
    </div>
    <div className="space-y-1">
      <p className="text-slate-400 text-[10px] font-bold uppercase tracking-wider">{label}</p>
      <h4 className="text-2xl font-bold text-slate-800 dark:text-slate-100 tabular-nums">{value}</h4>
      {subValue && <p className="text-[10px] text-slate-500 truncate">{subValue}</p>}
    </div>
  </div>
)

const ChartSection = ({ title, icon, children }: any) => (
  <div className="bg-white dark:bg-slate-800 p-6 rounded-3xl border border-slate-100 dark:border-slate-800 shadow-sm transition-colors duration-300">
    <div className="flex items-center gap-2 mb-6">
      <div className="p-1.5 bg-slate-50 dark:bg-slate-700 rounded-lg text-primary-500">
        {icon}
      </div>
      <h3 className="text-sm font-bold text-slate-800 dark:text-slate-100 uppercase tracking-tight">{title}</h3>
    </div>
    {children}
  </div>
)

export default DashboardViz
