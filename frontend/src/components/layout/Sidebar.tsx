import React from 'react'
import { 
  MessageSquare, 
  Zap, 
  TrendingUp, 
  ShieldCheck, 
  Award, 
  BarChart3, 
  ChevronLeft, 
  ChevronRight 
} from 'lucide-react'

interface SidebarProps {
  activeTab: string
  setActiveTab: (tab: string) => void
  isOpen: boolean
  setIsOpen: (isOpen: boolean) => void
}

const menuItems = [
  { id: 'chat', label: 'Chat Assistant', icon: MessageSquare },
  { id: 'flight', label: 'Flight Time', icon: Zap },
  { id: 'roi', label: 'ROI Calculator', icon: TrendingUp },
  { id: 'compliance', label: 'Compliance', icon: ShieldCheck },
  { id: 'recommend', label: 'Recommendation', icon: Award },
  { id: 'analytics', label: 'Analytics', icon: BarChart3 },
]

const Sidebar: React.FC<SidebarProps> = ({ activeTab, setActiveTab, isOpen, setIsOpen }) => {
  return (
    <aside 
      className={`
        bg-white dark:bg-slate-900 border-r border-slate-200 dark:border-slate-800 
        transition-all duration-300 ease-in-out flex flex-col z-40
        ${isOpen ? 'w-64' : 'w-20'}
        fixed h-full md:relative
        ${isOpen ? 'translate-x-0' : '-translate-x-full md:translate-x-0'}
      `}
    >
      <div className="p-4 flex-1 overflow-y-auto space-y-2 py-6">
        {menuItems.map((item) => {
          const Icon = item.icon
          const isActive = activeTab === item.id
          
          return (
            <button
              key={item.id}
              onClick={() => setActiveTab(item.id)}
              className={`
                flex items-center gap-3 w-full p-3 rounded-xl transition-all group
                ${isActive 
                  ? 'bg-primary-50 dark:bg-primary-900/30 text-primary-600 dark:text-primary-400 font-semibold shadow-sm ring-1 ring-primary-100 dark:ring-primary-900/50' 
                  : 'text-slate-500 hover:text-slate-900 dark:hover:text-slate-100 hover:bg-slate-50 dark:hover:bg-slate-800'
                }
              `}
              title={item.label}
            >
              <Icon className={`w-5 h-5 flex-shrink-0 transition-transform ${isActive ? 'scale-110' : 'group-hover:scale-110'}`} />
              <span className={`whitespace-nowrap transition-opacity duration-200 ${isOpen ? 'opacity-100' : 'opacity-0 md:hidden'}`}>
                {item.label}
              </span>
            </button>
          )
        })}
      </div>

      <div className="p-4 border-t border-slate-100 dark:border-slate-800">
        <div className={`mb-4 px-2 transition-opacity duration-200 ${isOpen ? 'opacity-100' : 'opacity-0 md:hidden'}`}>
          <h4 className="text-[10px] font-bold text-slate-400 uppercase tracking-wider mb-2">Recent Chats</h4>
          <div className="space-y-1">
            {['Regulatory Query #1', 'Flight ROI Analysis', 'Compliance NCR'].map((chat, i) => (
              <button key={i} className="w-full text-left p-2 text-xs text-slate-500 hover:text-primary-600 hover:bg-primary-50 dark:hover:bg-primary-900/10 rounded-lg transition-all truncate">
                {chat}
              </button>
            ))}
          </div>
        </div>
        
        <button 
          onClick={() => setIsOpen(!isOpen)}
          className="flex items-center justify-center w-full p-2 text-slate-400 hover:text-slate-600 dark:hover:text-slate-200 hover:bg-slate-50 dark:hover:bg-slate-800 rounded-lg transition-colors"
        >
          {isOpen ? <ChevronLeft className="w-5 h-5" /> : <ChevronRight className="w-5 h-5" />}
        </button>
      </div>
    </aside>
  )
}

export default Sidebar
