import VinylRecord from "./VinylRecord"

export default function MenuBar() {
  return (
    <div className="flex items-center gap-6 px-3 py-1 border-b border-[#8B7355] bg-[#E8DFD0] z-20 flex-shrink-0">
      <VinylRecord size={36} duration="6s" />
      <span
        className="font-bold tracking-widest text-[#2C1810]"
        style={{ fontFamily: "'VT323', monospace", fontSize: 32 }}
      >
        FLIP SIDE
      </span>
      <span
        className=" cursor-pointer hover:text-[#2C1810]"
        style={{ fontFamily: "'Share Tech Mono', monospace", fontSize: 14 }}
      > 
      Help</span>
    </div>
  )
}