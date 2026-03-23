import React, { useState } from 'react'
import { ChatMeta } from '../../App'
import { 
  MessageSquare, 
  Zap, 
  TrendingUp, 
  ShieldCheck, 
  Award, 
  BarChart3, 
  ChevronLeft, 
  ChevronRight,
  ChevronDown,
  ChevronUp,
  Plus
} from 'lucide-react'

interface SidebarProps {
  activeTab: string
  setActiveTab: (tab: string) => void
  isOpen: boolean
  setIsOpen: (isOpen: boolean) => void
  chats: ChatMeta[]
  activeChatId: string | null
  setActiveChatId: (id: string | null) => void
}

const menuItems = [
  { id: 'chat', label: 'Chat Assistant', icon: MessageSquare },
  { id: 'flight', label: 'Flight Time', icon: Zap },
  { id: 'roi', label: 'ROI Calculator', icon: TrendingUp },
  { id: 'compliance', label: 'Compliance', icon: ShieldCheck },
  { id: 'recommend', label: 'Recommendation', icon: Award },
  { id: 'analytics', label: 'Analytics', icon: BarChart3 },
]

const Sidebar: React.FC<SidebarProps> = ({ activeTab, setActiveTab, isOpen, setIsOpen, chats, activeChatId, setActiveChatId }) => {
  const [isChatsExpanded, setIsChatsExpanded] = useState(false)

  return (
    <aside 
      className={`
        bg-white dark:bg-slate-900 border-r border-slate-200 dark:border-slate-800 
        transition-all duration-300 ease-in-out flex flex-col z-40 overflow-hidden
        ${isOpen ? 'w-64' : 'w-20'}
        fixed md:relative h-full
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
          <div 
            className="flex justify-between items-center mb-2 cursor-pointer group/header select-none"
            onClick={() => setIsChatsExpanded(!isChatsExpanded)}
          >
            <div className="flex items-center gap-1.5 text-slate-400 group-hover/header:text-slate-600 dark:group-hover/header:text-slate-200 transition-colors">
              {isChatsExpanded ? <ChevronUp className="w-3 h-3" /> : <ChevronDown className="w-3 h-3" />}
              <h4 className="text-[10px] font-bold uppercase tracking-wider">Recent Chats</h4>
            </div>
            <button 
              onClick={(e) => { e.stopPropagation(); setActiveTab('chat'); setActiveChatId(null); }}
              className="text-[10px] bg-primary-100 text-primary-700 hover:bg-primary-200 dark:bg-primary-900/50 dark:text-primary-300 dark:hover:bg-primary-900 px-2 py-1 flex items-center gap-1 rounded-md transition-colors font-semibold shadow-sm"
              title="End chat and start a new one"
            >
              <Plus className="w-3 h-3" /> New
            </button>
          </div>
          
          {isChatsExpanded && (
            <div className="space-y-1 animate-in fade-in slide-in-from-top-1 duration-200 max-h-[40vh] overflow-y-auto pr-1 scrollbar-thin scrollbar-thumb-slate-200 dark:scrollbar-thumb-slate-800">
              {chats.length === 0 && (
                <p className="text-xs text-slate-400 italic px-2">No recent chats</p>
              )}
              {chats.map((chat) => (
                <button 
                  key={chat.chat_id}
                  onClick={() => { setActiveTab('chat'); setActiveChatId(chat.chat_id); }}
                  className={`w-full text-left flex items-center gap-2 p-2 text-xs rounded-lg transition-all truncate
                    ${activeChatId === chat.chat_id 
                      ? 'text-primary-700 bg-primary-50 dark:text-primary-400 dark:bg-primary-900/20 font-semibold' 
                      : 'text-slate-500 hover:text-primary-600 hover:bg-primary-50 dark:hover:bg-primary-900/10'
                    }`}
                  title={chat.title}
                >
                  <MessageSquare className="w-3 h-3 shrink-0 opacity-50" />
                  <span className="truncate">{chat.title}</span>
                </button>
              ))}
            </div>
          )}
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
