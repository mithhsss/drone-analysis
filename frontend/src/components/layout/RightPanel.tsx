import React, { useState, useEffect } from 'react'
import { Calculator, Shield, Info, HelpCircle, Download, FileText, Award, Loader2 } from 'lucide-react'

// Subcomponent workaround for ROI icon
const TrendingUp = ({ className }: { className?: string }) => (
  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className={className}>
    <polyline points="23 6 13.5 15.5 8.5 10.5 1 18" />
    <polyline points="17 6 23 6 23 12" />
  </svg>
)

interface RightPanelProps {
  activeTab: string
}

const RightPanel: React.FC<RightPanelProps> = ({ activeTab }) => {
  const [loading, setLoading] = useState(false)
  const [result, setResult] = useState<any>(null)
  const [error, setError] = useState<string | null>(null)

  // Flight Time State
  const [ftBattery, setFtBattery] = useState(15000)
  const [ftWeight, setFtWeight] = useState(3.5)
  const [ftPayload, setFtPayload] = useState(1.0)
  const [ftWind, setFtWind] = useState(5.0)
  const [ftTemp, setFtTemp] = useState(28.0)

  // ROI State
  const [roiUsecase, setRoiUsecase] = useState("agriculture")
  const [roiInitial, setRoiInitial] = useState(500000)
  const [roiOpCost, setRoiOpCost] = useState(25000)
  const [roiRevenue, setRoiRevenue] = useState(80000)
  const [roiMonths, setRoiMonths] = useState(0)

  // Compliance State
  const [compWeight, setCompWeight] = useState(1.5)
  const [compType, setCompType] = useState("commercial")
  const [compLocation, setCompLocation] = useState("Delhi")
  const [compLicence, setCompLicence] = useState(false)

  // Recommend State
  const [recBudget, setRecBudget] = useState(500000)
  const [recUsecase, setRecUsecase] = useState("agriculture")
  const [recPayload, setRecPayload] = useState(2.0)
  const [recFlightTime, setRecFlightTime] = useState(20.0)
  const [recIndoor, setRecIndoor] = useState(false)

  // Clear results if user changes the active tabs
  useEffect(() => {
    setResult(null)
    setError(null)
  }, [activeTab])

  // Universal executor function
  const executeTool = async (path: string, payload: any) => {
    setLoading(true)
    setResult(null)
    setError(null)
    try {
      const res = await fetch(`http://localhost:8000/api/v1${path}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.error || "Failed to execute API")
      if (data.success) {
        setResult(data.data)
      } else {
        throw new Error(data.error || "Execution failed entirely")
      }
    } catch(err: any) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  const renderResult = () => {
    if (loading) return (
       <div className="flex items-center gap-2 p-4 text-primary-600 dark:text-primary-400 bg-primary-50 dark:bg-slate-800 rounded-lg shadow-inner mt-4">
         <Loader2 className="w-5 h-5 animate-spin" />
         <span className="font-semibold text-sm">Processing Intelligence Model...</span>
       </div>
    );
    if (error) return (
       <div className="p-4 mt-4 text-xs bg-red-50 dark:bg-red-900/40 text-red-600 dark:text-red-400 rounded-lg shadow border border-red-200 dark:border-red-900">
          <span className="font-bold block mb-1">Execution Failed</span>
          {error}
       </div>
    );
    if (result) return (
       <div className="mt-6 p-4 bg-slate-100 dark:bg-slate-900 rounded-lg border border-slate-200 dark:border-slate-700 shadow-inner">
         <h4 className="text-sm font-bold text-slate-700 dark:text-slate-300 mb-2 uppercase tracking-wide">Analysis Result</h4>
         <div className="space-y-2 text-sm text-slate-800 dark:text-slate-200">
           {Object.entries(result).map(([key, val]) => (
             <div key={key} className="flex flex-col border-b border-slate-200/50 dark:border-slate-800/50 pb-2 last:border-0 last:pb-0">
               <span className="font-semibold opacity-70 capitalize text-xs">{key.replace(/_/g, " ")}</span>
               <span className="font-medium whitespace-pre-wrap">{typeof val === 'object' ? JSON.stringify(val) : String(val)}</span>
             </div>
           ))}
         </div>
       </div>
    );
    return null;
  }

  const renderContent = () => {
    switch (activeTab) {
      case 'flight':
        return (
          <div className="space-y-4">
            <div className="flex items-center gap-2 text-primary-600 dark:text-primary-400 font-semibold mb-2">
              <Calculator className="w-5 h-5" />
              <span>Flight Time Parameters</span>
            </div>
            <div className="space-y-3">
               <div>
                  <label className="block text-xs font-semibold mb-1 opacity-80 uppercase tracking-wider">Battery Capacity (mAh)</label>
                  <input type="number" value={ftBattery} onChange={e => setFtBattery(Number(e.target.value))} className="w-full p-2 bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-lg focus:ring-2 focus:ring-primary-500 outline-none text-sm transition-all" />
               </div>
               <div>
                  <label className="block text-xs font-semibold mb-1 opacity-80 uppercase tracking-wider">Drone Weight (kg)</label>
                  <input type="number" step="0.1" value={ftWeight} onChange={e => setFtWeight(Number(e.target.value))} className="w-full p-2 bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-lg focus:ring-2 focus:ring-primary-500 outline-none text-sm transition-all" />
               </div>
               <div>
                  <label className="block text-xs font-semibold mb-1 opacity-80 uppercase tracking-wider">Payload Weight (kg)</label>
                  <input type="number" step="0.1" value={ftPayload} onChange={e => setFtPayload(Number(e.target.value))} className="w-full p-2 bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-lg focus:ring-2 focus:ring-primary-500 outline-none text-sm transition-all" />
               </div>
               <div>
                  <label className="block text-xs font-semibold mb-1 opacity-80 uppercase tracking-wider">Wind Speed (km/h)</label>
                  <input type="number" step="0.1" value={ftWind} onChange={e => setFtWind(Number(e.target.value))} className="w-full p-2 bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-lg focus:ring-2 focus:ring-primary-500 outline-none text-sm transition-all" />
               </div>
               <div>
                  <label className="block text-xs font-semibold mb-1 opacity-80 uppercase tracking-wider">Temperature (°C)</label>
                  <input type="number" step="0.1" value={ftTemp} onChange={e => setFtTemp(Number(e.target.value))} className="w-full p-2 bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-lg focus:ring-2 focus:ring-primary-500 outline-none text-sm transition-all" />
               </div>
               
               <button 
                onClick={() => executeTool('/calculate/flight-time', {
                  battery_mah: ftBattery,
                  drone_weight_kg: ftWeight,
                  payload_kg: ftPayload,
                  wind_speed_kmh: ftWind,
                  temperature_celsius: ftTemp
                })}
                disabled={loading}
                className="w-full bg-primary-600 hover:bg-primary-700 text-white font-semibold py-2.5 rounded-lg shadow-lg shadow-primary-500/20 disabled:scale-100 disabled:opacity-50 transition-all active:scale-95"
               >
                 Forecast Flight Efficiency
               </button>
               {renderResult()}
            </div>
          </div>
        )
      case 'roi':
        return (
          <div className="space-y-4">
            <div className="flex items-center gap-2 text-primary-600 dark:text-primary-400 font-semibold mb-2">
              <TrendingUp className="w-5 h-5" />
              <span>ROI Input Data</span>
            </div>
            <div className="space-y-3">
               <div>
                  <label className="block text-xs font-semibold mb-1 opacity-80 uppercase tracking-wider">Use Case</label>
                  <select value={roiUsecase} onChange={e => setRoiUsecase(e.target.value)} className="w-full p-2 bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-lg focus:ring-2 text-sm focus:ring-primary-500 outline-none transition-all">
                    <option value="agriculture">Agriculture</option>
                    <option value="mapping">Mapping</option>
                    <option value="inspection">Inspection</option>
                    <option value="delivery">Delivery</option>
                  </select>
               </div>
               <div>
                  <label className="block text-xs font-semibold mb-1 opacity-80 uppercase tracking-wider">Drone Setup Cost (INR)</label>
                  <input type="number" step="1000" value={roiInitial} onChange={e => setRoiInitial(Number(e.target.value))} className="w-full p-2 bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-lg focus:ring-2 text-sm focus:ring-primary-500 outline-none transition-all" />
               </div>
               <div>
                  <label className="block text-xs font-semibold mb-1 opacity-80 uppercase tracking-wider">Monthly Op. Cost (INR)</label>
                  <input type="number" step="1000" value={roiOpCost} onChange={e => setRoiOpCost(Number(e.target.value))} className="w-full p-2 bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-lg focus:ring-2 text-sm focus:ring-primary-500 outline-none transition-all" />
               </div>
               <div>
                  <label className="block text-xs font-semibold mb-1 opacity-80 uppercase tracking-wider">Monthly Revenue Target (INR)</label>
                  <input type="number" step="1000" value={roiRevenue} onChange={e => setRoiRevenue(Number(e.target.value))} className="w-full p-2 bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-lg focus:ring-2 text-sm focus:ring-primary-500 outline-none transition-all" />
               </div>
               <div>
                  <label className="block text-xs font-semibold mb-1 opacity-80 uppercase tracking-wider">Financing Period (Months)</label>
                  <input type="number" value={roiMonths} onChange={e => setRoiMonths(Number(e.target.value))} className="w-full p-2 bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-lg focus:ring-2 text-sm focus:ring-primary-500 outline-none transition-all" />
               </div>
               <button 
                onClick={() => executeTool('/calculate/roi', {
                  use_case: roiUsecase,
                  drone_cost_inr: roiInitial,
                  monthly_operational_cost_inr: roiOpCost,
                  monthly_revenue_inr: roiRevenue,
                  financing_months: roiMonths
                })}
                disabled={loading}
                className="w-full bg-primary-600 hover:bg-primary-700 text-white font-semibold py-2.5 rounded-lg shadow-lg disabled:scale-100 disabled:opacity-50 shadow-primary-500/20 transition-all active:scale-95"
               >
                 Compute ROI Returns
               </button>
               {renderResult()}
            </div>
          </div>
        )
      case 'compliance':
        return (
          <div className="space-y-4">
            <div className="flex items-center gap-2 text-primary-600 dark:text-primary-400 font-semibold mb-2">
              <Shield className="w-5 h-5" />
              <span>Compliance Matrix</span>
            </div>
            <div className="space-y-3">
               <div>
                  <label className="block text-xs font-semibold mb-1 opacity-80 uppercase tracking-wider">Drone Weight (kg)</label>
                  <input type="number" step="0.1" value={compWeight} onChange={e => setCompWeight(Number(e.target.value))} className="w-full p-2 text-sm bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-lg focus:ring-2 focus:ring-primary-500 outline-none transition-all" />
               </div>
               <div>
                  <label className="block text-xs font-semibold mb-1 opacity-80 uppercase tracking-wider">Mission Location</label>
                  <input type="text" value={compLocation} onChange={e => setCompLocation(e.target.value)} className="w-full p-2 text-sm bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-lg focus:ring-2 focus:ring-primary-500 outline-none transition-all" />
               </div>
               <div>
                  <label className="block text-xs font-semibold mb-1 opacity-80 uppercase tracking-wider">Sector Protocol</label>
                  <select value={compType} onChange={e => setCompType(e.target.value)} className="w-full p-2 text-sm bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-lg focus:ring-2 focus:ring-primary-500 outline-none transition-all">
                    <option value="commercial">Commercial</option>
                    <option value="recreational">Recreational</option>
                    <option value="research">Research / Education</option>
                    <option value="defence">Defence</option>
                  </select>
               </div>
               <div className="flex items-center gap-2 p-2 border border-slate-200 dark:border-slate-800 bg-slate-50 dark:bg-slate-900 rounded-lg">
                  <input type="checkbox" id="pilotLicence" checked={compLicence} onChange={e => setCompLicence(e.target.checked)} className="w-4 h-4 text-primary-600 focus:ring-primary-500 rounded border-slate-300 dark:border-slate-600" />
                  <label htmlFor="pilotLicence" className="text-xs font-semibold opacity-80 uppercase tracking-wider cursor-pointer select-none">Has DGCA Pilot Licence?</label>
               </div>
               <button 
                onClick={() => executeTool('/check/compliance', {
                  drone_weight_kg: compWeight,
                  use_type: compType,
                  location: compLocation,
                  has_remote_pilot_licence: compLicence
                })}
                disabled={loading}
                className="w-full bg-primary-600 hover:bg-primary-700 text-white font-semibold py-2.5 rounded-lg disabled:scale-100 disabled:opacity-50 shadow-lg shadow-primary-500/20 transition-all active:scale-95"
               >
                 Run DGCA Compliance Check
               </button>
               {renderResult()}
            </div>
          </div>
        )
      case 'recommend':
        return (
          <div className="space-y-4">
            <div className="flex items-center gap-2 text-primary-600 dark:text-primary-400 font-semibold mb-2">
              <Award className="w-5 h-5" />
              <span>Drone Recommender</span>
            </div>
            <div className="space-y-3">
               <div>
                  <label className="block text-xs font-semibold mb-1 opacity-80 uppercase tracking-wider">Budget Limit (INR)</label>
                  <input type="number" step="1000" value={recBudget} onChange={e => setRecBudget(Number(e.target.value))} className="w-full p-2 text-sm bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-lg focus:ring-2 focus:ring-primary-500 outline-none transition-all" />
               </div>
               <div>
                  <label className="block text-xs font-semibold mb-1 opacity-80 uppercase tracking-wider">Primary Use Case</label>
                  <select value={recUsecase} onChange={e => setRecUsecase(e.target.value)} className="w-full p-2 text-sm bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-lg focus:ring-2 focus:ring-primary-500 outline-none transition-all">
                    <option value="agriculture">Agriculture & Spraying</option>
                    <option value="mapping">Surveying & Mapping</option>
                    <option value="inspection">Industrial Inspection</option>
                    <option value="photography">Cinematography</option>
                  </select>
               </div>
               <div>
                  <label className="block text-xs font-semibold mb-1 opacity-80 uppercase tracking-wider">Req. Payload (kg)</label>
                  <input type="number" step="0.5" value={recPayload} onChange={e => setRecPayload(Number(e.target.value))} className="w-full p-2 text-sm bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-lg focus:ring-2 focus:ring-primary-500 outline-none transition-all" />
               </div>
               <div>
                  <label className="block text-xs font-semibold mb-1 opacity-80 uppercase tracking-wider">Req. Flight Time (min)</label>
                  <input type="number" step="1" value={recFlightTime} onChange={e => setRecFlightTime(Number(e.target.value))} className="w-full p-2 text-sm bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-lg focus:ring-2 focus:ring-primary-500 outline-none transition-all" />
               </div>
               <div className="flex items-center gap-2 p-2 border border-slate-200 dark:border-slate-800 bg-slate-50 dark:bg-slate-900 rounded-lg">
                  <input type="checkbox" id="indoorNav" checked={recIndoor} onChange={e => setRecIndoor(e.target.checked)} className="w-4 h-4 text-primary-600 focus:ring-primary-500 rounded border-slate-300 dark:border-slate-600" />
                  <label htmlFor="indoorNav" className="text-xs font-semibold opacity-80 uppercase tracking-wider cursor-pointer select-none">Requires Indoor Flight?</label>
               </div>
               <button 
                onClick={() => executeTool('/recommend/drone', {
                  budget_inr: recBudget,
                  use_case: recUsecase,
                  payload_required_kg: recPayload,
                  flight_time_required_min: recFlightTime,
                  indoor_use: recIndoor
                })}
                disabled={loading}
                className="w-full bg-primary-600 hover:bg-primary-700 text-white font-semibold py-2.5 rounded-lg disabled:scale-100 disabled:opacity-50 shadow-lg shadow-primary-500/20 transition-all active:scale-95"
               >
                 Discover Optimal Drones
               </button>
               {renderResult()}
            </div>
          </div>
        )
      default:
        return (
          <div className="space-y-4 flex flex-col items-center justify-center p-8 text-center h-full">
            <div className="w-16 h-16 bg-slate-100 dark:bg-slate-800 rounded-full flex items-center justify-center mb-4 text-slate-400">
               <HelpCircle className="w-8 h-8" />
            </div>
            <h3 className="font-semibold text-slate-700 dark:text-slate-300">Tool Selection Panel</h3>
            <p className="text-sm text-slate-500">Select a tool from the left sidebar to access specific inputs and calculations here.</p>
          </div>
        )
    }
  }

  return (
    <div className="p-6 h-full flex flex-col">
      <div className="flex-1">
        {renderContent()}
      </div>

      <div className="mt-8 space-y-3 pt-6 border-t border-slate-100 dark:border-slate-800">
        <div className="grid grid-cols-2 gap-2">
           <button className="flex items-center justify-center gap-2 p-2 text-xs font-medium border border-slate-200 dark:border-slate-800 rounded-lg hover:bg-slate-50 dark:hover:bg-slate-800 transition-all">
              <FileText className="w-3.5 h-3.5" />
              Export PDF
           </button>
           <button className="flex items-center justify-center gap-2 p-2 text-xs font-medium border border-slate-200 dark:border-slate-800 rounded-lg hover:bg-slate-50 dark:hover:bg-slate-800 transition-all">
              <Download className="w-3.5 h-3.5" />
              Export CSV
           </button>
        </div>
        <div className="flex items-center gap-2 text-primary-700 dark:text-primary-300 font-medium mb-2 text-sm">
           <Info className="w-4 h-4" />
           <span>Quick Tip</span>
        </div>
        <p className="text-xs text-slate-600 dark:text-slate-400 leading-relaxed">
          Results are processed using India's DigitalSky & DGCA guidelines (Version 2.1). Always verify mission critical data.
        </p>
      </div>
    </div>
  )
}

export default RightPanel
