# ParKARO 🚗🗺️

## Smart Open-to-Sky Parking Detection & Management System

ParKARO is a low-cost, computer-vision-based parking management system designed for unstructured environments. Unlike traditional sensors, it uses a "Digital Twin" approach: transforming a standard CCTV camera feed into a geospatial top-down map to detect vehicle occupancy, classify vehicle types (Bike/Car/SUV), and optimize parking space usage.

---

## 🌟 Features
- **Digital Twin Mapping:** Real-time perspective transformation (Homography) from angled CCTV to 2D Map.
- **Active Defragmentation:** Identifies available gaps based on vehicle size (Bike vs. SUV) to maximize capacity.
- **Low-Bandwidth Architecture:** Edge processing sends only lightweight JSON coordinates, not video streams.
- **Drift-Resistant:** Separation of static configuration (Map) and dynamic status (Live Feed).

---

## 📂 Repository Structure
- `backend_brain.py` - The central FastAPI server that acts as the "State Manager."
- `edge_node.py` *(or `simulator.py`)* - The AI processing unit that runs YOLOv8 and sends coordinates.
- `calibration.py` - Tool to map your camera view to the top-down map (generates `matrix.npy`).
- `build_config.py` - Tool to draw parking slots on your map (generates `config.json`).
- `index.html` - The frontend dashboard for users/admins.
- `requirements.txt` - Python dependencies.

---

## 🚀 Setup Guide: How to deploy for your own location

Follow these 4 phases to set up ParKARO for a new parking lot.

### Prerequisites
- Python 3.9+
- A webcam or video file (for testing).
- A top-down screenshot of your parking lot (from Google Maps).

### Installation
Clone the repository:
```bash
git clone https://github.com/eberjohns/parking_ai.git
cd parking_ai
```
Install dependencies:
```bash
pip install fastapi uvicorn opencv-python numpy ultralytics requests
```

---

### Phase 1: Asset Preparation
You need two images in the root folder:
- `camera_view.png`: A screenshot from your CCTV camera (or video).
- `top_down_view.png`: A screenshot of the same area from Google Maps Satellite view.

*(Note: Rename your images to match these names or update the scripts accordingly.)*

---

### Phase 2: Calibration (The Mathematics)
We need to teach the system how to translate pixels from the camera to the map.
Run the calibration tool:
```bash
python calibration.py
```
- **Window 1 (Camera View):** Click 4 distinct landmarks (e.g., 4 corners of the lot).
- **Window 2 (Top-Down View):** Click the same 4 landmarks in the same order.
- Press any key. The script will generate a `matrix.npy` file.

---

### Phase 3: Slot Configuration (The Digital Twin)
Now we define where the parking spots are on the map.
Run the builder tool:
```bash
python build_config.py
```
- Draw green boxes around every parking slot on your map image using your mouse.
- Press `s` to save.
- This generates `config.json`.
- *Optional:* Open `config.json` manually to change `type: "car"` to `type: "bike"` or `type: "suv"` for specific slots.

---

### Phase 4: Launching the System
You will need 3 separate terminals running simultaneously.

#### Terminal 1: The Backend (Brain)
This manages the state and serves the API.
```bash
python backend_brain.py
```
Verify: Open [http://localhost:8000/api/config](http://localhost:8000/api/config) in your browser. You should see your JSON data.

#### Terminal 2: The Edge Node (Eyes)
This runs the AI (or Simulator) to detect cars.

**Option A: Use the Simulator (No Camera needed)**  
Perfect for testing. Click to place "fake" cars.
```bash
python simulator.py
```
**Option B: Use Real AI (YOLOv8)**  
Requires a webcam or video file.
```bash
python edge_node.py
```

#### Terminal 3: The Frontend (Interface)
To avoid CORS errors, serve the HTML file using Python:
```bash
python -m http.server 8081
```
Now, open your browser and visit: 👉 [http://localhost:8081](http://localhost:8081)

---

## 🔧 Customization

### Changing the Camera Source
In `edge_node.py`, locate the line:
```python
# For Webcam
cap = cv2.VideoCapture(0)

# For IP Camera (RTSP)
# cap = cv2.VideoCapture("rtsp://admin:password@192.168.1.45:554/stream")
```

### Running on Multiple Devices
To run the Backend on one laptop and the Frontend on another:
1. Find the Backend Laptop's IP (e.g., `192.168.1.5`).
2. In `index.html`, update the config:
```js
const API_BASE_URL = "http://192.168.1.5:8000";
```
3. Ensure both devices are on the same Wi-Fi.

---

## 🆘 Troubleshooting

**Q: The map boxes are green but don't turn red when I click a car.**
- Check Backend: Look at the Terminal running `backend_brain.py`. Is it printing `Updated State: ...`?
- Check Matrix: Did you click the points in the exact same order during calibration? Run `python calibration.py` again.

**Q: "CORS Error" in Browser Console.**
- Ensure `backend_brain.py` includes the CORSMiddleware block (see code).
- If using Ngrok, ensure your `index.html` fetch headers include `"ngrok-skip-browser-warning": "true"`.

---

## 📜 License
This project was developed for the GIS Mapathon Challenge. Open for educational use.
