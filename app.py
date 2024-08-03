import os
from pathlib import Path
import cv2
from ultralytics import YOLO
import tkinter as tk
from tkinter import filedialog, messagebox

# Initialize YOLOv8 object detector
model_path = 'best.pt'
model = YOLO(model_path)

# Define directories
test_dir = 'test'
result_dir = 'result'
video_dir = 'saved_videos'
os.makedirs(result_dir, exist_ok=True)
os.makedirs(video_dir, exist_ok=True)

def live_detection():
    cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)  # Try different backends if necessary

    if not cap.isOpened():
        print("Cannot open webcam")
        return

    # Define the codec and create VideoWriter object
    # fourcc = cv2.VideoWriter_fourcc(*'XVID')
    # out = cv2.VideoWriter(os.path.join(video_dir, 'output.avi'), fourcc, 20.0, (640, 480))
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(os.path.join(video_dir, 'output.mp4'), fourcc, 8.0, (640, 480))


    # Create a named window with a specific size
    window_name = 'YOLOv8 Live Webcam'
    cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)  # Allow resizing
    cv2.resizeWindow(window_name, 640, 480)  # Set the window size

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            print("Can't receive frame (stream end?). Exiting ...")
            break

        # Perform inference
        results = model(frame, iou=0.5, conf=0.7)

        # Process each result and display the image with bounding boxes
        for result in results:
            result_img = result.plot()  # Plot the results on the image

            # Write the frame to the video file
            out.write(result_img)

            # Display the resulting frame
            cv2.imshow(window_name, result_img)

            # Optionally, you can print results for each frame
            print(f"Results for frame:")
            if result.boxes:
                for box in result.boxes:
                    cls_id = int(box.cls)  # Convert tensor to integer
                    conf = float(box.conf)  # Convert tensor to float
                    xyxy = box.xyxy.tolist()  # Convert tensor to list
                    print(f"Class: {result.names[cls_id]}, Confidence: {conf:.2f}, Box: {xyxy}")

        if cv2.waitKey(1) & 0xFF == ord('q'):  # Press 'q' to quit
            break

    cap.release()
    out.release()
    cv2.destroyAllWindows()    

def detection_for_multiple_image():
    test_dir = filedialog.askdirectory(title="Select Directory")
    if test_dir:
        # Get list of images
        image_paths = list(Path(test_dir).glob('*.*'))
        # Process images from the test directory
        for image_path in image_paths:
            # Load image
            img = cv2.imread(str(image_path))
            
            # Perform inference
            results = model(img)

            # Process each result and save the image with bounding boxes
            for result in results:
                result_img = result.plot()  # Plot the results on the image

                # Save the image with detections
                result_path = os.path.join(result_dir, Path(image_path).name)
                cv2.imwrite(result_path, result_img)
                
                # Optionally, you can print results for each image
                print(f"Results for {Path(image_path).name}:")
                if result.boxes:
                    for box in result.boxes:
                        cls_id = int(box.cls)  # Convert tensor to integer
                        conf = float(box.conf)  # Convert tensor to float
                        xyxy = box.xyxy.tolist()  # Convert tensor to list
                        print(f"Class: {result.names[cls_id]}, Confidence: {conf:.2f}, Box: {xyxy}")

        messagebox.showinfo("Info", f"Results saved to {result_dir}")

def detection_single_image():
    image_path = filedialog.askopenfilename(title="Select Image", filetypes=[("Image files", "*.jpg *.jpeg *.png")])
    if image_path:
        # Load image
        img = cv2.imread(str(image_path))
        
        # Perform inference
        results = model(img)

        # Process each result and save the image with bounding boxes
        for result in results:
            result_img = result.plot()  # Plot the results on the image

            # Save the image with detections
            result_path = os.path.join(result_dir, Path(image_path).name)
            cv2.imwrite(result_path, result_img)
        
            # Optionally, you can print results for each image
            print(f"Results for {Path(image_path).name}:")
            if result.boxes:
                for box in result.boxes:
                    cls_id = int(box.cls)  # Convert tensor to integer
                    conf = float(box.conf)  # Convert tensor to float
                    xyxy = box.xyxy.tolist()  # Convert tensor to list
                    print(f"Class: {result.names[cls_id]}, Confidence: {conf:.2f}, Box: {xyxy}")

        # Display the result image
        cv2.imshow("YOLOv8 Detection Result", result_img)
        cv2.waitKey(0)
        cv2.destroyAllWindows()

# Create the main application window
root = tk.Tk()
root.title("YOLOv8 Object Detection")

# Change the background color
root.configure(bg='#ADD8E6')

# Create and place the heading
heading = tk.Label(root, text="Bottle & Bottle Cap Detection System", font=("Helvetica", 18, "bold"), bg='#ADD8E6')
heading.pack(pady=10)

# Create and place the buttons
button_process_directory = tk.Button(root, text="Detection for Multiple Images", command=detection_for_multiple_image, bg='white')
button_process_directory.pack(pady=10)

button_process_webcam = tk.Button(root, text="Live Detection", command=live_detection, bg='white')
button_process_webcam.pack(pady=10)

button_select_image = tk.Button(root, text="Detection Single Image", command=detection_single_image, bg='white')
button_select_image.pack(pady=10)

# Run the application
root.mainloop()
