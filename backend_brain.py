import cv2
import numpy as np
import requests
import json
import time
from fastapi import FastAPI
from threading import Thread
from fastapi.middleware.cors import CORSMiddleware  # <--- IMPORT THIS

app = FastAPI()

# --- PASTE THIS BLOCK EXACTLY ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows ALL origins (Laptop 3, Phone, etc.)
    allow_credentials=True,
    allow_methods=["*"],  # Allows ALL methods (GET, POST, etc.)
    allow_headers=["*"],  # Allows ALL headers (Content-Type, ngrok-skip, etc.)
)

# --- CONFIGURATION ---
FRIEND_LAPTOP_URL = "http://localhost:5000/detections"
#FRIEND_LAPTOP_URL = "https://mugwumpian-scottie-homely.ngrok-free.dev/get_coords"
MATRIX_FILE = "matrix.npy"
SLOTS_CONFIG_FILE = "./config.json"
# ---------------------

# Load Configuration ONCE
with open(SLOTS_CONFIG_FILE, 'r') as f:
    master_config = json.load(f)

# Load Matrix
try:
    h_matrix = np.load(MATRIX_FILE)
except:
    print("CRITICAL ERROR: Matrix file not found. Run calibration first.")
    h_matrix = np.eye(3) # Fallback to prevent crash

# GLOBAL STATE (The String)
# We initialize it with all '0's based on number of slots
current_status_string = "0" * len(master_config['slots'])

def point_in_rect(x, y, rx, ry, rw, rh):
    """Simple check if a point (x,y) is inside a rectangle."""
    return (rx <= x <= rx + rw) and (ry <= y <= ry + rh)

def processing_loop():
    """
    Runs in background: Fetches from Friend -> Transforms -> Updates String
    """
    global current_status_string
    
    while True:
        try:
            # 1. GET Raw Coords from Friend's Vision System
            # Expected format: [{"x": 200, "y": 450, "type": "car"}, ...]
            response = requests.get(FRIEND_LAPTOP_URL, timeout=1)
            raw_detections = response.json()
            
            # Temporary list to track occupied slots for this frame
            # 0 = Empty, 1 = Occupied (Simplified for MVP)
            # You can change '1' to 'C' or 'B' later

            print(f"DEBUG RAW DATA: {raw_detections}") 
            print(f"DEBUG TYPE: {type(raw_detections)}")

            slot_status = ['0'] * len(master_config['slots'])

            # 2. Loop through every detected car
            for det in raw_detections:
                # IMPORTANT: Use the bottom-center of the bounding box!
                # If friend sends x,y (center), adjust if needed.
                # Assuming friend sends the "footprint" x,y.
                
                # Transform Logic
                point_vector = np.array([[[det['x'], det['y']]]], dtype=np.float32)
                transformed = cv2.perspectiveTransform(point_vector, h_matrix)
                
                map_x = transformed[0][0][0]
                map_y = transformed[0][0][1]

                # 3. Check which slot this point falls into
                for index, slot in enumerate(master_config['slots']):
                    coords = slot['coordinates'] 
                    slot_x = coords['x']
                    slot_y = coords['y']
                    slot_w = coords['w']
                    slot_h = coords['h']

                    if point_in_rect(map_x, map_y, slot_x, slot_y, slot_w, slot_h):
                        # We found a match!
                        # Mark this slot index as Occupied
                        slot_status[index] = '1' 
                        break # Stop checking other slots for this specific car

            # 4. Update the Global String
            current_status_string = "".join(slot_status)
            print(f"Updated State: {current_status_string}")

        except Exception as e:
            print(f"Error fetching from Vision Edge: {e}")
        
        # Don't spam the network; wait a bit
        time.sleep(0.5)

# Start the background processing thread
processor_thread = Thread(target=processing_loop, daemon=True)
processor_thread.start()

# --- API ENDPOINTS FOR FRONTEND ---

@app.get("/api/config")
def get_config():
    """Frontend calls this ONCE on load to know where to draw boxes."""
    return master_config

@app.get("/api/status")
def get_status():
    """Frontend calls this repeatedly to color the boxes."""
    return {
        "lot_id": master_config['lot_id'],
        "status_string": current_status_string
    }

# Run with: uvicorn backend_brain:app --host 0.0.0.0 --port 8000