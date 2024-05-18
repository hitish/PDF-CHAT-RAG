
import React, { useState, useEffect } from 'react';
import { useRef } from 'react';
import ChatApp from './component/ChatApp';
//import LoginApp from './component/LoginApp';
import UploadApp from './component/UploadApp';

function App() {
  const [websocketConnected, setWebSocketConnected] = useState(false);
  const [chatinitiated, setchatinitiated] = useState(false);
  const [chatname, setchatname] = useState('');
  
  const wsRef = useRef(null);

  useEffect(() => {
    wsRef.current = new WebSocket('ws://localhost:4000/ws');
    const ws = wsRef.current;

    ws.onopen = () => {
      setWebSocketConnected(true);
      
    }
    ws.onerror = (error) => {
      console.error('WebSocket error:', error);
    }

    return () => ws.close();
  }, []);

  const handlechatname=(chatname)=>{
    setchatname(chatname);
    setchatinitiated(true);
  }

  return (
    <div>
      
      { chatinitiated?(
      <div className="App">
        <ChatApp ws={wsRef.current}  chatname = {chatname}  />
      </div>
      ):(<div className="App">
      <UploadApp ws={wsRef.current} setchatnamefn={handlechatname} />
    </div>)}
     </div>
  );
}

export default App;
