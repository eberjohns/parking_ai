import streamlit as st
import cv2
from ultralytics import YOLO
import requests
import pandas as pd
import tempfile

st.set_page_config(page_title="Smart Parking AI", layout="wide")
st.title("🅿️ Vehicle Detection & JSON Bridge")

# Sidebar for AI and API configuration
st.sidebar.header("Settings")
conf_level = st.sidebar.slider("Confidence", 0.0, 1.0, 0.25)
api_url = st.sidebar.text_input("Server URL", "http://127.0.0.1:8000/update_data")

# Initialize YOLO
model = YOLO("yolov8n.pt")
uploaded_video = st.file_uploader("Upload Parking Video", type=["mp4", "mov"])

if uploaded_video:
    tfile = tempfile.NamedTemporaryFile(delete=False)
    tfile.write(uploaded_video.read())
    cap = cv2.VideoCapture(tfile.name)
    
    st_frame = st.empty()

    while cap.isOpened():
        ret, frame = cap.read()
        
        # --- VIDEO LOOPING LOGIC ---
        if not ret:
            cap.set(cv2.CAP_PROP_POS_FRAMES, 0) # Reset to start
            ret, frame = cap.read()
            if not ret: break

        # Run AI (Classes 2,3,5,7 = Car, Motorcycle, Bus, Truck)
        results = model.predict(frame, conf=conf_level, imgsz=1280, classes=[2,3,5,7], verbose=False)
        
        current_frame_data = []
        for box in results[0].boxes:
            x, y, _, _ = box.xywh[0].tolist()
            label = model.names[int(box.cls[0])]
            current_frame_data.append({ "x": round(x, 1), "y": round(y, 1),"type": label,})

        # --- UPDATE THE BRIDGE ---
        try:
            # We "push" the data to the FastAPI server
            requests.get(api_url, params={"data": str(current_frame_data)}, timeout=0.01)
        except:
            pass

        # Display Live Feed
        st_frame.image(results[0].plot(), channels="BGR", use_container_width=True)

    cap.release()