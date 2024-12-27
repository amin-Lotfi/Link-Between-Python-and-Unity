import mediapipe as mpe
import cv2
import threading
import time
import struct

TERMINATE_THREADS = False  # شرط توقف نخ‌ها
DEBUGIN = True  # حالت اشکال‌زدایی
EMPLOY_CUSTOMIZED_CAMERA_OPTIONS = False  # استفاده از تنظیمات دوربین سفارشی
FRAMES_PER_SECOND = 60  # تعداد فریم در ثانیه
WIDTH_ONE = 320  # عرض فریم
HEIGHT_TOW = 240  # ارتفاع فریم
LEVEL_OF_MODEL_COMPLEXITY = 1  # سطح پیچیدگی مدل

class Crisp_image_capture(threading.Thread):
    Lid = None  # شیء ویدئو
    ret = None  # برچسب موجود برای آیا فریم دریافت شده است یا نه
    frame_video = None  # فریم ویدئو
    jogging = False  # شرط اجرای حلقه ویدئو
    numberer = 0  # شمارنده
    Time_control = 0.0  # کنترل زمان

    def run(self):
        self.Lid = cv2.VideoCapture(0)  # شروع ویدئو

        if EMPLOY_CUSTOMIZED_CAMERA_OPTIONS:
            self.Lid.set(cv2.CAP_PROP_FPS, FRAMES_PER_SECOND)  # تنظیم تعداد فریم در ثانیه
            self.Lid.set(cv2.CAP_PROP_FRAME_WIDTH, WIDTH_ONE)  # تنظیم عرض فریم
            self.Lid.set(cv2.CAP_PROP_FRAME_HEIGHT, HEIGHT_TOW)  # تنظیم ارتفاع فریم
        else:
            time.sleep(1)  # تأخیر برای آماده سازی دوربین

        while not TERMINATE_THREADS:
            self.ret, self.frame_video = self.Lid.read()  # دریافت فریم از دوربین
            self.jogging = True  # شروع اجرای حلقه ویدئو

            if DEBUGIN:
                self.numberer = self.numberer + 1  # افزایش شمارنده

                if time.time() - self.Time_control >= 3:  # بررسی زمان
                    self.numberer = 0  # مقداردهی مجدد شمارنده
                    self.Time_control = time.time()  # به‌روزرسانی زمان

class Detection_of_body_movements(threading.Thread):
    data_nl = ""  # داده‌ها
    line = None  # لوله ارتباطی
    since_last_connection_check = 0  # زمانی که آخرین بار بررسی اتصال صورت گرفته است
    Details_of_the_time_elapsed_since_publication = 0  # جزئیات زمان گذشته از انتشار

    def run(self):
        mechanical_drawing = mpe.solutions.drawing_utils
        Parliamentary_Pose = mpe.solutions.pose
        acquire_fresh = Crisp_image_capture()
        acquire_fresh.start()

        with Parliamentary_Pose.Pose(min_detection_confidence=0.80, min_tracking_confidence=0.5,
                                     model_complexity=LEVEL_OF_MODEL_COMPLEXITY, static_image_mode=False,
                                     enable_segmentation=True) as pose_new:

            while not TERMINATE_THREADS and acquire_fresh.jogging == False:
                print("منتظر شدن برای خواندن دوربین...")
                time.sleep(0.5)

            print("شروع...")

            while not TERMINATE_THREADS and acquire_fresh.Lid.isOpened():
                image_new = acquire_fresh.frame_video
                image_new = cv2.flip(image_new, 1)  # وارون‌سازی تصویر
                image_new.flags.writeable = DEBUGIN  # تنظیم وضعیت نوشتن پیکسل‌ها

                results_new = pose_new.process(image_new)  # پردازش تصویر

                if DEBUGIN:
                    if time.time() - self.since_last_connection_check >= 1:
                        self.since_last_connection_check = time.time()

                    if results_new.pose_landmarks:  # اگر لندمارک‌های حرکت بدن شناسایی شده باشند
                        mechanical_drawing.draw_landmarks(image_new, results_new.pose_landmarks,
                                                          Parliamentary_Pose.POSE_CONNECTIONS,
                                                          mechanical_drawing.DrawingSpec(color=(0, 100, 255),
                                                                                       thickness=2,
                                                                                       circle_radius=4),
                                                          mechanical_drawing.DrawingSpec(color=(0, 255, 255),
                                                                                       thickness=2,
                                                                                       circle_radius=2))

                    cv2.imshow('پیگیری', image_new)
                    cv2.waitKey(3)

                if self.line == None and time.time() - self.since_last_connection_check >= 1:
                    try:
                        self.line = open(r'\\.\pipe\Unity', 'r+b', 0)  # باز کردن لوله ارتباطی با یک نرم‌افزار دیگر
                    except FileNotFoundError:
                        self.line = None
                    self.Details_of_the_time_elapsed_since_publication = time.time()

                if self.line != None:
                    self.data_nl = ""
                    i = 0

                    if results_new.pose_world_landmarks:
                        hand_world_landmarks_new = results_new.pose_world_landmarks
                        for i in range(0, 33):
                            self.data_nl += f"{i}|{hand_world_landmarks_new.landmark[i].x}|{hand_world_landmarks_new.landmark[i].y}|{hand_world_landmarks_new.landmark[i].z}\n"

                    D = self.data_nl.encode('ascii')
                    try:
                        self.line.write(struct.pack('I', len(D)) + D)
                        self.line.seek(0)
                    except Exception as ex:
                        self.line = None

        self.line.close()  # بستن لوله ارتباطی
        acquire_fresh.Lid.release()  # رها کردن دوربین
        cv2.destroyAllWindows()

thread = Detection_of_body_movements().start()  # شروع نخ
i_new = input()
TERMINATE_THREADS = True  # متغیر توقف نخ‌ها
time.sleep(0.5)
exit()
