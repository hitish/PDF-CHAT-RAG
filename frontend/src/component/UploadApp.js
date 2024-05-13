import React,  { useState, useEffect } from 'react';
//import Path from 'path';

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
            const delimiter = '\x00';
            const fileReader = new FileReader();

            fileReader.onload = (event) => {
                const arrayBuffer = event.target.result;
                const header = new TextEncoder().encode(`${chatname}${delimiter}${selectedFile.name}${delimiter}`);
                const combinedBuffer = new Uint8Array(header.length + arrayBuffer.byteLength);
                combinedBuffer.set(header);
                combinedBuffer.set(new Uint8Array(arrayBuffer), header.length);
                try{
                    const socket = new WebSocket('ws://localhost:4000/ws/file'); 
                    socket.onopen = () => socket.send(combinedBuffer); 
                    socket.onerror = (error) => console.error('WebSocket error:', error);
                    socket.onmessage = (event) => {
                        const data = JSON.parse(event.data); // Assuming messages are JSON-encoded
                        console.log(data);
                        setchatnamefn(chatname);
                    };
                    setSelectedFile(null);
                }catch(error){
                    console.error('Error sending file data:', error);
                }
            };
            fileReader.readAsArrayBuffer(selectedFile);
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
  