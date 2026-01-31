import cv2
import numpy as np

# --- CONFIGURATION ---
SOURCE_IMAGE_PATH = 'camera_view.png'
OUTPUT_IMAGE_PATH = 'true_top_down.png'
# ---------------------

src_points = []

def select_points(event, x, y, flags, param):
    if event == cv2.EVENT_LBUTTONDOWN:
        src_points.append((x, y))
        cv2.circle(param['img'], (x, y), 5, (0, 255, 0), -1)
        cv2.putText(param['img'], str(len(src_points)), (x + 10, y), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
        cv2.imshow("Select 4 Corners", param['img'])

def main():
    img = cv2.imread(SOURCE_IMAGE_PATH)
    if img is None: return
    h, w = img.shape[:2]
    clone = img.copy()

    cv2.namedWindow("Select 4 Corners")
    cv2.setMouseCallback("Select 4 Corners", select_points, {'img': clone})

    print("Click 4 corners of a real-world rectangle (e.g., a parking spot).")
    while len(src_points) < 4:
        cv2.imshow("Select 4 Corners", clone)
        cv2.waitKey(1)

    # 1. Source Points
    pts_src = np.float32(src_points)

    # 2. Calculate the "Natural" dimensions of the selection
    # We find the width and height of the box to maintain aspect ratio
    (tl, tr, br, bl) = pts_src
    width_a = np.sqrt(((br[0] - bl[0]) ** 2) + ((br[1] - bl[1]) ** 2))
    width_b = np.sqrt(((tr[0] - tl[0]) ** 2) + ((tr[1] - tl[1]) ** 2))
    max_w = max(int(width_a), int(width_b))

    height_a = np.sqrt(((tr[0] - br[0]) ** 2) + ((tr[1] - br[1]) ** 2))
    height_b = np.sqrt(((tl[0] - bl[0]) ** 2) + ((tl[1] - bl[1]) ** 2))
    max_h = max(int(height_a), int(height_b))

    # 3. Destination Points
    # We place the result in the center of the original resolution 
    # to avoid the image flying off-screen.
    offset_x = (w - max_w) // 2
    offset_y = (h - max_h) // 2
    
    pts_dst = np.float32([
        [offset_x, offset_y],
        [offset_x + max_w, offset_y],
        [offset_x + max_w, offset_y + max_h],
        [offset_x, offset_y + max_h]
    ])

    # 4. Generate Matrix and Warp
    matrix = cv2.getPerspectiveTransform(pts_src, pts_dst)
    
    # We keep the output resolution exactly the same as the input (w, h)
    result = cv2.warpPerspective(img, matrix, (w, h), flags=cv2.INTER_LINEAR)

    # 5. Save and Show
    cv2.imwrite(OUTPUT_IMAGE_PATH, result)
    print(f"Transformed image saved to {OUTPUT_IMAGE_PATH}")
    cv2.imshow("Top-Down (Original Resolution)", result)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()