import React, { useState, useEffect } from 'react';
import { useRef } from 'react';
import ChatMessage from './ChatMessage';

function ChatApp({ ws,chatname }) {
  const [messages, setMessages] = useState([]);
  const [message, setMessage] = useState('');
  

 
  useEffect(() => {
  
    if(chatname && messages.length == 0)
      {
        console.log("this is first message to be printed");
        const msg = "Hello, your chat " + chatname + " is set up. ";
        const first_message = {user:'bot',text:msg};
        setMessages([...messages, first_message]);
        const second_message = {user:'bot',text:"You can ask questions related to file shared "};
        setMessages((prevMessages) => [...prevMessages, second_message]);
      }
    
    // Handle incoming messages from server
    if(ws)
      {
        ws.onmessage = (event) => {
            const data = JSON.parse(event.data); 
            setMessages((prevMessages) => [...prevMessages, data]);
          };
        }    
      
    }, [ws]);

    

    const sendMessage = (e) => {
        e.preventDefault();
        if (message.trim() && ws) {
          const your_message = {user:'human',chatname:chatname, text:message}
          setMessages((prevMessages) => [...prevMessages, your_message]);
          ws.send(JSON.stringify(your_message)); 
          setMessage(''); 
        }
      };

      

      return (
        <div className="chat-app">
          
          <h2>Chatbot</h2>
          <ul>
            {
            messages.map((msg, index) => (
                <li key={index}>
                        {console.log(messages)}
                        {msg.user ? (
                            <span className="user-message">{msg.user}: {msg.text}</span>
                        ) : (
                            <span className="bot-message">{msg.text}</span>
                        )}
                </li>
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
