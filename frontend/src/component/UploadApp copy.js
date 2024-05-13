import React,  { useState, useEffect } from 'react';

function UploadApp({ws,setchatnamefn}) {

    const [chatname, setchatname] = useState('');
    const [selectedFile, setSelectedFile] = useState(null);
    
      
    const handleFileChange = (event) => {
        const file = event.target.files[0];
        if (file) {
          setSelectedFile(file);
        } else {
          setSelectedFile(null);
        }
      };
      
      useEffect(() => {
            if(ws)
                {
                    ws.onmessage = (event) => {
                        const data = JSON.parse(event.data); // Assuming messages are JSON-encoded
                        console.log(data);
                        
                        setchatnamefn(chatname);
                    };
                }
            
    }, [ws]);


      const startchat = async(e) => {
        e.preventDefault();
        if (chatname && ws && selectedFile) {
           
           const msg = {name:chatname};
           ws.send(JSON.stringify(msg));
           alert('message sent complete');
           const reader = new FileReader();
            reader.onload = (event) => {
            const fileContent = event.target.result;
            const socket = new WebSocket('ws://localhost:4000/ws/file'); // Create a new socket for each file (optional)
            socket.onopen = () => socket.send(fileContent); // Send the file content
            socket.onerror = (error) => console.error('WebSocket error:', error);
            setSelectedFile(null);
          };
          reader.readAsArrayBuffer(selectedFile);
        
        } else {
          alert('Please select a file and ensure the connection is established.');
        }
      };

    return (
      <div>
        <div className="uploadapp">
        <h2>{chatname}</h2>
          <form >
            <input
              type="text"
              value={chatname}
              onChange={(e) => setchatname(e.target.value)}
              placeholder="Create a name for Chat"
            />
            <input type="file" onChange={handleFileChange} />
               {ws ? (
                 <button onClick={startchat}>Start Chat</button>
                  ) : (
                   <p>Connecting to WebSocket...</p>
                )}

            
          </form>
        </div>
      </div>
    );
  }
  
  export default UploadApp;
  