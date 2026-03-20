import { XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, AreaChart, Area } from 'recharts'
import { TrendingUp, Battery, Scale, Globe } from 'lucide-react'

const data = [
  { name: 'Month 1', profit: -5000 },
  { name: 'Month 2', profit: -3800 },
  { name: 'Month 3', profit: -2200 },
  { name: 'Month 4', profit: -400 },
  { name: 'Month 5', profit: 1200 },
  { name: 'Month 6', profit: 2800 },
  { name: 'Month 7', profit: 4500 },
]

const DashboardViz = () => {
  return (
    <div className="p-6 space-y-8 animate-in fade-in slide-in-from-bottom-4 duration-700">
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <MetricCard label="ROI Projection" value="+240%" subValue="6 Months" icon={<TrendingUp className="w-4 h-4" />} trend="up" />
        <MetricCard label="Flight Capacity" value="42 min" subValue="Standard LiPo" icon={<Battery className="w-4 h-4" />} />
        <MetricCard label="Max Payload" value="5.2 kg" subValue="Safe Operating" icon={<Scale className="w-4 h-4" />} />
        <MetricCard label="Region Status" value="Green Zone" subValue="NCR Region" icon={<Globe className="w-4 h-4" />} trend="up" />
      </div>

      <div className="bg-white dark:bg-slate-800 p-6 rounded-2xl border border-slate-100 dark:border-slate-800 shadow-sm transition-colors duration-300">
        <h3 className="text-lg font-bold mb-6 text-slate-800 dark:text-slate-100">Cumulative Profit Analysis</h3>
        <div className="h-80 w-full">
          <ResponsiveContainer width="100%" height="100%">
            <AreaChart data={data}>
              <defs>
                <linearGradient id="colorProfit" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#3b82f6" stopOpacity={0.3}/>
                  <stop offset="95%" stopColor="#3b82f6" stopOpacity={0}/>
                </linearGradient>
              </defs>
              <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#E2E8F0" />
              <XAxis dataKey="name" stroke="#94A3B8" fontSize={12} tickLine={false} axisLine={false} />
              <YAxis stroke="#94A3B8" fontSize={12} tickLine={false} axisLine={false} tickFormatter={(v) => `$${v}`} />
              <Tooltip 
                contentStyle={{ backgroundColor: '#1e293b', border: 'none', borderRadius: '12px', color: '#fff' }}
                itemStyle={{ color: '#60a5fa' }}
              />
              <Area type="monotone" dataKey="profit" stroke="#3b82f6" strokeWidth={3} fillOpacity={1} fill="url(#colorProfit)" />
            </AreaChart>
          </ResponsiveContainer>
        </div>
      </div>
    </div>
  )
}

const MetricCard = ({ label, value, subValue, icon, trend }: any) => (
  <div className="bg-white dark:bg-slate-800 p-4 rounded-2xl border border-slate-100 dark:border-slate-800 shadow-xs transition-all hover:shadow-md">
    <div className="flex items-center gap-2 text-slate-400 text-xs font-medium mb-1 capitalize">
      {icon}
      {label}
    </div>
    <div className="flex items-baseline justify-between">
      <h4 className="text-2xl font-bold text-slate-800 dark:text-slate-100">{value}</h4>
      {trend && (
        <span className="text-[10px] font-bold text-green-500 bg-green-50 dark:bg-green-900/20 px-1.5 py-0.5 rounded-full">
           +12%
        </span>
      )}
    </div>
    <p className="text-xs text-slate-400 mt-1">{subValue}</p>
  </div>
)

export default DashboardViz
