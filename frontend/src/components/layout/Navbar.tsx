import { Sun, Moon, User, Menu } from 'lucide-react'

interface NavbarProps {
  isDarkMode: boolean
  toggleDarkMode: () => void
  toggleSidebar: () => void
}

const Navbar: React.FC<NavbarProps> = ({ isDarkMode, toggleDarkMode, toggleSidebar }) => {
  return (
    <nav className="h-16 px-4 flex items-center justify-between bg-white dark:bg-slate-900 border-b border-slate-200 dark:border-slate-800 sticky top-0 z-50 transition-colors duration-300">
      <div className="flex items-center gap-3">
        <button 
          onClick={toggleSidebar}
          className="p-2 hover:bg-slate-100 dark:hover:bg-slate-800 rounded-lg transition-colors md:hidden"
        >
          <Menu className="w-5 h-5" />
        </button>
        <div className="flex items-center gap-2 text-primary-600 dark:text-primary-400">
          <div className="p-1.5 bg-primary-100 dark:bg-primary-900/40 rounded-lg">
            {/* Using a drone-like icon represent the logo */}
            <div className="w-6 h-6 flex items-center justify-center">
               <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="w-full h-full">
                  <path d="M12 2v8" />
                  <path d="M12 14v8" />
                  <path d="M22 12h-8" />
                  <path d="M10 12H2" />
                  <circle cx="12" cy="12" r="2" />
                  <path d="M20 5l-2.5 2.5" />
                  <path d="M6.5 17.5L4 20" />
                  <path d="M20 19l-2.5-2.5" />
                  <path d="M6.5 6.5L4 4" />
               </svg>
            </div>
          </div>
          <h1 className="text-xl font-bold font-display hidden sm:block">
            Drone Intelligence System <span className="text-sm font-medium text-slate-500">for India</span>
          </h1>
        </div>
      </div>

      <div className="flex items-center gap-2">
        <button
          onClick={toggleDarkMode}
          className="p-2 text-slate-500 hover:text-primary-600 hover:bg-slate-100 dark:hover:bg-slate-800 rounded-lg transition-all"
          title="Toggle Dark Mode"
        >
          {isDarkMode ? <Sun className="w-5 h-5" /> : <Moon className="w-5 h-5" />}
        </button>
        
        <div className="w-px h-6 bg-slate-200 dark:bg-slate-800 mx-1"></div>
        
        <button className="flex items-center gap-2 p-1.5 pl-3 pr-3 text-sm font-medium text-slate-700 dark:text-slate-200 hover:bg-slate-100 dark:hover:bg-slate-800 rounded-full border border-slate-200 dark:border-slate-800 transition-all">
          <User className="w-4 h-4" />
          <span className="hidden md:inline">Profile</span>
        </button>
      </div>
    </nav>
  )
}

export default Navbar
