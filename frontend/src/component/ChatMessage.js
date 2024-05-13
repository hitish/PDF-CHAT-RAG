import React from 'react';

function ChatMessage({ message }) {
  
  const { user, text } = message; 
  
  console.log(user)
  //console.log(text)
     
  return (
    <li className={`chat-message ${user == 'human' ? 'me' : 'bot'}`}>
      {user == 'human' ? (
        <span className="you">human: </span>
      ) : (
        <span className="bot">Chatbot: </span>
      )}
      {text}
      {user}
    </li>

  );
}

export default ChatMessage;
