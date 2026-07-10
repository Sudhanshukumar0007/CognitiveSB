import { useState, useRef, useEffect, type ReactNode } from 'react'
import { Loader2, Copy, Check } from 'lucide-react'
import { useChat } from '../../hooks/useChat'
import { ModeSelector } from './mode-selector'
import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'
import { toast } from 'sonner'

type MarkdownChildren = {
  children?: ReactNode
}

type CodeProps = MarkdownChildren & {
  inline?: boolean
  className?: string
}

const markdownComponents = {
  pre: ({ children }: MarkdownChildren) => <>{children}</>,
  p: ({ children }: MarkdownChildren) => (
    <p style={{ marginBottom: '10px', lineHeight: '1.8', color: 'rgba(255,255,255,0.85)', fontSize: '16px' }}>
      {children}
    </p>
  ),
  strong: ({ children }: MarkdownChildren) => (
    <strong style={{ color: '#a9a3f0', fontWeight: 500 }}>{children}</strong>
  ),
  em: ({ children }: MarkdownChildren) => (
    <em style={{ color: 'rgba(255,255,255,0.6)', fontStyle: 'italic' }}>{children}</em>
  ),
  code: ({ inline, className, children, ...props }: CodeProps) => {
    const match = /language-(\w+)/.exec(className || '')
    if (!inline) {
      const handleCodeCopy = async () => {
        const text = typeof children === 'string' ? children : String(children)
        try {
          await navigator.clipboard.writeText(text)
          toast.success('Code copied!')
        } catch {
          toast.error('Failed to copy')
        }
      }
      return (
        <div className="bg-[#1c1c1c] border border-[#2a2440] rounded-xl overflow-hidden my-4">
          <div className="flex items-center justify-between px-4 py-2 bg-[#1a1726] border-b border-[#2a2440]">
            <span className="text-xs font-mono text-[#a78bfa]">{match ? match[1] : 'code'}</span>
            <button
              onClick={handleCodeCopy}
              className="text-[10px] border border-[#3b345c] rounded px-2 py-0.5 text-[#a78bfa] hover:bg-[#231d36] transition-colors"
            >
              copy
            </button>
          </div>
          <pre style={{ padding: '14px 16px', overflowX: 'auto', margin: 0 }}>
            <code
              className={className}
              style={{ fontFamily: 'monospace', fontSize: '14px', color: '#cdd6f4', lineHeight: '1.8' }}
              {...props}
            >
              {children}
            </code>
          </pre>
        </div>
      )
    }
    return (
      <code
        style={{
          background: 'rgba(127,119,221,0.15)',
          color: '#c4b5fd',
          padding: '2px 6px',
          borderRadius: '4px',
          fontFamily: 'monospace',
          fontSize: '14px',
          lineHeight: '1.8',
        }}
        {...props}
      >
        {children}
      </code>
    )
  },
  ul: ({ children }: MarkdownChildren) => (
    <ul style={{ paddingLeft: '20px', marginBottom: '10px', color: 'rgba(255,255,255,0.8)' }}>{children}</ul>
  ),
  ol: ({ children }: MarkdownChildren) => (
    <ol style={{ paddingLeft: '20px', marginBottom: '10px', color: 'rgba(255,255,255,0.8)' }}>{children}</ol>
  ),
  li: ({ children }: MarkdownChildren) => (
    <li style={{ marginBottom: '6px', lineHeight: '1.6' }}>{children}</li>
  ),
  h1: ({ children }: MarkdownChildren) => (
    <p style={{ fontSize: '15px', fontWeight: 500, color: '#a9a3f0', marginBottom: '8px' }}>{children}</p>
  ),
  h2: ({ children }: MarkdownChildren) => (
    <p style={{ fontSize: '14px', fontWeight: 500, color: '#a9a3f0', marginBottom: '6px' }}>{children}</p>
  ),
  h3: ({ children }: MarkdownChildren) => (
    <p style={{ fontSize: '14px', fontWeight: 500, color: 'rgba(255,255,255,0.7)', marginBottom: '6px' }}>{children}</p>
  ),
  blockquote: ({ children }: MarkdownChildren) => (
    <blockquote
      style={{
        borderLeft: '3px solid rgba(127,119,221,0.4)',
        paddingLeft: '12px',
        margin: '10px 0',
        color: 'rgba(255,255,255,0.55)',
        fontStyle: 'italic',
      }}
    >
      {children}
    </blockquote>
  ),
}

// ── Copy Button Component ──────────────────────────────────────────────────────
function CopyButton({ text }: { text: string }) {
  const [copied, setCopied] = useState(false)

  const handleCopy = async () => {
    if (!text) return
    try {
      await navigator.clipboard.writeText(text)
      setCopied(true)
      toast.success('Copied to clipboard!')
      setTimeout(() => setCopied(false), 2000)
    } catch {
      // Fallback for older browsers / non-HTTPS
      try {
        const textarea = document.createElement('textarea')
        textarea.value = text
        textarea.style.position = 'fixed'
        textarea.style.opacity = '0'
        document.body.appendChild(textarea)
        textarea.select()
        document.execCommand('copy')
        document.body.removeChild(textarea)
        setCopied(true)
        toast.success('Copied to clipboard!')
        setTimeout(() => setCopied(false), 2000)
      } catch {
        toast.error('Failed to copy')
      }
    }
  }

  return (
    <button
      onClick={handleCopy}
      title={copied ? 'Copied!' : 'Copy message'}
      aria-label={copied ? 'Copied!' : 'Copy message'}
      className="
        opacity-0 group-hover:opacity-100
        transition-all duration-150
        p-1 rounded
        text-white/30 hover:text-white/70
        hover:bg-white/10
        flex items-center gap-1
      "
    >
      {copied
        ? <Check size={13} className="text-green-400" />
        : <Copy size={13} />
      }
    </button>
  )
}

// ── Main Component ─────────────────────────────────────────────────────────────
export function ChatInterface({ sessionId }: { sessionId: string }) {
  const { messages, isLoading, currentMode, setCurrentMode, sendMessage } = useChat()
  const [input, setInput] = useState('')
  const messagesEndRef = useRef<HTMLDivElement>(null)

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  useEffect(() => {
    const handleAsk = (e: Event) => {
      const question = e instanceof CustomEvent ? e.detail : undefined
      if (question && !isLoading) {
        sendMessage(question, sessionId, currentMode)
      }
    }
    window.addEventListener('shadowbyte:ask', handleAsk)
    return () => window.removeEventListener('shadowbyte:ask', handleAsk)
  }, [isLoading, sessionId, currentMode, sendMessage])

  const handleSend = () => {
    if (input.trim() && !isLoading) {
      sendMessage(input, sessionId, currentMode)
      setInput('')
    }
  }

  return (
    <div className="flex flex-col h-full w-full bg-[#13111c] rounded-xl overflow-hidden">

      {/* Header / Mode Selector */}
      <div className="pt-6 px-6 pb-2">
        <ModeSelector mode={currentMode} onChange={setCurrentMode} />
      </div>

      {/* Messages Area */}
      <div className="flex-1 overflow-y-auto px-5 pt-6 pb-28 flex flex-col bg-[#141414]">
        {messages.length === 0 ? (
          <div className="h-full flex flex-col items-center justify-center text-center px-4">
            <div className="w-16 h-16 rounded-full bg-[#231d36] border border-[#3b345c] flex items-center justify-center mb-4">
              <span className="text-[#a78bfa] font-bold text-xl">AI</span>
            </div>
            <h3 className="text-xl font-medium text-white">How can I help you study today?</h3>
            <p className="text-[#888888] mt-2 max-w-md">Ask a question, or choose a mode above to change how I respond.</p>
          </div>
        ) : (
          messages.map((msg) => (
            <div
              key={msg.id}
              className={`flex items-start gap-3 mb-6 group ${msg.role === 'user' ? 'flex-row-reverse' : 'flex-row'}`}
            >

              {/* Avatar */}
              <div className="flex-shrink-0 mt-0.5">
                <div className={`w-7 h-7 rounded-full flex items-center justify-center text-xs font-medium border
                  ${msg.role === 'user'
                    ? 'bg-white/10 border-transparent text-white/60'
                    : 'bg-purple-900/40 border-purple-500/25 text-purple-300'}
                `}>
                  {msg.role === 'user' ? 'U' : 'AI'}
                </div>
              </div>

              {/* Message Content */}
              <div className={`relative
                ${msg.role === 'user'
                  ? 'max-w-[78%] rounded-2xl rounded-tr-sm px-4 py-2.5 bg-purple-500/15 border border-purple-500/25 text-white/90'
                  : 'flex-1 min-w-0 text-[#e2e8f0] pt-1'}
                ${msg.error ? 'border-red-900 bg-red-900/20' : ''}
              `}>

                {/* Message text */}
                {msg.role === 'user' ? (
                  <p className="text-white/90 text-base leading-relaxed">
                    {msg.content || (msg.streaming ? '...' : '')}
                  </p>
                ) : (
                  <ReactMarkdown remarkPlugins={[remarkGfm]} components={markdownComponents}>
                    {msg.content || (msg.streaming ? '...' : '')}
                  </ReactMarkdown>
                )}

                {/* Streaming dots */}
                {msg.streaming && !msg.content && (
                  <div className="flex space-x-1 mt-2">
                    <div className="w-2 h-2 bg-[#a78bfa] rounded-full animate-bounce [animation-delay:-0.3s]"></div>
                    <div className="w-2 h-2 bg-[#a78bfa] rounded-full animate-bounce [animation-delay:-0.15s]"></div>
                    <div className="w-2 h-2 bg-[#a78bfa] rounded-full animate-bounce"></div>
                  </div>
                )}

                {/* Citations */}
                {msg.role === 'assistant' && msg.citations && msg.citations.length > 0 && (
                  <div className="mt-2 flex flex-wrap gap-1.5">
                    {msg.citations.map((citation, i) => (
                      <span
                        key={`${citation.source || 'source'}-${i}`}
                        className="text-xs px-2 py-0.5 rounded bg-white/5 border border-white/10 text-white/40 cursor-pointer hover:text-white/60"
                        title={citation.text}
                      >
                        {citation.page !== undefined && citation.page !== null ? `p.${citation.page}` : `ref ${i + 1}`}
                      </span>
                    ))}
                  </div>
                )}

                {/* Copy button — only shown when message is complete (not streaming) */}
                {!msg.streaming && msg.content && (
                  <div className={`
                    flex mt-1
                    ${msg.role === 'user' ? 'justify-end' : 'justify-start'}
                  `}>
                    <CopyButton text={msg.content} />
                  </div>
                )}

              </div>
            </div>
          ))
        )}
        <div ref={messagesEndRef} />
      </div>

      {/* Input Area */}
      <div className="p-4 px-6 pb-6">
        <div className="relative flex items-center">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => {
              if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault()
                handleSend()
              }
            }}
            placeholder="Ask a question about your material..."
            className="w-full bg-[#252525] border border-[#333333] rounded-xl pl-4 pr-12 py-3.5 text-[15px] text-[#e2e8f0] outline-none focus:border-[#555] transition-colors placeholder:text-[#888]"
            disabled={isLoading}
          />
          <button
            onClick={handleSend}
            disabled={!input.trim() || isLoading}
            className="absolute right-3 w-8 h-8 flex items-center justify-center bg-[#7c5cf7] text-white rounded-full disabled:opacity-50 disabled:cursor-not-allowed hover:opacity-90 transition-opacity"
          >
            {isLoading
              ? <Loader2 size={16} className="animate-spin" />
              : <div className="w-0 h-0 border-t-[5px] border-t-transparent border-l-[8px] border-l-white border-b-[5px] border-b-transparent ml-1" />
            }
          </button>
        </div>
        <p className="text-center text-[11px] text-[#555555] mt-3">
          ShadowByte AI can make mistakes. Always verify important information.
        </p>
      </div>

    </div>
  )
}