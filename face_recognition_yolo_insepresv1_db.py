import cv2
import numpy as np
import os
import pickle
from facenet_pytorch import InceptionResnetV1
import torch
from PIL import Image
from scipy.spatial.distance import cosine
from datetime import datetime
import jdatetime
from sqlit_setup import save_record_to_db, load_recognized_today


recognition_running = False

# Load facenet-pytorch InceptionResnetV1 model
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
print(device)
inception_resnet = InceptionResnetV1(pretrained='vggface2').eval().to(device)

# Load YOLO model
yolo_config = 'yolov3-face.cfg'  
yolo_weights = 'yolov3-wider_16000.weights'  
net = cv2.dnn.readNet(yolo_weights, yolo_config)
layer_names = net.getLayerNames()

# Handle different formats of getUnconnectedOutLayers
try:
    output_layers = [layer_names[i[0] - 1] for i in net.getUnconnectedOutLayers()]
except IndexError:
    output_layers = [layer_names[i - 1] for i in net.getUnconnectedOutLayers()]

def detect_faces(image):
    height, width = image.shape[:2]
    blob = cv2.dnn.blobFromImage(image, 1 / 255.0, (416, 416), swapRB=True, crop=False)
    net.setInput(blob)
    detections = net.forward(output_layers)

    boxes = []
    confidences = []
    faces = []

    for detection in detections:
        for obj in detection:
            scores = obj[5:]
            confidence = scores[np.argmax(scores)]
            if confidence > 0.5:
                center_x = int(obj[0] * width)
                center_y = int(obj[1] * height)
                w = int(obj[2] * width)
                h = int(obj[3] * height)
                x = int(center_x - w / 2)
                y = int(center_y - h / 2)

                boxes.append([x, y, w, h])
                confidences.append(float(confidence))

    indices = cv2.dnn.NMSBoxes(boxes, confidences, score_threshold=0.5, nms_threshold=0.4)

    for i in indices:
        box = boxes[i]
        x, y, w, h = box
        face = image[y:y+h, x:x+w]
        if face.size != 0:
            faces.append(face)

    return faces, [boxes[i] for i in indices], [confidences[i] for i in indices]

def get_face_embedding_inceptionresnet(face):
    if face.size == 0:
        # print("Empty face image passed to get_face_embedding_inceptionresnet.")
        return None
    face_rgb = cv2.cvtColor(face, cv2.COLOR_BGR2RGB)
    img = Image.fromarray(face_rgb)
    img = img.resize((160, 160))
    img_tensor = torch.tensor(np.array(img)).permute(2, 0, 1).float().to(device)
    img_tensor = (img_tensor / 255.0).unsqueeze(0)
    with torch.no_grad():
        embedding = inception_resnet(img_tensor).cpu().numpy().flatten()
    return embedding.tolist()

def load_faces_data(pkl_file):
    with open(pkl_file, 'rb') as f:
        return pickle.load(f)

def recognize_face(face_embedding, faces_data, threshold=0.4):
    if face_embedding is None:
        return None, float('inf')

    min_distance = float('inf')
    recognized_member = None
    
    for member_name, member_embedding in faces_data:
        distance = cosine(face_embedding, member_embedding)
        if distance < min_distance:
            min_distance = distance
            recognized_member = member_name
            
    if min_distance < threshold:
        return recognized_member, min_distance
    else:
        return None, min_distance

def convert_date_time():
    now = datetime.now()
    current_date = now.strftime("%Y-%m-%d")
    current_time = now.strftime("%H:%M:%S")
    jalali_date = jdatetime.datetime.now().strftime("%Y-%m-%d")
    
    return (jalali_date, current_date, current_time)

def save_recognize_face_frame(membername, currentdate, t, frame):
    if not os.path.exists('recognized_faces_frame'):
        os.makedirs('recognized_faces_frame')
                    
    photo_filename = f"{membername}_{currentdate}_{t}.png"
    photo_path = os.path.join('recognized_faces_frame', photo_filename)
                    
            
    result = cv2.imwrite(photo_path, frame)
    print(f"Save result: {result}")

def save_recognize_face(member_name, current_date, current_time_string, face):
    if not os.path.exists('recognized_faces'):
        os.makedirs('recognized_faces')
                        
    photo_filename = f"{member_name}_{current_date}_{current_time_string}.png"
    photo_path = os.path.join('recognized_faces', photo_filename)
                        
    result = cv2.imwrite(photo_path, face)
    print(f"Save result: {result}")
    return photo_path

def stop_recognition():
    global recognition_running
    recognition_running = False

def start_recognition(camera_index, toggle_flag, save_pic_flag, ui_th=0.3, update_treeview_callback=None, progress_bar=None):
    global recognition_running
    
    recognition_running = True
    first_frame_displayed = False
    pkl_file = 'faces_data_Inception-ResNet.pkl'
    faces_data = load_faces_data(pkl_file)

    cap = cv2.VideoCapture(camera_index)  # Capture from the default webcam
    recognized_today = load_recognized_today()
    # print(recognized_today)
    while recognition_running:
        ret, frame = cap.read()
        if not ret:
            break

        faces, boxes, confidences = detect_faces(frame)
        # Color of the rectangle
        rectangle_color = (0,255, 0)
        
        for i, face in enumerate(faces):
            face_embedding = get_face_embedding_inceptionresnet(face)
            
            member_name, m_dist = recognize_face(face_embedding, faces_data, threshold=ui_th)
            
            if member_name is not None:
                label = f'{member_name}'
                
                # Check if member has been recognized today
                today_date = datetime.now().strftime("%Y-%m-%d")
                if (member_name, today_date) not in recognized_today:
                    recognized_today.add((member_name, today_date))
                    jalali_date, current_date, current_time = convert_date_time()
                    
                    photo_path = "photo do not saved."
                    
                    # save two photo, 1- a whole frame and the face.
                    if save_pic_flag:
                        current_time_string = current_time.split(':')[-1]
                        save_recognize_face_frame(membername=member_name, currentdate=current_date, t=current_time_string, frame=frame)
                        # Save photo
                        photo_path = save_recognize_face(member_name, current_date, current_time_string, face)
                        
                        
                    # Save record to database
                    save_record_to_db(member_name, current_date, current_time, jalali_date, photo_path)
                    
                    # Update UI three view bottom
                    if update_treeview_callback:
                        update_treeview_callback()
                    
                    # print(f"Recognized {member_name} at {current_time} on {jalali_date}")
                
            else:
                label = 'Unknown'
                rectangle_color = (255, 0, 0)

            x, y, w, h = boxes[i]
            cv2.rectangle(frame, (x, y), (x + w, y + h), rectangle_color, 2)
            cv2.putText(frame, f'{label} {m_dist:.2f}', (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)

        cv2.imshow('Face Recognition', frame)
        
        # Hide the progress bar after displaying the first frame
        if not first_frame_displayed and progress_bar is not None:
            progress_bar.stop()
            progress_bar.grid_remove()
            first_frame_displayed = True

        if cv2.waitKey(1) & 0xFF == ord('q') or toggle_flag == 0:
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == '__main__':
    print("This file use Yolo and InseptionResNet to detect and recognize faces real-time")
