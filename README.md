# ai-blind-navigation-assistant
AI-powered Blind Navigation Assistant using OpenCV and speech feedback to detect obstacles and assist visually impaired users in real time

This project is an AI-powered Blind Navigation Assistant designed to support visually impaired individuals in safe movement. It uses a webcam-based computer vision system to detect motion and potential obstacles in the user’s path.

The system processes live video using OpenCV, identifies movement regions, estimates direction (left, center, right), and calculates approximate distance. When an obstacle is detected within a critical range, the system provides real-time voice alerts using text-to-speech (pyttsx3).

The application features a modern GUI built with Tkinter, offering controls for starting/stopping the camera and enabling/disabling speech feedback.

Key Features:
Real-time obstacle detection using OpenCV
Direction-based alerts (Left / Right / Center)
Voice feedback using text-to-speech
Live video GUI interface (Tkinter)
FPS and alert tracking system
Lightweight and runs on basic hardware
