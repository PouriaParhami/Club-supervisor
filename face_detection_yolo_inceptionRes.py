import cv2
import numpy as np
import os
import pickle
import matplotlib.pyplot as plt
from facenet_pytorch import InceptionResnetV1
import torch
from PIL import Image

# Load YOLO model
yolo_config = 'yolov3-face.cfg'  # Update with your config file
yolo_weights = 'yolov3-wider_16000.weights'  # Update with your weights file
net = cv2.dnn.readNet(yolo_weights, yolo_config)
layer_names = net.getLayerNames()

# Handle different formats of getUnconnectedOutLayers
try:
    output_layers = [layer_names[i[0] - 1] for i in net.getUnconnectedOutLayers()]
except IndexError:
    output_layers = [layer_names[i - 1] for i in net.getUnconnectedOutLayers()]

# Load facenet-pytorch InceptionResnetV1 model
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
inception_resnet = InceptionResnetV1(pretrained='vggface2').eval().to(device)

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
        faces.append(image[y:y+h, x:x+w])

    return faces, [boxes[i] for i in indices], [confidences[i] for i in indices]

def get_face_embedding_inceptionresnet(face):
    face_rgb = cv2.cvtColor(face, cv2.COLOR_BGR2RGB)
    img = Image.fromarray(face_rgb)
    img = img.resize((160, 160))
    img_tensor = torch.tensor(np.array(img)).permute(2, 0, 1).float().to(device)
    img_tensor = (img_tensor / 255.0).unsqueeze(0)
    with torch.no_grad():
        embedding = inception_resnet(img_tensor).cpu().numpy().flatten()
    return embedding.tolist()

def save_detected_face(faces_dict):
    if not os.path.exists('faces'):
        os.makedirs('faces')
    
    for key, faces in faces_dict.items():
        for i, face in enumerate(faces):
          
            face_file = f'faces/{key}_{i}.png'
            cv2.imwrite(face_file, np.array(faces[i][0]))

def save_faces(faces, member_name):
    face_data = []
    for face in faces:
        embedding = get_face_embedding_inceptionresnet(face)
        face_data.append((member_name, embedding))
    return face_data

def display_image(image, boxes):
    for (x, y, w, h) in boxes:
        cv2.rectangle(image, (x, y), (x + w, y + h), (0, 255, 0), 2)
    
    rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    plt.imshow(rgb_image)
    plt.axis('off')
    plt.show()

def main():
    club_members_folder = r'club_members'

    all_faces_data = []
    all_faces_detected = {}
    
    for member_name in os.listdir(club_members_folder):
        # print(member_name)
        member_folder = os.path.join(club_members_folder, member_name)
        if not os.path.isdir(member_folder):
            continue
        
        faces_detected = []
        for image_name in os.listdir(member_folder):
            # print(image_name)
            image_path = os.path.join(member_folder, image_name)
            if not os.path.isfile(image_path):
                continue

            image = cv2.imread(image_path)
            if image is None:
                print(f'Error loading image: {image_path}')
                continue

            faces, boxes, confidences = detect_faces(image)

            if not faces:
                print(f'No face detected in {image_path}')
                continue
            
            faces_detected.append(faces)
            face_data = save_faces(faces, member_name)
            all_faces_data.extend(face_data)

            # display_image(image, boxes)
            
        all_faces_detected[member_name] = faces_detected
        save_detected_face(all_faces_detected)
        
    pkl_file = 'faces_data_Inception-ResNet.pkl'
    with open(pkl_file, 'wb') as f:
        pickle.dump(all_faces_data, f)
    
    return True

# if __name__ == '__main__':
#     main()
