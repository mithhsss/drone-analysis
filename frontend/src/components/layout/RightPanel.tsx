import { Calculator, Shield, Info, HelpCircle, Download, FileText, Award } from 'lucide-react'

interface RightPanelProps {
  activeTab: string
}

const RightPanel: React.FC<RightPanelProps> = ({ activeTab }) => {
  const renderContent = () => {
    switch (activeTab) {
      case 'flight':
        return (
          <div className="space-y-6">
            <div className="flex items-center gap-2 text-primary-600 dark:text-primary-400 font-semibold mb-2">
              <Calculator className="w-5 h-5" />
              <span>Flight Time Parameters</span>
            </div>
            <div className="space-y-4">
               <div>
                  <label className="block text-sm font-medium mb-1 opacity-70">Battery Capacity (mAh)</label>
                  <input type="number" defaultValue={5000} className="w-full p-2.5 bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-lg focus:ring-2 focus:ring-primary-500 outline-none transition-all" />
               </div>
               <div>
                  <label className="block text-sm font-medium mb-1 opacity-70">Drone Weight (g)</label>
                  <input type="number" defaultValue={1500} className="w-full p-2.5 bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-lg focus:ring-2 focus:ring-primary-500 outline-none transition-all" />
               </div>
               <div>
                  <label className="block text-sm font-medium mb-1 opacity-70">Payload (g)</label>
                  <input type="number" defaultValue={500} className="w-full p-2.5 bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-lg focus:ring-2 focus:ring-primary-500 outline-none transition-all" />
               </div>
               <div>
                  <label className="block text-sm font-medium mb-1 opacity-70">Weather Conditions</label>
                  <select className="w-full p-2.5 bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-lg focus:ring-2 focus:ring-primary-500 outline-none transition-all">
                    <option>Clear & Calm</option>
                    <option>Moderate Wind</option>
                    <option>High Wind</option>
                  </select>
               </div>
               <button className="w-full bg-primary-600 hover:bg-primary-700 text-white font-semibold py-2.5 rounded-lg shadow-lg shadow-primary-500/20 transition-all active:scale-95">
                 Calculate Flight Time
               </button>
            </div>
          </div>
        )
      case 'roi':
        return (
          <div className="space-y-6">
            <div className="flex items-center gap-2 text-primary-600 dark:text-primary-400 font-semibold mb-2">
              <TrendingUp className="w-5 h-5" />
              <span>ROI Input Data</span>
            </div>
            <div className="space-y-4">
               <div>
                  <label className="block text-sm font-medium mb-1 opacity-70">Initial Investment ($)</label>
                  <input type="number" defaultValue={10000} className="w-full p-2.5 bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-lg focus:ring-2 focus:ring-primary-500 outline-none transition-all" />
               </div>
               <div>
                  <label className="block text-sm font-medium mb-1 opacity-70">Monthly Operatinal Cost ($)</label>
                  <input type="number" defaultValue={1500} className="w-full p-2.5 bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-lg focus:ring-2 focus:ring-primary-500 outline-none transition-all" />
               </div>
               <div>
                  <label className="block text-sm font-medium mb-1 opacity-70">Expected Monthly Revenue ($)</label>
                  <input type="number" defaultValue={4000} className="w-full p-2.5 bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-lg focus:ring-2 focus:ring-primary-500 outline-none transition-all" />
               </div>
               <button className="w-full bg-primary-600 hover:bg-primary-700 text-white font-semibold py-2.5 rounded-lg shadow-lg shadow-primary-500/20 transition-all active:scale-95">
                 Generate ROI Report
               </button>
            </div>
          </div>
        )
      case 'compliance':
        return (
          <div className="space-y-6">
            <div className="flex items-center gap-2 text-primary-600 dark:text-primary-400 font-semibold mb-2">
              <Shield className="w-5 h-5" />
              <span>Compliance Checker</span>
            </div>
            <div className="space-y-4">
               <div>
                  <label className="block text-sm font-medium mb-1 opacity-70">Drone Type</label>
                  <select className="w-full p-2.5 bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-lg focus:ring-2 focus:ring-primary-500 outline-none transition-all">
                    <option>Nano (&lt; 250g)</option>
                    <option>Micro (250g - 2kg)</option>
                    <option>Small (2kg - 25kg)</option>
                    <option>Medium (25kg - 150kg)</option>
                  </select>
               </div>
               <div>
                  <label className="block text-sm font-medium mb-1 opacity-70">Mission Location</label>
                  <input type="text" placeholder="Coordinates or City..." className="w-full p-2.5 bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-lg focus:ring-2 focus:ring-primary-500 outline-none transition-all" />
               </div>
               <div>
                  <label className="block text-sm font-medium mb-1 opacity-70">Use Case</label>
                  <select className="w-full p-2.5 bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-lg focus:ring-2 focus:ring-primary-500 outline-none transition-all">
                    <option>Photography</option>
                    <option>Agriculture</option>
                    <option>Surveillance</option>
                    <option>Delivery</option>
                  </select>
               </div>
               <button className="w-full bg-primary-600 hover:bg-primary-700 text-white font-semibold py-2.5 rounded-lg shadow-lg shadow-primary-500/20 transition-all active:scale-95">
                 Run Compliance Check
               </button>
            </div>
          </div>
        )
      case 'recommend':
        return (
          <div className="space-y-6">
            <div className="flex items-center gap-2 text-primary-600 dark:text-primary-400 font-semibold mb-2">
              <Award className="w-5 h-5" />
              <span>Drone Recommendation</span>
            </div>
            <div className="space-y-4">
               <div>
                  <label className="block text-sm font-medium mb-1 opacity-70">Budget Range ($)</label>
                  <select className="w-full p-2.5 bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-lg focus:ring-2 focus:ring-primary-500 outline-none transition-all">
                    <option>$500 - $2,000</option>
                    <option>$2,000 - $10,000</option>
                    <option>$10,000+</option>
                  </select>
               </div>
               <div>
                  <label className="block text-sm font-medium mb-1 opacity-70">Primary Use Case</label>
                  <select className="w-full p-2.5 bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-lg focus:ring-2 focus:ring-primary-500 outline-none transition-all">
                    <option>Agriculture Spraying</option>
                    <option>Cinematography</option>
                    <option>Land Mapping</option>
                    <option>Industrial Inspection</option>
                  </select>
               </div>
               <button className="w-full bg-primary-600 hover:bg-primary-700 text-white font-semibold py-2.5 rounded-lg shadow-lg shadow-primary-500/20 transition-all active:scale-95">
                 Get Recommendations
               </button>
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

      <div className="mt-auto space-y-3">
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

// Subcomponent workaround for ROI icon
const TrendingUp = ({ className }: { className?: string }) => (
  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className={className}>
    <polyline points="23 6 13.5 15.5 8.5 10.5 1 18" />
    <polyline points="17 6 23 6 23 12" />
  </svg>
)

export default RightPanel
