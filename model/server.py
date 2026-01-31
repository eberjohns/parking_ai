from fastapi import FastAPI
import uvicorn
import ast

app = FastAPI()

# This variable stores the state of the 'current' frame
latest_frame_results = []
from fastapi import FastAPI
import uvicorn
import ast

app = FastAPI()

# Shared variable to hold the latest AI results
latest_ai_data = []

@app.get("/update_data")
def update_data(data: str):
    """Internal: Streamlit calls this to push new coordinates."""
    global latest_ai_data
    try:
        # Convert string back to Python objects safely
        vehicle_list = ast.literal_eval(data)
        
        # Store it globally
        latest_ai_data = vehicle_list
        
        return {"status": "success"}
    except Exception as e:
        # If conversion fails, return the error for debugging
        return {"status": "error", "message": str(e)}

@app.get("/get_coords")
def get_coords():
    """Public: Your friend calls this to get the JSON response."""
    return latest_ai_data

if __name__ == "__main__":
    # Runs on port 8000
    uvicorn.run(app, host="0.0.0.0", port=8000)
@app.get("/update_data")
def update_data(data: str):
    """Internal endpoint: Streamlit calls this to push new coordinates."""
    global latest_frame_results
    try:
        # Convert string back to Python list safely
        vehicle_list = ast.literal_eval(data)
        latest_frame_results = vehicle_list
    
        return {"status": "success"}
    except:
        return {"status": "error"}

@app.get("/get_coords")
def get_coords():
    """Public endpoint: Your friend calls this to get the JSON response."""
    return latest_frame_results

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)