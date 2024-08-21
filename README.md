![Build Status](https://img.shields.io/badge/build-passing-brightgreen)
![License](https://img.shields.io/badge/license-MIT-blue)
![Python Version](https://img.shields.io/badge/python-3.8%2B-blue)

# Gym Entry Management System

This is a Gym Entry Management System that uses facial recognition to manage member entries, store member data, and provide various features such as adding new members, exporting data, and editing member information. The application is built using Python with the `Tkinter` library for the GUI, and it integrates various other libraries for image processing, database management, and more.

## Features

- **Facial Recognition**: Real-time face recognition to manage gym entries.
- **Webcam Selection**: Choose from available webcams to start recognition.
- **Adjustable Accuracy**: Set the accuracy level for face recognition.
- **Member Management**: Add, edit, and view gym members.
- **Data Export**: Export daily or all-time records to Excel files.
- **Multi-language Support**: Manage member names in both English and Farsi.
- **Progress Indicators**: Visual feedback during long operations like recognition and data export.

## Installation

### Prerequisites

- Python 3.x
- [ttkbootstrap](https://pypi.org/project/ttkbootstrap/)
- OpenCV
- Pillow
- Tourch
- jdatetime
- facenet_pytorch
- yolov3-wider_16000.weights
- yolov3-face.cfg
- Pandas
- `win32com.client` (for webcam detection on Windows)
- SQLite (database setup included)

### Setting Up the Environment

1. Clone the repository:

    ```sh
    git clone https://github.com/yourusername/gym-entry-system.git
    cd gym-entry-system
    ```

2. Install the required Python packages:

    ```sh
    pip install -r requirements.txt
    ```

3. Run the application:

    ```sh
    python main.py
    ```

## Usage

1. **Start the Application**: The main window will open with three sections: the left frame for controls, the right frame for member management, and the bottom frame for viewing entry logs.

2. **Choose Webcam**: Select the desired webcam from the dropdown menu in the left frame.

3. **Set Recognition Accuracy**: Adjust the accuracy slider to set the desired level for facial recognition.

4. **Start/Stop Recognition**: Toggle the recognition process using the provided checkbox.

5. **Save Member Pictures**: Enable or disable saving pictures of members during recognition. (It can help to adjust accuracy level)

6. **Add New Members**: First you need to create a folder with the user image and user name in the `club_members` folder. Forexample `club_members -> pouria_parhami'. Then Use the right frame to input new member details in both English and Farsi, then click 'Add Member'. (The english name must be the same as user folder.)

7. **Edit Members**: Select a member from the list and update their details.

8. **Export Data**: Export today's or all-time records to an Excel file.

## File Structure

- **ui_display.py**: The main application file containing all UI components and logic.
- **face_recognition_yolo_insepresv1_db.py**: Module for face recognition logic.
- **face_detection_yolo_inceptionRes.py**: Module for detecting faces using YOLO and InceptionResNet.
- **sqlit_setup.py**: Handles SQLite database setup and operations.
- **requirements.txt**: Lists all the required Python packages.

## Contributing

Contributions are welcome! Please fork the repository and create a pull request with your changes.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
