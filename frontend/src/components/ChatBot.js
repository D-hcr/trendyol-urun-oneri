import React, { useState } from 'react';
import axios from 'axios';

const ChatBot = () => {
  const [input, setInput] = useState('');
  const [messages, setMessages] = useState([]);

  const handleSend = async () => {
    if (!input.trim()) return;

    const newMessages = [...messages, { sender: 'user', text: input }];
    setMessages(newMessages);

    try {
      const response = await axios.post('http://localhost:8000/chat', { message: input });
      const botReply = response.data.reply;
      setMessages(prev => [...prev, { sender: 'bot', text: botReply }]);
    } catch (error) {
      console.error(error);
      setMessages(prev => [...prev, { sender: 'bot', text: "Sunucu hatası." }]);
    }

    setInput('');
  };

  return (
    <div style={{ padding: 20 }}>
      <h2>Güneş Kremi Chat Botu ☀️</h2>
      <div style={{ minHeight: '300px', border: '1px solid gray', padding: 10, marginBottom: 10 }}>
        {messages.map((msg, idx) => (
          <div key={idx} style={{ textAlign: msg.sender === 'user' ? 'right' : 'left' }}>
            <p><strong>{msg.sender === 'user' ? 'Sen' : 'Bot'}:</strong> {msg.text}</p>
          </div>
        ))}
      </div>
      <input
        value={input}
        onChange={e => setInput(e.target.value)}
        onKeyDown={(e) => e.key === 'Enter' && handleSend()}
        style={{ width: '80%', marginRight: 10 }}
        placeholder="Mesaj yaz..."
      />
      <button onClick={handleSend}>Gönder</button>
    </div>
  );
};

export default ChatBot;
