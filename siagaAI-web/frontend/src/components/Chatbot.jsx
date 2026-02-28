import { useState, useRef, useEffect } from 'react'

function Chatbot({ location = 'jakarta', onClose }) {
  const [messages, setMessages] = useState([
    {
      id: 1,
      sender: 'bot',
      text: `👋 Halo! Saya SiagaAI, asisten darurat bencana Anda.

Saya siap membantu Anda dengan:
• 🏃 Informasi rute evakuasi
• 🏥 Panduan pertolongang pertama  
• ⚠️ Info risiko bencana terkini
• 📞 Kontak layanan darurat

Silakan tanyakan apa yang Anda butuhkan!`,
      timestamp: new Date()
    }
  ])
  const [inputMessage, setInputMessage] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const messagesEndRef = useRef(null)

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  const handleSendMessage = async () => {
    if (!inputMessage.trim() || isLoading) return

    const userMessage = {
      id: Date.now(),
      sender: 'user',
      text: inputMessage,
      timestamp: new Date()
    }

    setMessages(prev => [...prev, userMessage])
    setInputMessage('')
    setIsLoading(true)

    try {
      const response = await fetch('/api/chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          message: userMessage.text,
          city: location
        })
      })

      const data = await response.json()

      const botMessage = {
        id: Date.now() + 1,
        sender: 'bot',
        text: data.response,
        timestamp: new Date(data.timestamp)
      }

      setMessages(prev => [...prev, botMessage])
    } catch (error) {
      console.error('Error sending message:', error)
      const errorMessage = {
        id: Date.now() + 1,
        sender: 'bot',
        text: 'Maaf, terjadi kesalahan. Silakan coba lagi.',
        timestamp: new Date()
      }
      setMessages(prev => [...prev, errorMessage])
    }

    setIsLoading(false)
  }

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSendMessage()
    }
  }

  const quickActions = [
    { label: '🚑', message: 'Bagaimana pertolongan pertama saat banjir?' },
    { label: '🏃', message: 'Apa rute evakuasi terdekat?' },
    { label: '⚠️', message: 'Berapa tingkat risiko bencana di sini?' },
    { label: '📞', message: 'Apa nomor telepon darurat?' }
  ]

  return (
    <div className="glass-card overflow-hidden border border-primary-500/20 shadow-2xl shadow-primary-500/10">
      {/* Header */}
      <div className="bg-gradient-to-r from-success-600 to-success-700 p-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <div className="w-12 h-12 bg-white/20 rounded-xl flex items-center justify-center backdrop-blur">
              <span className="text-2xl">🤖</span>
            </div>
            <div>
              <h3 className="font-bold text-white">SiagaAI Assistant</h3>
              <p className="text-xs text-success-200">Online • Siap Membantu</p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="text-white/80 hover:text-white transition-colors p-2"
          >
            <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>
      </div>

      {/* Messages */}
      <div className="h-80 overflow-y-auto p-4 bg-dark-bg/50 space-y-4">
        {messages.map((message) => (
          <div
            key={message.id}
            className={`flex ${message.sender === 'user' ? 'justify-end' : 'justify-start'}`}
          >
            <div
              className={`max-w-[85%] rounded-2xl p-4 ${
                message.sender === 'user'
                  ? 'bg-gradient-to-r from-primary-600 to-primary-700 text-white'
                  : 'bg-dark-card border border-dark-border text-dark-text'
              }`}
            >
              <p className="text-sm whitespace-pre-wrap leading-relaxed">{message.text}</p>
              <p className={`text-xs mt-2 ${message.sender === 'user' ? 'text-primary-200' : 'text-dark-muted'}`}>
                {message.timestamp.toLocaleTimeString('id-ID', { hour: '2-digit', minute: '2-digit' })}
              </p>
            </div>
          </div>
        ))}
        
        {isLoading && (
          <div className="flex justify-start">
            <div className="bg-dark-card border border-dark-border rounded-2xl p-4">
              <div className="flex space-x-2">
                <div className="w-2 h-2 bg-primary-500 rounded-full animate-bounce"></div>
                <div className="w-2 h-2 bg-primary-500 rounded-full animate-bounce" style={{ animationDelay: '0.1s' }}></div>
                <div className="w-2 h-2 bg-primary-500 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
              </div>
            </div>
          </div>
        )}
        
        <div ref={messagesEndRef} />
      </div>

      {/* Quick Actions */}
      <div className="px-4 py-3 bg-dark-card/50 border-t border-dark-border">
        <div className="flex flex-wrap gap-2">
          {quickActions.map((action, index) => (
            <button
              key={index}
              onClick={() => {
                setInputMessage(action.message)
              }}
              className="text-xs px-3 py-1.5 bg-dark-border hover:bg-dark-border/80 rounded-full transition-colors text-dark-muted hover:text-dark-text"
            >
              {action.label}
            </button>
          ))}
        </div>
      </div>

      {/* Input */}
      <div className="p-4 bg-dark-card/50 border-t border-dark-border">
        <div className="flex space-x-3">
          <input
            type="text"
            value={inputMessage}
            onChange={(e) => setInputMessage(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder="Ketik pesan Anda..."
            className="input-field"
          />
          <button
            onClick={handleSendMessage}
            disabled={!inputMessage.trim() || isLoading}
            className="px-5 py-3 bg-gradient-to-r from-success-500 to-success-600 text-white rounded-xl hover:from-success-600 hover:to-success-700 disabled:opacity-50 disabled:cursor-not-allowed transition-all shadow-lg shadow-success-500/25 hover:shadow-success-500/40"
          >
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8" />
            </svg>
          </button>
        </div>
      </div>
    </div>
  )
}

export default Chatbot
