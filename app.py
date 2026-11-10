import cv2
import mediapipe as mp
from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume

devices = AudioUtilities.GetSpeakers()
interface = devices.Activate(
    IAudioEndpointVolume._iid_,
    CLSCTX_ALL,
    None
)

volume = cast(interface, POINTER(IAudioEndpointVolume))

min_volume, max_volume, _ = volume.GetVolumeRange()

mp_hands = mp.solutions.hands
mp_draw = mp.solutions.drawing_utils

hands = mp_hands.Hands(
    max_num_hands=1,
    min_detection_confidence=0.7,
    min_tracking_confidence=0.7
)


cap = cv2.VideoCapture(0)

last_number = 0

while True:

    success, frame = cap.read()

    if not success:
        break


    frame = cv2.flip(frame, 1)

  
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    
    result = hands.process(rgb)

    finger_count = 0

    if result.multi_hand_landmarks:

        for hand_landmarks in result.multi_hand_landmarks:

            landmark = hand_landmarks.landmark

            mp_draw.draw_landmarks(
                frame,
                hand_landmarks,
                mp_hands.HAND_CONNECTIONS
            )

            # انگشت اشاره
            if landmark[8].y < landmark[6].y:
                finger_count += 1

            # انگشت وسط
            if landmark[12].y < landmark[10].y:
                finger_count += 1

            # انگشت حلقه
            if landmark[16].y < landmark[14].y:
                finger_count += 1

            # انگشت کوچک
            if landmark[20].y < landmark[18].y:
                finger_count += 1

            # انگشت شست
            if landmark[4].x > landmark[3].x:
                finger_count += 1

            # -------------کنترل صدا----------------

            if finger_count == 3:

                current_volume = volume.GetMasterVolumeLevelScalar()

                new_volume = min(
                    current_volume + 0.05,
                    1.0
                )

                volume.SetMasterVolumeLevelScalar(
                    new_volume,
                    None
                )

            elif finger_count == 1:

                # کاهش صدا
                current_volume = volume.GetMasterVolumeLevelScalar()

                new_volume = max(
                    current_volume - 0.05,
                    0.0
                )

                volume.SetMasterVolumeLevelScalar(
                    new_volume,
                    None
                )

    # ------------نمایش تعداد انگشت‌ها-----------------

    cv2.putText(
        frame,
        str(finger_count),
        (50, 100),
        cv2.FONT_HERSHEY_SIMPLEX,
        3,
        (0, 255, 0),
        5
    )

    cv2.putText(
        frame,
        "3 = Volume UP",
        (50, 180),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.8,
        (255, 255, 255),
        2
    )

    cv2.putText(
        frame,
        "1 = Volume DOWN",
        (50, 220),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.8,
        (255, 255, 255),
        2
    )

    cv2.putText(
        frame,
        "Press Q to Exit",
        (50, 260),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.8,
        (255, 255, 255),
        2
    )

    cv2.imshow("MediaPipe Volume Control", frame)

    if cv2.waitKey(1) & 0xFF == ord("q"):
        break


cap.release()
cv2.destroyAllWindows()

