// import React, { useState } from 'react';
// import logo from './logo.svg';
// import './App.css';

// function App() {
//   const [selectedFile, setSelectedFile] = useState(null);
//   const [uploadStatus, setUploadStatus] = useState('');
//   const [wsData, setWsData] = useState(null);
//   const [socket, setSocket] = useState(null);

//   // Function to establish WebSocket connection
//   const connectWebSocket = () => {
//     if (socket && socket.readyState === WebSocket.OPEN) {
//       console.log('WebSocket already connected');
//       return;
//     }

//     const newSocket = new WebSocket('ws://localhost:8000/ws/client123');

//     newSocket.onopen = () => {
//       console.log('WebSocket connected');
//     };

//     newSocket.onmessage = (event) => {
//       try {
//         const data = JSON.parse(event.data);
//         setWsData(data);
//       } catch (error) {
//         console.error('Error parsing WebSocket message:', error);
//       }
//     };

//     newSocket.onerror = (error) => {
//       console.error('WebSocket error:', error);
//     };

//     newSocket.onclose = () => {
//       console.log('WebSocket disconnected');
//       setSocket(null);
//     };

//     setSocket(newSocket);
//   };

//   // Handle video file selection
//   const handleFileChange = (event) => {
//     setSelectedFile(event.target.files[0]);
//   };

//   // Handle file upload via HTTP
//   const handleUpload = async () => {
//     if (!selectedFile) return;
//     setUploadStatus('Uploading...');
//     const formData = new FormData();
//     formData.append('file', selectedFile);

//     try {
//       const response = await fetch('http://localhost:8000/upload', {
//         method: 'POST',
//         headers: {'x-client-id': 'client123'},
//         body: formData,
//       });

//       if (response.ok) {
//         setUploadStatus('Upload successful!');
//       } else {
//         setUploadStatus('Upload failed.');
//       }
//     } catch (error) {
//       console.error('Upload error:', error);
//       setUploadStatus('Upload error.');
//     }
//   };

//   return (
//     <div className="App">
//       <header className="App-header">
//         <img src={logo} className="App-logo" alt="logo" />
//         <h1>Client Interface</h1>
//         <section style={{ margin: '20px' }}>
//           <h2>Video Upload</h2>
//           <input type="file" accept="video/*" onChange={handleFileChange} />
//           <button onClick={handleUpload}>Upload Video</button>
//           <p>{uploadStatus}</p>
//         </section>
//         <section style={{ margin: '20px' }}>
//           <h2>WebSocket Connection</h2>
//           {!socket ? (
//             <button onClick={connectWebSocket}>Connect WebSocket</button>
//           ) : (
//             <p>WebSocket is connected</p>
//           )}
//         </section>
//         <section style={{ margin: '20px' }}>
//   <h2>WebSocket Data</h2>
//   {wsData ? (
//     <div>
//       <p>Metadata: {JSON.stringify(wsData.metadata)}</p>
//       {wsData.videoUrl && (
//         <video controls src={wsData.videoUrl} width="400" />
//       )}
//     </div>
//   ) : (
//     <p>No data received yet from WebSocket.</p>
//   )}
// </section>
//       </header>
//     </div>
//   );
// }

// export default App;


import React, { useState } from 'react';
import './App.css';

function App() {
  const [selectedFile, setSelectedFile] = useState(null);
  const [uploadStatus, setUploadStatus] = useState('');
  const [wsData, setWsData] = useState(null);
  const [socket, setSocket] = useState(null);

  // Function to establish WebSocket connection
  const connectWebSocket = () => {
    if (socket && socket.readyState === WebSocket.OPEN) {
      console.log('WebSocket already connected');
      return;
    }

    const newSocket = new WebSocket('ws://localhost:8000/ws/client123');

    newSocket.onopen = () => {
      console.log('WebSocket connected');
    };

    newSocket.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        setWsData(data);
      } catch (error) {
        console.error('Error parsing WebSocket message:', error);
      }
    };

    newSocket.onerror = (error) => {
      console.error('WebSocket error:', error);
    };

    newSocket.onclose = () => {
      console.log('WebSocket disconnected');
      setSocket(null);
    };

    setSocket(newSocket);
  };

  // Handle video file selection
  const handleFileChange = (event) => {
    setSelectedFile(event.target.files[0]);
  };

  // Handle file upload via HTTP
  const handleUpload = async () => {
    if (!selectedFile) return;
    setUploadStatus('Uploading...');
    const formData = new FormData();
    formData.append('file', selectedFile);

    try {
      const response = await fetch('http://localhost:8000/upload', {
        method: 'POST',
        headers: { 'x-client-id': 'client123' },
        body: formData,
      });

      if (response.ok) {
        setUploadStatus('Upload successful!');
      } else {
        setUploadStatus('Upload failed.');
      }
    } catch (error) {
      console.error('Upload error:', error);
      setUploadStatus('Upload error.');
    }
  };

  return (
    <div className="App">
      <header className="App-header">
        <h1>Client Interface</h1>
        <div className="card-container">
          <div className="card">
            <h2 className="card-title">Video Upload</h2>
            <input
              type="file"
              accept="video/*"
              onChange={handleFileChange}
              className="file-input"
            />
            <button onClick={handleUpload} className="btn-primary">
              Upload Video
            </button>
            <p className="status">{uploadStatus}</p>
          </div>
          <div className="card">
            <h2 className="card-title">WebSocket Connection</h2>
            {!socket ? (
              <button onClick={connectWebSocket} className="btn-primary">
                Connect WebSocket
              </button>
            ) : (
              <p className="status">WebSocket is connected</p>
            )}
          </div>
          <div className="card">
            <h2 className="card-title">WebSocket Data</h2>
            {wsData ? (
              <div className="data-container">
                <p>Metadata: {JSON.stringify(wsData.metadata)}</p>
                {wsData.videoUrl && (
                  <video
                    controls
                    src={wsData.videoUrl}
                    width="400"
                    className="video-player"
                  />
                )}
              </div>
            ) : (
              <p className="status">No data received yet from WebSocket.</p>
            )}
          </div>
        </div>
      </header>
    </div>
  );
}

export default App;