from fastapi import FastAPI, UploadFile, File, WebSocket, WebSocketDisconnect, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
import os
import aiofiles
from app.rabbitmq import publish_task
from app.websocket_manager import ws_manager
from app.config import STORAGE_DIR
from pydantic import BaseModel

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Track processing status for each file
file_processing_status = {}

class StatusUpdate(BaseModel):
    client_id: str
    filename: str

class MetadataUpdate(BaseModel):
    client_id: str
    metadata: dict

# Function to check if a file is fully processed
def is_fully_processed(filename):
    if filename not in file_processing_status:
        return False
    
    status = file_processing_status[filename]
    return status.get("enhanced", False) and status.get("metadata", False)

# WebSocket endpoint for real-time client updates
@app.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: str):
    await ws_manager.connect(websocket, client_id)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        await ws_manager.disconnect(client_id)


@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.post("/upload")
async def upload_video(request: Request, file: UploadFile = File(...)):
    # Get client ID from headers or cookies
    client_id = request.headers.get("x-client-id", "anonymous")
    
    file_path = os.path.join(STORAGE_DIR, file.filename)
    async with aiofiles.open(file_path, 'wb') as out_file:
        content = await file.read()
        await out_file.write(content)
    
    # Initialize processing status
    file_processing_status[file.filename] = {
        "enhanced": False,
        "metadata": False,
        "client_id": client_id
    }
    
    # Publish a task to RabbitMQ
    publish_task({"filename": file.filename, "client_id": client_id})
    
    return {"message": "File uploaded successfully", "filename": file.filename}


# Internal endpoint for video enhancement status update
@app.post("/internal/video-enhancement-status")
async def video_enhancement_status(data: StatusUpdate):
    client_id = data.client_id
    filename = data.filename
    
    original_filename = filename.replace("enhanced_", "")
    if original_filename in file_processing_status:
        file_processing_status[original_filename]["enhanced"] = True
        
        # Send update to client
        await ws_manager.send_message(client_id, {
            "type": "enhanced", 
            "filename": filename
        })
        
        # Check if both processes are complete
        if is_fully_processed(original_filename):
            await ws_manager.send_message(client_id, {
                "type": "completed",
                "filename": original_filename,
                "metadata": file_processing_status[original_filename].get("metadata_data", {})
            })
    
    return {"message": "Video enhancement status updated."}

# Internal endpoint for metadata extraction status update
@app.post("/internal/metadata-extraction-status")
async def metadata_extraction_status(data: MetadataUpdate):
    client_id = data.client_id
    metadata = data.metadata
    filename = metadata.get("filename")
    
    if filename in file_processing_status:
        file_processing_status[filename]["metadata"] = True
        file_processing_status[filename]["metadata_data"] = metadata
        
        # Send update to client
        await ws_manager.send_message(client_id, {
            "type": "metadata", 
            "metadata": metadata
        })
        
        # Check if both processes are complete
        if is_fully_processed(filename):
            await ws_manager.send_message(client_id, {
                "type": "completed",
                "filename": filename,
                "enhanced_filename": f"enhanced_{filename}",
                "metadata": metadata
            })
    
    return {"message": "Metadata extraction status updated."}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
