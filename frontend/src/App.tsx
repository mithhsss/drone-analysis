import { useState, useEffect, useCallback } from 'react'
import Navbar from './components/layout/Navbar'
import Sidebar from './components/layout/Sidebar'
import ChatAssistant from './components/chat/ChatAssistant'
import RightPanel from './components/layout/RightPanel'
import DashboardViz from './components/viz/DashboardViz'

export interface ChatMeta {
  chat_id: string;
  title: string;
  updated_at: string;
}

function App() {
  const [isDarkMode, setIsDarkMode] = useState(false)
  const [activeTab, setActiveTab] = useState('chat')
  const [isSidebarOpen, setIsSidebarOpen] = useState(true)
  
  // Memory State Lifting
  const [chats, setChats] = useState<ChatMeta[]>([])
  const [activeChatId, setActiveChatId] = useState<string | null>(null)

  const fetchChats = useCallback(async () => {
    try {
      const res = await fetch("http://localhost:8000/api/chats")
      if (res.ok) {
        const data = await res.json()
        setChats(data.chats || [])
      }
    } catch (e) {
      console.error("Failed to load chat history payload:", e)
    }
  }, [])

  // Auto-pull Sidebar entries whenever App mounts
  useEffect(() => {
    fetchChats()
  }, [fetchChats])

  useEffect(() => {
    if (isDarkMode) {
      document.documentElement.classList.add('dark')
    } else {
      document.documentElement.classList.remove('dark')
    }
  }, [isDarkMode])

  const toggleDarkMode = () => setIsDarkMode(!isDarkMode)

  return (
    <div className="min-h-screen bg-slate-50 dark:bg-slate-900 text-slate-900 dark:text-slate-100 transition-colors duration-300">
      <Navbar 
        isDarkMode={isDarkMode} 
        toggleDarkMode={toggleDarkMode} 
        toggleSidebar={() => setIsSidebarOpen(!isSidebarOpen)} 
      />
      
      <div className="flex h-[calc(100vh-64px)] overflow-hidden">
        <Sidebar 
          activeTab={activeTab} 
          setActiveTab={setActiveTab} 
          isOpen={isSidebarOpen} 
          setIsOpen={setIsSidebarOpen}
          chats={chats}
          activeChatId={activeChatId}
          setActiveChatId={setActiveChatId}
          fetchChats={fetchChats}
        />
        
        <main className={`flex-1 flex flex-col md:flex-row overflow-hidden transition-all duration-300 ${isSidebarOpen ? 'md:ml-0' : 'ml-0'}`}>
          <div className="flex-1 overflow-hidden relative overflow-y-auto">
            {activeTab === 'chat' || activeTab === 'flight' || activeTab === 'roi' || activeTab === 'compliance' || activeTab === 'recommend' ? (
              <ChatAssistant 
                activeTab={activeTab} 
                activeChatId={activeChatId}
                setActiveChatId={setActiveChatId}
                fetchChats={fetchChats}
              />
            ) : (
              <DashboardViz />
            )}
            
            {/* Show Analytics on top or overlay if needed, currently substituting central area for non-chat tools if they have visualizations */}
            {activeTab === 'analytics' && (
               <div className="absolute inset-0 bg-slate-50 dark:bg-slate-900 z-10 overflow-y-auto">
                  <DashboardViz />
               </div>
            )}
          </div>
          
          <div className="w-full md:w-80 lg:w-96 border-l border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-800/50 overflow-y-auto">
            <RightPanel activeTab={activeTab} />
          </div>
        </main>
      </div>
    </div>
  )
}

export default App
