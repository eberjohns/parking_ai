from fastapi import FastAPI

import uvicorn

import ast



app = FastAPI()



# This variable stores the state of the 'current' frame

latest_frame_results = {

    "status": "Waiting for AI...",

    "vehicles": []

}



@app.get("/update_data")

def update_data(data: str):

    """Internal endpoint: Streamlit calls this to push new coordinates."""

    global latest_frame_results

    try:

        # Convert string back to Python list safely

        vehicle_list = ast.literal_eval(data)

        latest_frame_results = {

            "status": "Live",

            "count": len(vehicle_list),

            "vehicles": vehicle_list

        }

        return {"status": "success"}

    except:

        return {"status": "error"}



@app.get("/get_coords")

def get_coords():

    """Public endpoint: Your friend calls this to get the JSON response."""

    return latest_frame_results



if __name__ == "__main__":

    uvicorn.run(app, host="0.0.0.0", port=8000)





import streamlit as st

import cv2

from ultralytics import YOLO

import requests

import pandas as pd

import tempfile

from sahi import AutoDetectionModel

from sahi.predict import get_sliced_prediction



# --- Page Setup ---

st.set_page_config(page_title="Smart Parking AI", layout="wide")

st.title("🅿️ Vehicle Detection & API Sync")



# --- Sidebar Configuration ---

st.sidebar.header("AI Settings")

model_path = st.sidebar.selectbox("Model", ["yolov8n.pt", "yolov8s.pt"])

conf_level = st.sidebar.slider("Confidence", 0.0, 1.0, 0.25)

use_sahi = st.sidebar.toggle("Enable Aerial Slicing (SAHI)", value=True)



st.sidebar.header("API Settings")

server_url = st.sidebar.text_input("Server Update URL", "http://127.0.0.1:8000/update_data")



# Only detect specific vehicle classes

VEHICLE_CLASSES = ["car", "motorcycle", "bus", "truck"]



# --- Initialize Models ---

standard_model = YOLO(model_path)

detection_model = AutoDetectionModel.from_pretrained(

    model_type='ultralytics',

    model_path=model_path,

    confidence_threshold=conf_level,

    device="cpu"

)



uploaded_video = st.file_uploader("Upload Parking Video", type=["mp4", "mov"])



if uploaded_video:

    tfile = tempfile.NamedTemporaryFile(delete=False)

    tfile.write(uploaded_video.read())

    cap = cv2.VideoCapture(tfile.name)

    

    st_frame = st.empty()

    st_table = st.empty()



    while cap.isOpened():

        ret, frame = cap.read()

        if not ret: break

        

        current_frame_data = []

        annotated_frame = frame.copy()

        

        if use_sahi:

            # Sliced detection for high-res aerial footage

            result = get_sliced_prediction(

                frame, detection_model, slice_height=640, slice_width=640

            )

            for pred in result.object_prediction_list:

                label = pred.category.name.lower()

                if label in VEHICLE_CLASSES:

                    box = pred.bbox.to_xywh()

                    current_frame_data.append({

                        "vehicle": label, 

                        "x": round(box[0], 1), 

                        "y": round(box[1], 1)

                    })

                    # Draw boxes

                    cv2.rectangle(annotated_frame, (int(pred.bbox.minx), int(pred.bbox.miny)), 

                                  (int(pred.bbox.maxx), int(pred.bbox.maxy)), (0, 255, 0), 2)

        else:

            # Standard YOLO detection

            results = standard_model.predict(frame, conf=conf_level, imgsz=1280, classes=[2,3,5,7])

            annotated_frame = results[0].plot()

            for box in results[0].boxes:

                x, y, _, _ = box.xywh[0].tolist()

                current_frame_data.append({

                    "vehicle": standard_model.names[int(box.cls[0])], 

                    "x": round(x, 1), 

                    "y": round(y, 1)

                })



        # --- SYNC TO SERVER ---

        # This makes the data available for your friend's GET request

        try:

            requests.get(server_url, params={"data": str(current_frame_data)}, timeout=0.01)

        except:

            pass



        # Update UI

        st_frame.image(annotated_frame, channels="BGR", use_container_width=True)

        if current_frame_data:

            st_table.table(pd.DataFrame(current_frame_data))



    cap.release()





Is there any problem with the bridge?