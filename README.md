# Video Processing System

This repository contains a video processing system with two main components:

- **Backend:** A FastAPI application that handles video uploads, real-time WebSocket updates, and triggers background workers (for metadata extraction and video enhancement) using RabbitMQ.
- **Client:** A React application that provides a user interface for uploading videos and viewing real-time processing updates via WebSocket.

---

## Project Structure

```filetree
Backend_assignment
├── Backend
│   ├── requirements.txt
│   ├── run.py
│   ├── app
│   │   ├── __init__.py
│   │   ├── config.py
│   │   ├── main.py
│   │   ├── rabbitmq.py
│   │   └── websocket_manager.py
│   ├── logs
│   │   └── ...              # Logs for workers and server
│   ├── storage              # Storage directory for uploaded/processed videos
│   └── workers
│       ├── enhancement_worker.py
│       ├── metadata_worker.py
│       └── __init__.py
└── client
    ├── frontend
```
---

## Backend Setup

### Requirements

- Python 3.8+
- RabbitMQ

### Installing RabbitMQ

#### Using Docker (Recommended)

If you have Docker installed, you can quickly run RabbitMQ (with the management plugin) using the command:

```bash
docker run -d --hostname rabbitmq --name rabbitmq -p 5672:5672 -p 15672:15672 rabbitmq:3-management
```

- The management console will be available at [http://localhost:15672](http://localhost:15672) (default credentials: guest/guest).

#### Installing Locally (i am using this cause it worked for me)

**On Ubuntu/Debian:**

1. Update packages and install RabbitMQ server:
   ```bash
   sudo apt-get update
   sudo apt-get install rabbitmq-server
   ```

2. Enable and start the RabbitMQ service:
   ```bash
   sudo systemctl enable rabbitmq-server
   sudo systemctl start rabbitmq-server
   ```

3. (Optional) Enable the RabbitMQ management console:
   ```bash
   sudo rabbitmq-plugins enable rabbitmq_management
   ```
   Access the management console at [http://localhost:15672](http://localhost:15672) (default credentials: guest/guest).

**On macOS:**

If you have Homebrew installed, use:
```bash
brew update
brew install rabbitmq
brew services start rabbitmq
```
And enable the management plugin if needed:
```bash
rabbitmq-plugins enable rabbitmq_management
```

### Docker (Work in Progress)

Docker Compose files (`docker-compose.yml` and `Dockerfile`) will be added, but Docker deployment is still being finalized. If you prefer, you can run the backend locally using the instructions below.

### Running the Backend Locally

1. Change directory to the backend folder:
   ```bash
   cd Backend_assignment/Backend
   ```

2. Create a new virtual environment and activate it:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

3. Install the dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Ensure RabbitMQ is running on your machine, or update the configuration in `app/config.py` to point to your RabbitMQ instance.

5. Run the backend server:
   ```bash
   python run.py
   ```

The FastAPI server will be available at:  
- **HTTP API:** `http://localhost:8000/`  
- **WebSocket Endpoint:** `ws://localhost:8000/ws/<client_id>` (e.g., `ws://localhost:8000/ws/client123`)

---

## Client Setup

### Requirements

- Node.js (v14 or above)
- npm or yarn

### Running the Client

1. Change to the client directory:
   ```bash
   cd /Backend_assignment/client
   ```

2. Install dependencies:
   ```bash
   npm install
   ```

3. Start the React development server:
   ```bash
   npm start
   ```

The client will run on: [http://localhost:3000](http://localhost:3000).

---

## How It Works

1. **Video Upload:**  
   Users can select a video file and upload it to the backend at `POST http://localhost:8000/upload` with an `x-client-id` header (e.g., `client123`).

2. **Background Processing:**  
   - **Metadata Extraction:** A worker extracts metadata (duration, dimensions, FPS, etc.) from the video.
   - **Video Enhancement:** A worker enhances the video and saves an updated version.  
   Both workers communicate their status back to the backend via internal endpoints.

3. **Real-Time Updates:**  
   The backend sends updates via a WebSocket endpoint. The React client listens for these updates and displays them in real time.

4. **Storage:**  
   Uploaded and processed videos are stored in the `Backend/storage` directory.

---
