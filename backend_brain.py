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
# FRIEND_LAPTOP_URL = "http://localhost:5000/detections"
FRIEND_LAPTOP_URL = "https://mugwumpian-scottie-homely.ngrok-free.dev/get_coords"
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

            # --- VISUALIZATION SETUP (New) ---
            # Load the map image to draw on
            debug_map = cv2.imread("st_thomas_top_down.png") # Make sure path is correct!
            # ---------------------------------

            slot_status = ['0'] * len(master_config['slots'])

            for det in raw_detections:
                # Defensive check
                if 'x' not in det: continue

                # Transform Logic
                point_vector = np.array([[[det['x'], det['y']]]], dtype=np.float32)
                transformed = cv2.perspectiveTransform(point_vector, h_matrix)
                
                map_x = int(transformed[0][0][0])
                map_y = int(transformed[0][0][1])

                # --- DRAW THE CAR (New) ---
                # Draw a Red Dot where the backend thinks the car is
                cv2.circle(debug_map, (map_x, map_y), 5, (0, 0, 255), -1) 
                # --------------------------

                # 3. Check which slot this point falls into
                for index, slot in enumerate(master_config['slots']):
                    coords = slot['coordinates']
                    
                    # Draw the Slot Box (Green) for reference
                    cv2.rectangle(debug_map, 
                                  (coords['x'], coords['y']), 
                                  (coords['x']+coords['w'], coords['y']+coords['h']), 
                                  (0, 255, 0), 1)

                    if point_in_rect(map_x, map_y, coords['x'], coords['y'], coords['w'], coords['h']):
                        slot_status[index] = '1'
                        # If hit, draw the dot Green to show success
                        cv2.circle(debug_map, (map_x, map_y), 5, (0, 255, 0), -1)
                        break 

            # 4. Update String
            current_status_string = "".join(slot_status)
            print(f"Updated State: {current_status_string}")

            # --- SHOW THE DEBUG WINDOW (New) ---
            # Resize if huge
            debug_map = cv2.resize(debug_map, (800, 600)) 
            cv2.imshow("Backend Brain - God Mode", debug_map)
            cv2.waitKey(1) # Required to update the window
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