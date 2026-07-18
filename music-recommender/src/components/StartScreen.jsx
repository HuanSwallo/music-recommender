import { useState } from "react"
import VinylRecord from "./VinylRecord"
import StatusBar from "./StatusBar"
import MenuBar from "./MenuBar"

export default function StartScreen({ onSubmit }) {
  const [username, setUsername] = useState("")

  const handleAnalyze = () => {
    if (username.trim()) onSubmit(username.trim())
  }

  return (
    <div className="min-h-screen bg-[#E8DFD0] flex flex-col relative overflow-hidden"
         style={{ fontFamily: "'Share Tech Mono', monospace", color: '#2C1810' }}>
      
      {/* Menu bar at the top */}
      <MenuBar />
      {/* Background vinyl decorations */}
      <VinylRecord size={320} duration="18s"
        style={{ position:'absolute', bottom: 80, left: 80, opacity:0.07, pointerEvents:'none' }} />
      <VinylRecord size={420} duration="22s"
        style={{ position:'absolute', top: 80, right:80, opacity:0.07, pointerEvents:'none',
                 animationDirection:'reverse' }} />

      {/* Main content */}
      <div className="flex-1 flex items-center justify-center p-6">
        <div className="bg-[#D4C8B0] border border-[#8B7355] rounded-sm w-[450px]"
             style={{ boxShadow: '2px 2px 0 #8B7355' }}>

          {/* Window title bar */}
          <div className="flex items-center px-4 py-2 border-b border-[#8B7355] relative"
               style={{ background: 'linear-gradient(to bottom, #A89070, #8B7355)', borderRadius: '2px 2px 0 0' }}>
            <div className="flex gap-1">
              {['#C0392B','#C8A020','#4A8A3A'].map((c, i) => (
                <div key={i} className="w-3 h-3 rounded-full border border-black/30"
                     style={{ background: c }} />
              ))}
            </div>
            <span className="absolute left-1/2 -translate-x-1/2 text-[#F5EBE0] tracking-widest"
                  style={{ fontFamily: "'VT323', monospace", fontSize: 18 }}>
              FLIP SIDE v1.0
            </span>
          </div>

          {/* Window body */}
          <div className="p-6">
            {/* Logo row */}
            <div className="flex items-center gap-3 mb-4 pb-4 border-b-2 border-[#A89070]">
              <VinylRecord size={82} duration="4s" />
              <div>
                <div style={{ fontFamily: "'VT323', monospace", fontSize: 30, letterSpacing: '0.15em' }}>
                  FLIP SIDE
                </div>
                <div className="text-[14px] text-[#6B4F3A] leading-relaxed">
                  Your personal record oracle.<br />Powered by Last.fm data.
                </div>
              </div>
            </div>

            {/* Input */}
            <div className="text-[12px] text-[#6B4F3A] tracking-widest mb-1">
              LAST.FM USERNAME:
            </div>
            <input
              type="text"
              value={username}
              onChange={e => setUsername(e.target.value)}
              onKeyDown={e => e.key === 'Enter' && handleAnalyze()}
              placeholder="e.g. vinylhead"
              className="w-full bg-[#F5EBE0] border border-[#8B7355] px-2 py-1.5 text-[14px]
                         outline-none focus:border-[#C0392B] focus:bg-[#FFF8F0] rounded-none"
              style={{ fontFamily: "'Share Tech Mono', monospace" }}
            />

            {/* Buttons */}
            <div className="flex gap-2 mt-2">
              <button
                onClick={() => setUsername("")}
                className="border border-[#8B7355] bg-[#D4C8B0] text-[#6B4F3A] px-3 py-1.5
                           text-[14px] tracking-wider hover:bg-[#C4B8A0] rounded-none"
                style={{ fontFamily: "'Share Tech Mono', monospace" }}>
                Clear
              </button>
              <button
                onClick={handleAnalyze}
                className="flex-1 flex items-center justify-center gap-2 border border-[#8B7355]
                           bg-[#C0392B] text-[#F5EBE0] py-1.5 text-[14px] tracking-wider
                           hover:bg-[#A93220] active:translate-y-px rounded-none"
                style={{ fontFamily: "'Share Tech Mono', monospace" }}>
                <span style={{ width:0, height:0, borderTop:'5px solid transparent',
                               borderBottom:'5px solid transparent', borderLeft:'8px solid #F5EBE0' }} />
                Analyze Profile
              </button>
            </div>
          </div>
        </div>
      </div>

      <StatusBar />
    </div>
  )
}