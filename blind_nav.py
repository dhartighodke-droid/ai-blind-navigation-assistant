import cv2
import numpy as np
import tkinter as tk
from tkinter import ttk
import pyttsx3
import threading
import time
import queue

class BlindNavigationApp:
    def __init__(self):
        # Initialize TTS
        self.tts = pyttsx3.init()
        self.tts.setProperty('rate', 180)
        self.tts.setProperty('volume', 0.9)
        
        # Motion detection vars
        self.prev_frame = None
        self.last_alert = 0
        self.running = False
        
        # GUI
        self.setup_gui()
        
    def setup_gui(self):
        self.root = tk.Tk()
        self.root.title("🧭 Blind Navigation Assistant")
        self.root.geometry("800x600")
        self.root.configure(bg='black')
        
        # Video panel
        self.video_label = tk.Label(self.root, bg='black')
        self.video_label.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Status
        self.status_label = tk.Label(self.root, text="🔄 Initializing...", 
                                   font=('Arial', 24, 'bold'), bg='black', fg='#00ff88')
        self.status_label.pack(pady=10)
        
        # Controls
        control_frame = tk.Frame(self.root, bg='black')
        control_frame.pack(pady=10)
        
        self.start_btn = tk.Button(control_frame, text="▶️ START CAMERA", 
                                  command=self.start_camera, font=('Arial', 16),
                                  bg='#00ff88', fg='black', padx=20, pady=10)
        self.start_btn.pack(side=tk.LEFT, padx=10)
        
        self.stop_btn = tk.Button(control_frame, text="⏹️ STOP", 
                                 command=self.stop_camera, font=('Arial', 16),
                                 bg='#ff4444', fg='white', padx=20, pady=10)
        self.stop_btn.pack(side=tk.LEFT, padx=10)
        
        self.speech_btn = tk.Button(control_frame, text="🔊 SPEECH ON", 
                                   command=self.toggle_speech, font=('Arial', 14),
                                   bg='#007AFF', fg='white', padx=20, pady=5)
        self.speech_btn.pack(side=tk.LEFT, padx=10)
        
        # FPS/Stats
        self.stats_label = tk.Label(self.root, text="FPS: 0 | Alerts: 0", 
                                   font=('Arial', 12), bg='black', fg='white')
        self.stats_label.pack()
        
        self.frame_queue = queue.Queue(maxsize=1)
        self.alert_count = 0
        
    def speak(self, text):
        def _speak():
            self.tts.say(text)
            self.tts.runAndWait()
        threading.Thread(target=_speak, daemon=True).start()
    
    def detect_motion(self, frame):
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        gray = cv2.GaussianBlur(gray, (21, 21), 0)
        
        if self.prev_frame is None:
            self.prev_frame = gray
            return False, "Starting..."
        
        frame_delta = cv2.absdiff(self.prev_frame, gray)
        thresh = cv2.threshold(frame_delta, 25, 255, cv2.THRESH_BINARY)[1]
        thresh = cv2.dilate(thresh, None, iterations=2)
        
        contours, _ = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        motion_detected = False
        h, w = frame.shape[:2]
        
        for contour in contours:
            if cv2.contourArea(contour) < 2000:
                continue
                
            (x, y, cw, ch) = cv2.boundingRect(contour)
            distance = max(0.5, 3.5 * (h / ch))
            
            # Direction
            center_x = x + cw/2
            if center_x < w*0.35:
                direction = "LEFT"
            elif center_x > w*0.65:
                direction = "RIGHT"
            else:
                direction = "CENTER"
            
            if distance < 3.0:
                motion_detected = True
                return True, f"🚨 {direction} {distance:.1f}m"
        
        return False, "✅ PATH CLEAR"
    
    def video_thread(self):
        cap = cv2.VideoCapture(0)
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        
        fps_counter = 0
        start_time = time.time()
        
        while self.running:
            ret, frame = cap.read()
            if not ret:
                continue
                
            frame = cv2.flip(frame, 1)
            alert, message = self.detect_motion(frame)
            
            # Draw
            h, w = frame.shape[:2]
            cv2.putText(frame, message, (20, 50), cv2.FONT_HERSHEY_SIMPLEX, 
                       1.2, (0, 255, 0) if not alert else (0, 0, 255), 3)
            
            if alert:
                self.alert_count += 1
                now = time.time()
                if now - self.last_alert > 1.2:
                    self.last_alert = now
                    if self.speech_on:
                        self.speak(message)
            
            # FPS
            fps_counter += 1
            if time.time() - start_time > 1:
                fps = fps_counter
                fps_counter = 0
                start_time = time.time()
                
                self.stats_label.config(text=f"FPS: {fps} | Alerts: {self.alert_count}")
            
            # Resize for GUI
            frame = cv2.resize(frame, (640, 480))
            
            try:
                self.frame_queue.put_nowait(frame)
            except:
                pass
        
        cap.release()
    
    def update_gui(self):
        try:
            frame = self.frame_queue.get_nowait()
            img = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            img = cv2.resize(img, (640, 480))
            
            # Update label
            self.photo = tk.PhotoImage(data=cv2.imencode('.png', img)[1].tobytes())
            self.video_label.config(image=self.photo)
            
        except:
            pass
        
        if self.running:
            self.root.after(30, self.update_gui)
    
    def start_camera(self):
        if not self.running:
            self.running = True
            self.start_btn.config(state='disabled')
            self.stop_btn.config(state='normal')
            threading.Thread(target=self.video_thread, daemon=True).start()
            self.update_gui()
    
    def stop_camera(self):
        self.running = False
        self.start_btn.config(state='normal')
        self.stop_btn.config(state='disabled')
    
    def toggle_speech(self):
        self.speech_on = not getattr(self, 'speech_on', True)
        self.speech_btn.config(text="🔇 SPEECH OFF" if not self.speech_on else "🔊 SPEECH ON")
    
    def run(self):
        self.speech_on = True
        self.root.mainloop()

# 🔥 RUN THIS!
if __name__ == "__main__":
    print("🚀 Blind Navigation Assistant Starting...")
    print("🎮 Desktop Python App - Full GUI + Speech + Camera")
    app = BlindNavigationApp()
    app.run()