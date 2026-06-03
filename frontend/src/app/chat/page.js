'use client';

import { useState, useEffect, useRef, useCallback, Suspense } from 'react';
import { useSearchParams } from 'next/navigation';
import Link from 'next/link';
import { streamChat } from '@/lib/api';

/* ───────────────────── Constants ───────────────────── */

const WELCOME_MESSAGE = {
  role: 'assistant',
  content: `Namaste! 🙏 I'm GigSaathi, your AI tax assistant.\n\nI can help you with:\n• Understanding your total earnings across platforms\n• Calculating your exact tax liability\n• Finding deductions you might be missing\n• Generating your ITR-4 summary for filing\n• Tracking advance tax deadlines\n\nJust ask me anything about your taxes! 💰`,
  tools_called: [],
  timestamp: new Date().toLocaleTimeString('en-IN', {
    hour: '2-digit',
    minute: '2-digit',
  }),
};

const SUGGESTIONS = [
  'How much tax do I owe?',
  'What deductions can I claim?',
  'When is my next tax deadline?',
  'Generate my ITR summary',
  'Explain Section 44ADA to me',
  'Am I getting a refund?',
];

/* ───────────────────── Helpers ───────────────────── */

function formatTime() {
  return new Date().toLocaleTimeString('en-IN', {
    hour: '2-digit',
    minute: '2-digit',
  });
}

/** Minimal markdown-style rendering: bold, bullet points, newlines */
function renderMessageContent(text) {
  if (!text) return null;
  const lines = text.split('\n');
  return lines.map((line, i) => {
    // Bullet points
    if (line.startsWith('• ') || line.startsWith('- ')) {
      const bulletContent = line.slice(2);
      return (
        <div key={i} className="chat-bullet">
          <span className="chat-bullet-dot">•</span>
          <span
            dangerouslySetInnerHTML={{
              __html: bulletContent.replace(
                /\*\*(.*?)\*\*/g,
                '<strong>$1</strong>'
              ),
            }}
          />
        </div>
      );
    }
    // Regular lines — support bold
    return (
      <p
        key={i}
        className={line.trim() === '' ? 'chat-line-break' : 'chat-line'}
        dangerouslySetInnerHTML={{
          __html:
            line.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>') || '&nbsp;',
        }}
      />
    );
  });
}

/* ───────────────────── Component ───────────────────── */

function ChatPageContent() {
  const searchParams = useSearchParams();
  const user = searchParams.get('user') || 'ravi_kumar';

  const [messages, setMessages] = useState([WELCOME_MESSAGE]);
  const [input, setInput] = useState('');
  const [isStreaming, setIsStreaming] = useState(false);
  const [showSuggestions, setShowSuggestions] = useState(true);

  const messagesEndRef = useRef(null);
  const inputRef = useRef(null);

  /* Auto-scroll to bottom */
  const scrollToBottom = useCallback(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, []);

  useEffect(() => {
    scrollToBottom();
  }, [messages, isStreaming, scrollToBottom]);

  /* Focus input on mount */
  useEffect(() => {
    inputRef.current?.focus();
  }, []);

  /* ────────── Send a message ────────── */
  const sendMessage = useCallback(
    async (text) => {
      const trimmed = (text || input).trim();
      if (!trimmed || isStreaming) return;

      setShowSuggestions(false);
      setInput('');

      // Add user message
      const userMsg = {
        role: 'user',
        content: trimmed,
        tools_called: [],
        timestamp: formatTime(),
      };
      setMessages((prev) => [...prev, userMsg]);
      setIsStreaming(true);

      // Prepare assistant placeholder
      const assistantMsg = {
        role: 'assistant',
        content: '',
        tools_called: [],
        timestamp: formatTime(),
      };
      setMessages((prev) => [...prev, assistantMsg]);

      try {
        await streamChat(user, trimmed, (chunk) => {
          setMessages((prev) => {
            const updated = [...prev];
            const lastAssistant = updated[updated.length - 1];
            if (chunk.content) {
              lastAssistant.content += chunk.content;
            }
            if (chunk.tool && !lastAssistant.tools_called.includes(chunk.tool)) {
              lastAssistant.tools_called = [
                ...lastAssistant.tools_called,
                chunk.tool,
              ];
            }
            if (chunk.tools_called && Array.isArray(chunk.tools_called)) {
              for (const t of chunk.tools_called) {
                if (!lastAssistant.tools_called.includes(t)) {
                  lastAssistant.tools_called = [
                    ...lastAssistant.tools_called,
                    t,
                  ];
                }
              }
            }
            lastAssistant.timestamp = formatTime();
            return updated;
          });
        });
      } catch (err) {
        setMessages((prev) => {
          const updated = [...prev];
          const last = updated[updated.length - 1];
          last.content =
            last.content ||
            "I'm sorry, I couldn't process that right now. Please try again in a moment. 🙏";
          return updated;
        });
        console.error('Chat stream error:', err);
      } finally {
        setIsStreaming(false);
        inputRef.current?.focus();
      }
    },
    [input, isStreaming, user]
  );

  /* ────────── Clear history ────────── */
  const clearHistory = () => {
    setMessages([
      {
        ...WELCOME_MESSAGE,
        timestamp: formatTime(),
      },
    ]);
    setShowSuggestions(true);
    setInput('');
  };

  /* ────────── Handle keyboard ────────── */
  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  /* ───────────────────── Render ───────────────────── */
  return (
    <div className="chat-container">
      {/* ── Top Bar ── */}
      <header className="chat-header">
        <Link href={`/dashboard?user=${user}`} className="chat-back-btn">
          <svg
            width="20"
            height="20"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            strokeWidth="2.5"
            strokeLinecap="round"
            strokeLinejoin="round"
          >
            <path d="M19 12H5" />
            <path d="M12 19l-7-7 7-7" />
          </svg>
        </Link>

        <div className="chat-header-info">
          <div className="chat-header-title">
            <span className="chat-robot-emoji">🤖</span>
            <span>GigSaathi AI</span>
            <span className="chat-online-dot" />
          </div>
          <span className="chat-header-subtitle">
            Your intelligent tax assistant
          </span>
        </div>

        <button
          className="chat-clear-btn"
          onClick={clearHistory}
          title="Clear chat history"
        >
          <svg
            width="18"
            height="18"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            strokeWidth="2"
            strokeLinecap="round"
            strokeLinejoin="round"
          >
            <polyline points="3 6 5 6 21 6" />
            <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2" />
          </svg>
        </button>
      </header>

      {/* ── Messages Area ── */}
      <div className="chat-messages-area">
        {messages.map((msg, idx) => (
          <div
            key={idx}
            className={`chat-message-row ${
              msg.role === 'user' ? 'chat-row-user' : 'chat-row-assistant'
            }`}
          >
            {/* Avatar */}
            <div
              className={`chat-avatar ${
                msg.role === 'user' ? 'chat-avatar-user' : 'chat-avatar-bot'
              }`}
            >
              {msg.role === 'user' ? '👤' : '🤖'}
            </div>

            {/* Bubble */}
            <div
              className={`chat-bubble ${
                msg.role === 'user' ? 'chat-bubble-user' : 'chat-bubble-assistant'
              }`}
            >
              <div className="chat-bubble-content">
                {renderMessageContent(msg.content)}
              </div>

              {/* Tool badges */}
              {msg.tools_called && msg.tools_called.length > 0 && (
                <div className="chat-tool-badges">
                  {msg.tools_called.map((tool, tIdx) => (
                    <span key={tIdx} className="chat-tool-badge">
                      {tool.includes('tax') || tool.includes('calculate')
                        ? '🔧'
                        : tool.includes('income') || tool.includes('summary')
                        ? '📊'
                        : tool.includes('deadline')
                        ? '📅'
                        : tool.includes('deduction')
                        ? '💡'
                        : '⚙️'}{' '}
                      {tool}
                    </span>
                  ))}
                </div>
              )}

              {/* Timestamp */}
              <span className="chat-timestamp">{msg.timestamp}</span>
            </div>
          </div>
        ))}

        {/* Typing indicator */}
        {isStreaming && (
          <div className="chat-message-row chat-row-assistant">
            <div className="chat-avatar chat-avatar-bot">🤖</div>
            <div className="chat-typing-indicator">
              <span className="chat-typing-dot" />
              <span className="chat-typing-dot" />
              <span className="chat-typing-dot" />
            </div>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* ── Suggestion Chips ── */}
      {showSuggestions && (
        <div className="chat-suggestions">
          <div className="chat-suggestions-scroll">
            {SUGGESTIONS.map((s, i) => (
              <button
                key={i}
                className="chat-suggestion-chip"
                onClick={() => sendMessage(s)}
              >
                {s}
              </button>
            ))}
          </div>
        </div>
      )}

      {/* ── Input Area ── */}
      <div className="chat-input-area">
        <div className="chat-input-wrapper">
          <input
            ref={inputRef}
            type="text"
            className="chat-input"
            placeholder="Ask GigSaathi anything about your taxes..."
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            disabled={isStreaming}
          />
          <button
            className="chat-send-btn"
            onClick={() => sendMessage()}
            disabled={isStreaming || !input.trim()}
            title="Send message"
          >
            {isStreaming ? (
              <div className="chat-send-spinner" />
            ) : (
              <svg
                width="20"
                height="20"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                strokeWidth="2.5"
                strokeLinecap="round"
                strokeLinejoin="round"
              >
                <line x1="22" y1="2" x2="11" y2="13" />
                <polygon points="22 2 15 22 11 13 2 9 22 2" />
              </svg>
            )}
          </button>
        </div>
        <p className="chat-disclaimer">
          GigSaathi AI may make mistakes. Verify important tax information.
        </p>
      </div>

      {/* ━━━━━━━━━━━━━━━━ Scoped Styles ━━━━━━━━━━━━━━━━ */}
      <style jsx>{`
        /* ── Container ── */
        .chat-container {
          display: flex;
          flex-direction: column;
          height: 100vh;
          max-height: 100dvh;
          background: #0a0a1a;
          font-family: 'Inter', sans-serif;
          color: #f9fafb;
          overflow: hidden;
        }

        /* ── Header ── */
        .chat-header {
          display: flex;
          align-items: center;
          gap: 12px;
          padding: 14px 20px;
          background: rgba(17, 24, 39, 0.85);
          backdrop-filter: blur(20px);
          -webkit-backdrop-filter: blur(20px);
          border-bottom: 1px solid rgba(124, 58, 237, 0.2);
          position: sticky;
          top: 0;
          z-index: 20;
        }

        .chat-back-btn {
          display: flex;
          align-items: center;
          justify-content: center;
          width: 38px;
          height: 38px;
          border-radius: 12px;
          background: rgba(255, 255, 255, 0.06);
          color: #9ca3af;
          transition: all 0.2s ease;
          text-decoration: none;
          flex-shrink: 0;
        }
        .chat-back-btn:hover {
          background: rgba(124, 58, 237, 0.25);
          color: #c4b5fd;
          transform: translateX(-2px);
        }

        .chat-header-info {
          flex: 1;
          display: flex;
          flex-direction: column;
          gap: 2px;
        }
        .chat-header-title {
          display: flex;
          align-items: center;
          gap: 8px;
          font-weight: 700;
          font-size: 1.05rem;
          letter-spacing: -0.02em;
        }
        .chat-robot-emoji {
          font-size: 1.25rem;
        }
        .chat-online-dot {
          width: 9px;
          height: 9px;
          border-radius: 50%;
          background: #10b981;
          box-shadow: 0 0 8px rgba(16, 185, 129, 0.6);
          animation: pulse-dot 2s ease-in-out infinite;
        }
        @keyframes pulse-dot {
          0%, 100% { opacity: 1; box-shadow: 0 0 6px rgba(16, 185, 129, 0.4); }
          50% { opacity: 0.6; box-shadow: 0 0 14px rgba(16, 185, 129, 0.8); }
        }
        .chat-header-subtitle {
          font-size: 0.75rem;
          color: #6b7280;
          font-weight: 400;
        }

        .chat-clear-btn {
          display: flex;
          align-items: center;
          justify-content: center;
          width: 38px;
          height: 38px;
          border: none;
          border-radius: 12px;
          background: rgba(255, 255, 255, 0.06);
          color: #9ca3af;
          cursor: pointer;
          transition: all 0.2s ease;
          flex-shrink: 0;
        }
        .chat-clear-btn:hover {
          background: rgba(239, 68, 68, 0.2);
          color: #fca5a5;
        }

        /* ── Messages Area ── */
        .chat-messages-area {
          flex: 1;
          overflow-y: auto;
          padding: 20px 16px 8px;
          display: flex;
          flex-direction: column;
          gap: 8px;
          scroll-behavior: smooth;
        }
        .chat-messages-area::-webkit-scrollbar {
          width: 5px;
        }
        .chat-messages-area::-webkit-scrollbar-track {
          background: transparent;
        }
        .chat-messages-area::-webkit-scrollbar-thumb {
          background: rgba(124, 58, 237, 0.3);
          border-radius: 10px;
        }
        .chat-messages-area::-webkit-scrollbar-thumb:hover {
          background: rgba(124, 58, 237, 0.5);
        }

        /* ── Message Rows ── */
        .chat-message-row {
          display: flex;
          gap: 10px;
          max-width: 85%;
          animation: msg-slide-in 0.3s ease-out;
        }
        @keyframes msg-slide-in {
          from {
            opacity: 0;
            transform: translateY(12px);
          }
          to {
            opacity: 1;
            transform: translateY(0);
          }
        }
        .chat-row-user {
          align-self: flex-end;
          flex-direction: row-reverse;
        }
        .chat-row-assistant {
          align-self: flex-start;
        }

        /* Avatars */
        .chat-avatar {
          width: 34px;
          height: 34px;
          border-radius: 50%;
          display: flex;
          align-items: center;
          justify-content: center;
          font-size: 1rem;
          flex-shrink: 0;
          margin-top: 4px;
        }
        .chat-avatar-user {
          background: linear-gradient(135deg, #7c3aed, #6d28d9);
          box-shadow: 0 2px 10px rgba(124, 58, 237, 0.3);
        }
        .chat-avatar-bot {
          background: linear-gradient(135deg, #1e1b4b, #312e81);
          border: 1px solid rgba(124, 58, 237, 0.3);
          box-shadow: 0 2px 10px rgba(30, 27, 75, 0.4);
        }

        /* Bubbles */
        .chat-bubble {
          padding: 14px 18px;
          border-radius: 20px;
          max-width: 100%;
          position: relative;
          line-height: 1.6;
          font-size: 0.935rem;
        }
        .chat-bubble-user {
          background: linear-gradient(135deg, #7c3aed, #6d28d9);
          border-bottom-right-radius: 6px;
          color: #f3f0ff;
          box-shadow: 0 4px 20px rgba(124, 58, 237, 0.25);
        }
        .chat-bubble-assistant {
          background: rgba(255, 255, 255, 0.05);
          backdrop-filter: blur(12px);
          -webkit-backdrop-filter: blur(12px);
          border: 1px solid rgba(255, 255, 255, 0.08);
          border-bottom-left-radius: 6px;
          color: #e5e7eb;
          box-shadow: 0 4px 20px rgba(0, 0, 0, 0.2);
        }

        .chat-bubble-content {
          display: flex;
          flex-direction: column;
          gap: 2px;
        }
        .chat-line {
          margin: 0;
          word-wrap: break-word;
        }
        .chat-line-break {
          height: 8px;
          margin: 0;
        }
        .chat-bullet {
          display: flex;
          gap: 8px;
          align-items: flex-start;
          padding-left: 4px;
        }
        .chat-bullet-dot {
          color: #10b981;
          font-weight: 700;
          flex-shrink: 0;
          margin-top: 1px;
        }

        /* Tool badges */
        .chat-tool-badges {
          display: flex;
          flex-wrap: wrap;
          gap: 6px;
          margin-top: 10px;
          padding-top: 10px;
          border-top: 1px solid rgba(255, 255, 255, 0.08);
        }
        .chat-tool-badge {
          display: inline-flex;
          align-items: center;
          gap: 4px;
          padding: 4px 10px;
          border-radius: 20px;
          font-size: 0.72rem;
          font-weight: 600;
          background: rgba(16, 185, 129, 0.12);
          color: #6ee7b7;
          border: 1px solid rgba(16, 185, 129, 0.2);
          letter-spacing: 0.01em;
        }

        /* Timestamp */
        .chat-timestamp {
          display: block;
          font-size: 0.68rem;
          color: rgba(156, 163, 175, 0.6);
          margin-top: 8px;
          text-align: right;
        }
        .chat-row-assistant .chat-timestamp {
          text-align: left;
        }

        /* ── Typing Indicator ── */
        .chat-typing-indicator {
          display: flex;
          align-items: center;
          gap: 5px;
          padding: 14px 20px;
          border-radius: 20px;
          border-bottom-left-radius: 6px;
          background: rgba(255, 255, 255, 0.05);
          backdrop-filter: blur(12px);
          -webkit-backdrop-filter: blur(12px);
          border: 1px solid rgba(255, 255, 255, 0.08);
        }
        .chat-typing-dot {
          width: 8px;
          height: 8px;
          border-radius: 50%;
          background: #8b5cf6;
          animation: typing-bounce 1.4s ease-in-out infinite;
        }
        .chat-typing-dot:nth-child(2) {
          animation-delay: 0.16s;
        }
        .chat-typing-dot:nth-child(3) {
          animation-delay: 0.32s;
        }
        @keyframes typing-bounce {
          0%, 60%, 100% {
            transform: translateY(0);
            opacity: 0.4;
          }
          30% {
            transform: translateY(-8px);
            opacity: 1;
          }
        }

        /* ── Suggestions ── */
        .chat-suggestions {
          padding: 0 16px 8px;
          animation: msg-slide-in 0.4s ease-out;
        }
        .chat-suggestions-scroll {
          display: flex;
          gap: 8px;
          overflow-x: auto;
          padding: 8px 0;
          scrollbar-width: none;
          -ms-overflow-style: none;
        }
        .chat-suggestions-scroll::-webkit-scrollbar {
          display: none;
        }
        .chat-suggestion-chip {
          flex-shrink: 0;
          padding: 10px 18px;
          border-radius: 24px;
          border: 1px solid rgba(124, 58, 237, 0.3);
          background: rgba(124, 58, 237, 0.08);
          color: #c4b5fd;
          font-size: 0.825rem;
          font-weight: 500;
          font-family: 'Inter', sans-serif;
          cursor: pointer;
          transition: all 0.25s ease;
          white-space: nowrap;
        }
        .chat-suggestion-chip:hover {
          background: rgba(124, 58, 237, 0.22);
          border-color: rgba(124, 58, 237, 0.6);
          color: #e9ddff;
          transform: translateY(-2px);
          box-shadow: 0 4px 16px rgba(124, 58, 237, 0.2);
        }
        .chat-suggestion-chip:active {
          transform: translateY(0);
        }

        /* ── Input Area ── */
        .chat-input-area {
          padding: 12px 16px 16px;
          background: rgba(17, 24, 39, 0.8);
          backdrop-filter: blur(24px);
          -webkit-backdrop-filter: blur(24px);
          border-top: 1px solid rgba(124, 58, 237, 0.15);
        }
        .chat-input-wrapper {
          display: flex;
          align-items: center;
          gap: 10px;
          background: rgba(255, 255, 255, 0.06);
          border: 1px solid rgba(255, 255, 255, 0.1);
          border-radius: 16px;
          padding: 6px 6px 6px 18px;
          transition: border-color 0.2s ease, box-shadow 0.2s ease;
        }
        .chat-input-wrapper:focus-within {
          border-color: rgba(124, 58, 237, 0.5);
          box-shadow: 0 0 0 3px rgba(124, 58, 237, 0.1),
            0 4px 20px rgba(124, 58, 237, 0.08);
        }
        .chat-input {
          flex: 1;
          background: transparent;
          border: none;
          outline: none;
          color: #f9fafb;
          font-size: 0.935rem;
          font-family: 'Inter', sans-serif;
          padding: 10px 0;
          line-height: 1.4;
        }
        .chat-input::placeholder {
          color: #6b7280;
          font-weight: 400;
        }
        .chat-input:disabled {
          opacity: 0.5;
          cursor: not-allowed;
        }

        .chat-send-btn {
          display: flex;
          align-items: center;
          justify-content: center;
          width: 42px;
          height: 42px;
          border: none;
          border-radius: 12px;
          background: linear-gradient(135deg, #7c3aed, #6d28d9);
          color: white;
          cursor: pointer;
          transition: all 0.25s ease;
          flex-shrink: 0;
        }
        .chat-send-btn:hover:not(:disabled) {
          background: linear-gradient(135deg, #8b5cf6, #7c3aed);
          box-shadow: 0 4px 16px rgba(124, 58, 237, 0.4);
          transform: scale(1.05);
        }
        .chat-send-btn:active:not(:disabled) {
          transform: scale(0.97);
        }
        .chat-send-btn:disabled {
          opacity: 0.4;
          cursor: not-allowed;
        }

        /* Send spinner */
        .chat-send-spinner {
          width: 18px;
          height: 18px;
          border: 2px solid rgba(255, 255, 255, 0.3);
          border-top-color: white;
          border-radius: 50%;
          animation: spin 0.7s linear infinite;
        }
        @keyframes spin {
          to { transform: rotate(360deg); }
        }

        /* Disclaimer */
        .chat-disclaimer {
          text-align: center;
          font-size: 0.68rem;
          color: #4b5563;
          margin-top: 8px;
          letter-spacing: 0.01em;
        }

        /* ── Responsive ── */
        @media (max-width: 640px) {
          .chat-header {
            padding: 12px 14px;
          }
          .chat-message-row {
            max-width: 92%;
          }
          .chat-bubble {
            padding: 12px 14px;
            font-size: 0.89rem;
          }
          .chat-avatar {
            width: 30px;
            height: 30px;
            font-size: 0.85rem;
          }
          .chat-suggestion-chip {
            padding: 8px 14px;
            font-size: 0.78rem;
          }
          .chat-input-wrapper {
            padding: 4px 4px 4px 14px;
          }
          .chat-send-btn {
            width: 38px;
            height: 38px;
          }
        }
      `}</style>
    </div>
  );
}

/* ─── Export with Suspense boundary for useSearchParams ─── */
export default function ChatPage() {
  return (
    <Suspense
      fallback={
        <div
          style={{
            height: '100vh',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            background: '#0a0a1a',
            color: '#7c3aed',
            fontFamily: 'Inter, sans-serif',
            fontSize: '1.1rem',
            gap: '12px',
          }}
        >
          <span style={{ fontSize: '1.5rem' }}>🤖</span>
          Loading GigSaathi AI…
        </div>
      }
    >
      <ChatPageContent />
    </Suspense>
  );
}
