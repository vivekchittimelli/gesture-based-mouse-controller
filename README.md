\# Gesture Based Mouse Controller



A Python-based gesture-controlled mouse system that allows users to control the computer cursor and perform mouse clicks using hand movements detected through a webcam.



\## Features



\- Control the mouse cursor using index finger movement

\- Perform left click by holding the index finger nearly still

\- Perform right click by bringing the index and middle fingers close together

\- Cursor movement smoothing for better control

\- Dead-zone filtering to reduce unwanted small movements

\- Gesture hold-time detection

\- Click cooldowns to reduce accidental repeated clicks

\- Real-time hand landmark visualization

\- Webcam-based interaction



\## Technologies Used



\- Python

\- OpenCV

\- MediaPipe

\- PyAutoGUI



\## How It Works



The application captures live video from the computer's webcam using OpenCV.



MediaPipe detects the user's hand and identifies hand landmarks, including the index finger and middle finger.



The application then uses these landmarks to determine the user's actions:



\### Mouse Movement



The position of the index finger is tracked continuously. Its movement is converted into corresponding mouse cursor movement using PyAutoGUI.



A smoothing buffer is used to reduce sudden cursor movements.



\### Left Click



When the index finger remains nearly stationary for a specific amount of time, the application performs a left mouse click.



\### Right Click



When the index finger and middle finger are brought close together and held for a short period, the application performs a right mouse click.



\### Exit



Press the `ESC` key to close the application.



\## Project Structure



```text

gesture-based-mouse-controller/

│

├── gesture\_mouse.py

├── requirements.txt

├── README.md

└── images/

