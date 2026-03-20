import React, { useState, useRef, useEffect } from 'react'
import { Send, User, Bot, Loader2, BookOpen, ExternalLink } from 'lucide-react'

interface Message {
  id: string
  role: 'user' | 'assistant'
  content: string
  sources?: { title: string; link: string; snippet: string }[]
  timestamp: Date
}

interface ChatAssistantProps {
  activeTab: string
}

const ChatAssistant: React.FC<ChatAssistantProps> = () => {
  const [messages, setMessages] = useState<Message[]>([
    {
      id: '1',
      role: 'assistant',
      content: 'Hello! I am your Indian Drone Intelligence Assistant. How can I help you today? You can ask about drone regulations, technical specs, or business ROI.',
      timestamp: new Date()
    }
  ])
  const [input, setInput] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const messagesEndRef = useRef<HTMLDivElement>(null)

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  useEffect(scrollToBottom, [messages, isLoading])

  const handleSend = async () => {
    if (!input.trim()) return

    const userMsg: Message = {
      id: Date.now().toString(),
      role: 'user',
      content: input,
      timestamp: new Date()
    }

    setMessages(prev => [...prev, userMsg])
    setInput('')
    setIsLoading(true)

    // Call backend API
    try {
      const response = await fetch('http://localhost:8000/api/chat/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: input })
      });

      if (!response.ok) throw new Error('API request failed');

      const data = await response.json();
      
      const assistantMsg: Message = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: data.answer,
        sources: data.sources,
        timestamp: new Date()
      }
      setMessages(prev => [...prev, assistantMsg])
    } catch (error) {
       console.error("Chat API Error:", error);
       setMessages(prev => [...prev, {
         id: (Date.now() + 1).toString(),
         role: 'assistant',
         content: 'Sorry, I am currently unable to connect to the backend server. Please ensure the API is running.',
         timestamp: new Date()
       }]);
    } finally {
       setIsLoading(false)
    }
  }

  return (
    <div className="flex flex-col h-full bg-slate-50 dark:bg-slate-900/50">
      <div className="flex-1 overflow-y-auto p-4 md:p-6 space-y-6">
        {messages.map((m) => (
          <div key={m.id} className={`flex ${m.role === 'user' ? 'justify-end' : 'justify-start'}`}>
            <div className={`flex gap-3 max-w-[85%] ${m.role === 'user' ? 'flex-row-reverse' : 'flex-row'}`}>
              <div className={`w-8 h-8 rounded-full flex items-center justify-center flex-shrink-0 ${m.role === 'user' ? 'bg-primary-600' : 'bg-slate-200 dark:bg-slate-800'}`}>
                {m.role === 'user' ? <User className="w-5 h-5 text-white" /> : <Bot className="w-5 h-5 text-primary-500" />}
              </div>
              
              <div className="space-y-2">
                <div className={`p-4 rounded-2xl shadow-sm leading-relaxed ${
                  m.role === 'user' 
                    ? 'bg-primary-600 text-white rounded-tr-none' 
                    : 'bg-white dark:bg-slate-800 border border-slate-100 dark:border-slate-800 text-slate-800 dark:text-slate-200 rounded-tl-none'
                }`}>
                  {m.content}
                </div>
                
                {m.sources && (
                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-2 pt-2">
                    {m.sources.map((s, i) => (
                      <div key={i} className="p-3 bg-white/50 dark:bg-slate-800/50 border border-slate-200 dark:border-slate-700 rounded-xl text-xs group hover:border-primary-300 dark:hover:border-primary-700 transition-all">
                        <div className="flex items-center justify-between mb-1">
                          <span className="font-semibold text-slate-700 dark:text-slate-300 flex items-center gap-1">
                            <BookOpen className="w-3 h-3 text-primary-500" />
                            {s.title}
                          </span>
                          <ExternalLink className="w-3 h-3 text-slate-400 opacity-0 group-hover:opacity-100 transition-opacity" />
                        </div>
                        <p className="text-slate-500 dark:text-slate-400 line-clamp-2">"{s.snippet}"</p>
                      </div>
                    ))}
                  </div>
                )}
                
                <span className="text-[10px] text-slate-400 block px-1">
                   {m.timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                </span>
              </div>
            </div>
          </div>
        ))}
        {isLoading && (
          <div className="flex justify-start">
            <div className="flex gap-3 items-center text-slate-400 text-sm italic">
              <div className="w-8 h-8 rounded-full bg-slate-100 dark:bg-slate-800 flex items-center justify-center animate-pulse">
                <Bot className="w-5 h-5" />
              </div>
              <span>Assistant is typing...</span>
            </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      <div className="p-4 border-t border-slate-200 dark:border-slate-800 bg-white/80 dark:bg-slate-900/80 backdrop-blur-md">
        <div className="max-w-4xl mx-auto flex gap-3">
          <div className="flex-1 relative">
            <input
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={(e) => e.key === 'Enter' && handleSend()}
              placeholder="Ask about drones, regulations, or business..."
              className="w-full p-3.5 pr-12 bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-2xl focus:ring-2 focus:ring-primary-500 outline-none transition-all dark:text-white"
            />
            <button 
              onClick={handleSend}
              disabled={!input.trim() || isLoading}
              className="absolute right-2 top-2 p-2 bg-primary-600 hover:bg-primary-700 disabled:bg-slate-300 dark:disabled:bg-slate-700 text-white rounded-xl transition-all shadow-md shadow-primary-500/20 active:scale-95"
            >
              {isLoading ? <Loader2 className="w-5 h-5 animate-spin" /> : <Send className="w-5 h-5" />}
            </button>
          </div>
        </div>
        <p className="text-[10px] text-center text-slate-400 mt-2">
          AI-generated responses. Verify critical data with DGCA Official Portal.
        </p>
      </div>
    </div>
  )
}

export default ChatAssistant
