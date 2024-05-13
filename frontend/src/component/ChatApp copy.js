import React, { useState, useEffect } from 'react';
import { useRef } from 'react';
import ChatMessage from './ChatMessage';

function ChatApp() {
  const [messages, setMessages] = useState([]);
  const [message, setMessage] = useState('');
  const wsRef = useRef(null);

  useEffect(() => {
    // Handle incoming messages from server
    wsRef.current = new WebSocket('ws://localhost:4000/ws');
    const ws = wsRef.current;
    // Handle incoming messages from server
    ws.onmessage = (event) => {
        const data = JSON.parse(event.data); // Assuming messages are JSON-encoded
        console.log(data);
        console.log("before setting msg")
        console.log(messages)
        setMessages([...messages, data]);
        console.log("after setting msg")
        console.log(messages)
       };

      return () => ws.close();
    }, []);

    const sendMessage = (e) => {
        e.preventDefault();
        if (message.trim()) {
          const ws = wsRef.current;
          console.log(message)
          const your_message = {user:'human',text:message};
          //console.log(your_message)
          //setMessages([...messages, your_message]);
         // console.log(messages)
          ws.send(JSON.stringify(your_message)); // Send message to server

          setMessage(''); // Clear message input after sending
        }
      };

      
      return (
        <div className="chat-app">
          <h2>Chatbot</h2>
          <ul>
            {
            messages.map((msg, index) => (
                
              <ChatMessage key={index} message={msg} />
            ))}
          </ul>
          <form onSubmit={sendMessage}>
            <input
              type="text"
              value={message}
              onChange={(e) => setMessage(e.target.value)}
              placeholder="Type your message..."
            />
            <button type="submit">Send</button>
          </form>
        </div>
      );
    }

export default ChatApp;
