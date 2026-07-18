export default function StatusBar() {
  return (
    <div className="bg-[#8B7355] text-[#F5EBE0] px-3 py-1 flex items-center gap-4"
         style={{ fontFamily: "'VT323', monospace", fontSize: 14, letterSpacing: '0.08em' }}>
      <span className="flex items-center gap-1">
        <span style={{ animation: 'pulse-dot 2.5s ease-in-out infinite' }}
              className="inline-block w-2 h-2 rounded-full bg-[#4ACA60]" />
        ONLINE
      </span>
      <span className="text-[#A89070]">│</span>
      <span>FLIP SIDE MUSIC SYSTEM 1.0</span>
    </div>
  )
}