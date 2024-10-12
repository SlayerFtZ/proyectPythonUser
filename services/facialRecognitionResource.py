import cv2
import face_recognition
import os
import tkinter as tk
from tkinter import messagebox

GUIDE_WIDTH = 640
GUIDE_HEIGHT = 480

TOLERANCE = 20

def isPointInEllipse(x, y, center_x, center_y, axis_x, axis_y):
    return ((x - center_x) / axis_x) ** 2 + ((y - center_y) / axis_y) ** 2 <= 1


def captureImage(window_name, image_name, guide_type='credential'):
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        messagebox.showerror("Error", "Could not access the camera.")
        return False

    print(f'Please show your {window_name}. Press "s" to capture the image when you are ready.')

    if guide_type == 'credential':
        top_left = (int(GUIDE_WIDTH * 0.2), int(GUIDE_HEIGHT * 0.2))
        bottom_right = (int(GUIDE_WIDTH * 0.8), int(GUIDE_HEIGHT * 0.7))
        guide_color = (0, 255, 0)  # Green
    elif guide_type == 'face':
        center = (int(GUIDE_WIDTH * 0.5), int(GUIDE_HEIGHT * 0.4))
        axis_x = int(GUIDE_WIDTH * 0.15)  
        axis_y = int(GUIDE_HEIGHT * 0.2)  
        guide_color = (255, 0, 0)  

    aligned = False  

    while True:
        ret, frame = cap.read()
        if not ret:
            print("Error accessing the camera.")
            break

        frame = cv2.resize(frame, (GUIDE_WIDTH, GUIDE_HEIGHT))

        if guide_type == 'credential':
            cv2.rectangle(frame, top_left, bottom_right, (0, 255, 0), 2)
            cv2.putText(frame, "Place your credential here",
                        (top_left[0], top_left[1] - 10),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.6, (0, 255, 0), 2)
        elif guide_type == 'face':
            cv2.ellipse(frame, center, (axis_x, axis_y), 0, 0, 360, guide_color, 2)
            cv2.putText(frame, "Place your face here",
                        (center[0] - axis_x, center[1] - axis_y - 10),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.6, (255, 0, 0), 2)

        if guide_type == 'face':
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            face_locations = face_recognition.face_locations(rgb_frame)

            if face_locations:
                top, right, bottom, left = face_locations[0]
                face_center_x = (left + right) // 2
                face_center_y = (top + bottom) // 2

                cv2.circle(frame, (face_center_x, face_center_y), 5, (0, 255, 255), -1)

                if isPointInEllipse(face_center_x, face_center_y, center[0], center[1], axis_x, axis_y):
                    aligned = True
                    guide_color_current = (0, 255, 0)  
                    cv2.ellipse(frame, center, (axis_x, axis_y), 0, 0, 360, guide_color_current, 2)
                    cv2.putText(frame, "Aligned!", (center[0] - axis_x, center[1] + axis_y + 25),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
                else:
                    aligned = False
                    guide_color_current = (0, 0, 255)  
                    cv2.ellipse(frame, center, (axis_x, axis_y), 0, 0, 360, guide_color_current, 2)
                    cv2.putText(frame, "Adjust your position", (center[0] - axis_x, center[1] + axis_y + 25),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)

                if aligned:
                    cv2.putText(frame, "Correctly aligned.", (10, GUIDE_HEIGHT - 20),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
                else:
                    cv2.putText(frame, "Please align your face within the oval.",
                                (10, GUIDE_HEIGHT - 20),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)
            else:
                cv2.putText(frame, "No face detected", (center[0] - axis_x, center[1] + axis_y + 25),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)

        cv2.imshow(window_name, frame)

        key = cv2.waitKey(1) & 0xFF
        if key == ord('s'):
            if guide_type == 'face' and not aligned:
                messagebox.showwarning("Warning", "Please align your face within the oval before capturing.")
                continue  
            cv2.imwrite(image_name, frame)
            print(f'Image of {window_name} captured and saved as {image_name}.')
            break
        elif key == ord('q'):
            print("Image capture canceled by user.")
            break

    cap.release()
    cv2.destroyAllWindows()

    if not os.path.exists(image_name):
        return False
    return True

def checkFaceInImage(image_path):
    image = face_recognition.load_image_file(image_path)
    face_locations = face_recognition.face_locations(image)

    if len(face_locations) > 0:
        print(f"Face detected in {image_path}")
        return True
    else:
        print(f"No face detected in {image_path}")
        return False


def compareFaces(credential_image_path, user_image_path):
    credential_image = face_recognition.load_image_file(credential_image_path)
    user_image = face_recognition.load_image_file(user_image_path)

    try:
        credential_encoding = face_recognition.face_encodings(credential_image)[0]
        user_encoding = face_recognition.face_encodings(user_image)[0]
    except IndexError:
        print("Error: Could not find a face in one of the images.")
        return False

    results = face_recognition.compareFaces([credential_encoding], user_encoding)
    return results[0]

def showHelp():
    help_message = (
        "Instructions for verification:\n\n"
        "1. When the verification starts, the camera will open with a larger green guide.\n"
        "   Place your voter ID card within the green rectangle.\n"
        "   Ensure that the face on the credential is clearly visible.\n"
        "2. When the image is ready, press 's' to capture it.\n"
        "   If you want to cancel, press 'q'.\n\n"
        "3. Next, the camera will open with a blue oval guide.\n"
        "   Place your face inside the blue oval.\n"
        "   Adjust your position until the oval turns green, indicating that you are correctly aligned.\n"
        "4. Press 's' to capture your face.\n"
        "5. The system will verify if the face on the credential matches your face.\n"
        "6. If they match, you will see the message 'Verification successful'. If not, you will see 'Verification failed'."
    )
    messagebox.showinfo("Help", help_message)

def main():
    root = tk.Tk()
    root.title("Facial Verification")

    root.geometry("500x250")
    root.resizable(False, False)

    label = tk.Label(root, text="Welcome to the facial verification system.\nFollow the instructions to continue.", 
                    font=("Helvetica", 12), justify="center")
    label.pack(pady=20)

    help_button = tk.Button(root, text="Need help?", command=showHelp, width=20)
    help_button.pack(pady=5)

    def startVerification():
        credential_image_path = "temp_credencial.jpg"
        success = captureImage("voter ID card", credential_image_path, guide_type='credential')

        if not success:
            messagebox.showerror("Error", "Could not capture the credential image.")
            return

        if not checkFaceInImage(credential_image_path):
            print("No face detected on the credential. Verification failed.")
            messagebox.showerror("Error", "No face detected on the credential. Verification failed.")
            return

        user_image_path = "temp_usuario.jpg"
        success = captureImage("user's face", user_image_path, guide_type='face')

        if not success:
            messagebox.showerror("Error", "Could not capture the user image.")
            return

        if not checkFaceInImage(user_image_path):
            print("No face detected in the user image. Verification failed.")
            messagebox.showerror("Error", "No face detected in the user image. Verification failed.")
            return

        if compareFaces(credential_image_path, user_image_path):
            print("Verification successful: The face matches the credential.")
            messagebox.showinfo("Verification Result", "Verification successful: The face matches the credential.")
        else:
            print("Verification failed: The face does not match the credential.")
            messagebox.showerror("Verification Result", "Verification failed: The face does not match the credential.")

    verify_button = tk.Button(root, text="Start Verification", command=startVerification, width=20)
    verify_button.pack(pady=10)

    root.mainloop()

if __name__ == "__main__":
    main()
