import { ArrowRight, Play, BookOpen, BrainCircuit, PenTool, Target, Brain, CopyCheck } from "lucide-react";

export default function HeroSection({ onNavigate, onOpenNotes }: { onNavigate?: (tab: string) => void, onOpenNotes?: () => void }) {
  return (
    <div className="relative w-full min-h-screen text-white overflow-hidden font-sans border-b border-[#7c5cbf]/20">
      <style>{`
        @keyframes fadeSlideIn {
          from { opacity: 0; transform: translateY(20px); }
          to { opacity: 1; transform: translateY(0); }
        }
        .animate-fade-in {
          animation: fadeSlideIn 0.8s ease-out forwards;
          opacity: 0;
        }
        .delay-100 { animation-delay: 0.1s; }
        .delay-200 { animation-delay: 0.2s; }
        .delay-300 { animation-delay: 0.3s; }
        .delay-400 { animation-delay: 0.4s; }
        .delay-500 { animation-delay: 0.5s; }
        
        .shadow-glow {
          box-shadow: 0 0 40px rgba(124, 92, 191, 0.4);
        }
      `}</style>

      {/* Subtle Purple Radial Glow */}
      <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[800px] h-[800px] bg-[#6d28d9] opacity-20 blur-[120px] rounded-full pointer-events-none" />

      <div className="relative z-10 mx-auto max-w-7xl px-4 pt-32 pb-12 sm:px-6 md:pt-40 md:pb-20 lg:px-8">
        <div className="grid grid-cols-1 gap-12 lg:grid-cols-12 lg:gap-8 items-center">
          
          {/* --- LEFT COLUMN --- */}
          <div className="lg:col-span-7 flex flex-col justify-center space-y-8 pt-8">
            
            {/* Floating Feature Pills */}
          <div className="flex flex-wrap justify-center gap-3 sm:gap-4 mb-8 sm:mb-10 animate-fade-in-up" style={{ animationDelay: "200ms" }}>
            <div onClick={() => {
                onNavigate?.('Decks')
                const docId = localStorage.getItem('shadowbyte_current_doc_id')
                if (docId) {
                   setTimeout(() => {
                      // Trigger generate modal event
                      window.dispatchEvent(new CustomEvent('shadowbyte:openFlashcardsGenerate'))
                   }, 300)
                }
            }} className="cursor-pointer group flex items-center gap-2 px-3 sm:px-4 py-2 rounded-full bg-[#16161f]/80 border border-[#7c5cbf]/20 hover:border-[#7c5cbf]/50 hover:bg-[#7c5cbf]/10 transition-all duration-300">
              <BookOpen className="w-3.5 h-3.5 sm:w-4 sm:h-4 text-[#a78bfa] group-hover:scale-110 transition-transform" />
              <span className="text-xs sm:text-sm font-medium text-[#c0bde0]">Flashcards</span>
            </div>

            <div onClick={() => {
                onNavigate?.('Knowledge')
                // State checking for empty graph will be handled inside KnowledgeGraph mount, but we throw event here just in case.
                setTimeout(() => {
                   window.dispatchEvent(new CustomEvent('shadowbyte:triggerGraphRegeneration'))
                }, 500)
            }} className="cursor-pointer group flex items-center gap-2 px-3 sm:px-4 py-2 rounded-full bg-[#16161f]/80 border border-[#7c5cbf]/20 hover:border-[#7c5cbf]/50 hover:bg-[#7c5cbf]/10 transition-all duration-300">
              <BrainCircuit className="w-3.5 h-3.5 sm:w-4 sm:h-4 text-[#34d399] group-hover:scale-110 transition-transform" />
              <span className="text-xs sm:text-sm font-medium text-[#c0bde0]">Knowledge Graph</span>
            </div>

            <div onClick={() => {
                onOpenNotes?.()
                const docId = localStorage.getItem('shadowbyte_current_doc_id')
                if (docId) {
                   const saved = localStorage.getItem(`shadowbyte_notes_${docId}`)
                   if (!saved || JSON.parse(saved).length === 0) {
                      setTimeout(() => {
                         window.dispatchEvent(new CustomEvent('shadowbyte:triggerNotesSummarize'))
                      }, 500)
                   }
                }
            }} className="cursor-pointer group flex items-center gap-2 px-3 sm:px-4 py-2 rounded-full bg-[#16161f]/80 border border-[#7c5cbf]/20 hover:border-[#7c5cbf]/50 hover:bg-[#7c5cbf]/10 transition-all duration-300">
              <PenTool className="w-3.5 h-3.5 sm:w-4 sm:h-4 text-[#fbbf24] group-hover:scale-110 transition-transform" />
              <span className="text-xs sm:text-sm font-medium text-[#c0bde0]">Smart Notes</span>
            </div>
          </div>

            {/* Heading */}
            <h1 className="animate-fade-in delay-200 text-5xl sm:text-6xl lg:text-7xl font-bold tracking-tight leading-[1.1] text-white">
              Study smarter,<br />
              <span className="bg-gradient-to-br from-[#f1f0f9] via-[#a78bfa] to-[#7c5cbf] bg-clip-text text-transparent">
                in the shadows.
              </span>
            </h1>

            {/* Description */}
            <p className="animate-fade-in delay-300 max-w-xl text-lg text-[#9896b0] leading-relaxed font-medium">
              ShadowByte — your AI study companion that learns how you learn. Master concepts faster, generate dynamic flashcards, and map your knowledge intuitively.
            </p>

            {/* CTA Buttons */}
            <div className="flex flex-col sm:flex-row items-center justify-center gap-4 sm:gap-6 animate-fade-in-up" style={{ animationDelay: "600ms" }}>
            <button 
              onClick={() => onNavigate?.('Study Chat')}
              className="group relative w-full sm:w-auto px-8 py-4 rounded-xl font-bold text-white overflow-hidden transition-all duration-300 hover:scale-105 hover:shadow-[0_0_40px_rgba(124,92,191,0.4)] bg-[#7c5cbf]"
            >
              <div className="absolute inset-0 bg-gradient-to-r from-transparent via-white/10 to-transparent -translate-x-full group-hover:animate-shimmer" />
              <span className="relative flex items-center justify-center gap-2">
                Start Studying
                <ArrowRight className="w-4 h-4 group-hover:translate-x-1 transition-transform" />
              </span>
            </button>
            <button className="group flex items-center justify-center gap-2 w-full sm:w-auto px-8 py-4 rounded-xl font-bold text-[#c0bde0] hover:text-white transition-all bg-[#16161f] border border-[#7c5cbf]/20 hover:border-[#7c5cbf]/50 hover:bg-[#7c5cbf]/10">
              <Play className="w-4 h-4 text-[#a78bfa] group-hover:text-[#c0bde0] transition-colors" />
              See how it works
            </button>
          </div>
          </div>

          {/* --- RIGHT COLUMN (Floating Stat Cards) --- */}
          <div className="lg:col-span-5 relative space-y-6 lg:mt-0 flex flex-col items-center sm:items-end w-full">
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6 relative z-10">
            {/* Stat 1 */}
            <div className="glass-card bg-[#16161f]/60 rounded-2xl p-6 border border-[#7c5cbf]/20 backdrop-blur-xl animate-fade-in-up" style={{ animationDelay: "800ms" }}>
              <div className="flex items-center justify-center w-12 h-12 rounded-xl bg-[#7c5cbf]/20 mb-4 text-[#a78bfa] mx-auto border border-[#7c5cbf]/30">
                <Brain className="w-6 h-6" />
              </div>
              <h3 className="text-3xl font-bold text-white mb-1">2,400+</h3>
              <p className="text-[#9896b0] text-sm">Concepts Mastered</p>
            </div>
            
            {/* Stat 2 */}
            <div className="glass-card bg-[#16161f]/60 rounded-2xl p-6 border border-[#7c5cbf]/20 backdrop-blur-xl animate-fade-in-up" style={{ animationDelay: "900ms" }}>
              <div className="flex items-center justify-center w-12 h-12 rounded-xl bg-[#34d399]/20 mb-4 text-[#34d399] mx-auto border border-[#34d399]/30">
                <CopyCheck className="w-6 h-6" />
              </div>
              <h3 className="text-3xl font-bold text-white mb-1">94%</h3>
              <p className="text-[#9896b0] text-sm">Exam Pass Rate</p>
            </div>

            {/* Stat 3 */}
            <div className="glass-card bg-[#16161f]/60 rounded-2xl p-6 border border-[#7c5cbf]/20 backdrop-blur-xl animate-fade-in-up" style={{ animationDelay: "1000ms" }}>
              <div className="flex items-center justify-center w-12 h-12 rounded-xl bg-[#fbbf24]/20 mb-4 text-[#fbbf24] mx-auto border border-[#fbbf24]/30">
                <Target className="w-6 h-6" />
              </div>
              <h3 className="text-3xl font-bold text-white mb-1">3.2x</h3>
              <p className="text-[#9896b0] text-sm">Faster Retention</p>
            </div>
          </div>
          </div>
        </div>
      </div>
    </div>
  );
}
