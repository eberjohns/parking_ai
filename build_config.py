import cv2
import json
import os

# --- CONFIGURATION ---
IMAGE_PATH = 'st_thomas_top_down.png'
OUTPUT_JSON = 'config.json'
LOT_ID = "st_thomas_main"
LOT_NAME = "St. Thomas College Main Ground"
# ---------------------

drawing = False
ix, iy = -1, -1
current_rect = None
slots_data = []

def draw_rect(event, x, y, flags, param):
    global ix, iy, drawing, current_rect

    if event == cv2.EVENT_LBUTTONDOWN:
        drawing = True
        ix, iy = x, y

    elif event == cv2.EVENT_MOUSEMOVE:
        if drawing:
            img_copy = param['img'].copy()
            cv2.rectangle(img_copy, (ix, iy), (x, y), (0, 255, 0), 2)
            cv2.imshow("Slot Builder", img_copy)

    elif event == cv2.EVENT_LBUTTONUP:
        drawing = False
        # Calculate width and height
        w = abs(x - ix)
        h = abs(y - iy)
        # Top-left corner adjustment (in case you dragged backwards)
        rx = min(ix, x)
        ry = min(iy, y)
        
        # Save this slot
        current_rect = (rx, ry, w, h)
        
        # Add to our list
        slot_id = len(slots_data)
        slots_data.append({
            "id": slot_id,
            "label": f"Slot_{slot_id}", # Default name
            "type": "car",              # Default type (you can edit later)
            "coordinates": {
                "x": rx, "y": ry, "w": w, "h": h
            }
        })
        
        # Draw permanently on the image
        cv2.rectangle(param['img'], (rx, ry), (rx+w, ry+h), (0, 255, 0), 2)
        cv2.putText(param['img'], str(slot_id), (rx, ry-5), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)
        cv2.imshow("Slot Builder", param['img'])
        print(f"Added Slot {slot_id}: x={rx}, y={ry}, w={w}, h={h}")

def main():
    if not os.path.exists(IMAGE_PATH):
        print(f"Error: Could not find {IMAGE_PATH}")
        return

    img = cv2.imread(IMAGE_PATH)
    height, width, _ = img.shape

    cv2.namedWindow("Slot Builder")
    cv2.setMouseCallback("Slot Builder", draw_rect, {'img': img})

    print("--- PARKING SLOT BUILDER ---")
    print("1. Click and drag to draw a box around a parking slot.")
    print("2. Release mouse to save the slot.")
    print("3. Repeat for all slots.")
    print("4. Press 's' to SAVE the JSON file.")
    print("5. Press 'q' to Quit without saving.")
    print("----------------------------")

    while True:
        cv2.imshow("Slot Builder", img)
        k = cv2.waitKey(1) & 0xFF

        if k == ord('s'):
            # Construct the final JSON structure
            final_json = {
                "lot_id": LOT_ID,
                "lot_name": LOT_NAME,
                "map_image_url": f"assets/{IMAGE_PATH}",
                "image_dimensions": {
                    "width": width,
                    "height": height
                },
                "slots": slots_data
            }

            # Save to file
            with open(OUTPUT_JSON, 'w') as f:
                json.dump(final_json, f, indent=4)
            print(f"\nSUCCESS! Saved {len(slots_data)} slots to '{OUTPUT_JSON}'")
            break

        elif k == ord('q'):
            print("Quitting without saving.")
            break
        
        elif k == ord('z'):
            # Simple Undo (optional: restart if you make a mistake)
            print("Undo not implemented in simple version. Restart if messy!")

    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()