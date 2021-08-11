from kivy.graphics.texture import Texture
from kivymd.app import MDApp
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.button import MDRaisedButton, MDIconButton, MDFloatingActionButtonSpeedDial
from kivy.uix.image import Image
from kivy.clock import Clock
import cv2
from cvzone.HandTrackingModule import HandDetector
from cvzone.FaceDetectionModule import FaceDetector
import cvzone

class DroneApp(MDApp):
    data = {
        'Hand Gesture': 'hand.png',
        'Face': 'face.png',
        'Body': 'body.png',
    }
    def build(self):
        superBox = MDBoxLayout(orientation='vertical')
        self.image = Image()
        layoutH = MDBoxLayout(orientation='horizontal',
                              size_hint=(1,0))
        # btn1 = MDIconButton(text="Hand Gesture",
        #                       icon="hand.png",
        #                       size_hint=(0.7, 1)
        #                       )
        # btn2 = MDRaisedButton(text="Hand Gesture Mode Activated",
        #                       font_size = 32,
        #                       size_hint = (1, 1),
        #                       pos_hint={'center_x': .5, 'center_y': .5}
        #                      )
        speed_dial = MDFloatingActionButtonSpeedDial()
        speed_dial.data = self.data
        speed_dial.root_button_anim = True
        # layoutH.add_widget(btn1)
        # layoutH.add_widget(btn2)
        layoutH.add_widget(speed_dial)
        # layoutH.add_widget(MDRaisedButton(
        #     text="Hand Gesture",
        #     pos_hint={'left_x': .5, 'left_y': .5},
        #     size_hint=(None, None)
        # ))
        # layoutH.add_widget(MDRaisedButton(
        #     text="Face Follow",
        #     pos_hint={'right_x': .5, 'right_y': .5},
        #     size_hint=(None, None)
        # ))
        layoutV = MDBoxLayout(orientation='vertical')
        layoutV.add_widget(self.image)
        self.capture = cv2.VideoCapture(0)
        Clock.schedule_interval(self.load_video, 1.0/120.0)
        superBox.add_widget(layoutH)
        superBox.add_widget(layoutV)
        return superBox

    def load_video(self, *args):
        detectorHand = HandDetector(maxHands=1)
        detectorFace = FaceDetector()
        gesture = ""
        ret, img = self.capture.read()
        detectorHand.findHands(img)
        lmList, bboxInfo = detectorHand.findPosition(img)
        img, bboxs = detectorFace.findFaces(img, draw=True)
        if bboxs:
                x, y, w, h = bboxs[0]["bbox"]
                bboxRegion = x - 175 - 25, y - 75, 175, h + 75
                cvzone.cornerRect(img, bboxRegion, rt=0, t=10, colorC=(0, 0, 255))

                if lmList and detectorHand.handType() == "Right":
                    handCenter = bboxInfo["center"]
                    insideBox = bboxRegion[0] < handCenter[0] < bboxRegion[0] + bboxRegion[2] and \
                                bboxRegion[0] < handCenter[1] < bboxRegion[1] + bboxRegion[3]

                    if insideBox:
                        cvzone.cornerRect(img, bboxRegion, rt=0, t=10, colorC=(0, 255, 0))

                        figures = detectorHand.fingersUp()
                        # print(figures)

                        thumb, index, middle, ring, pinky = detectorHand.fingersUp()

                        if figures == [1, 1, 1, 1, 1]:
                            gesture = "Open"
                        elif figures == [0, 1, 0, 0, 0]:
                            gesture = "Index"
                        elif figures == [0, 0, 0, 0, 0]:
                            gesture = "Fist"
                        elif figures == [0, 0, 1, 0, 0]:
                            gesture = "Middle"
                        elif figures == [1, 1, 0, 0, 1]:
                            gesture = "SpiderMan"
                        elif figures == [0, 1, 1, 0, 0]:
                            gesture = "Victory"
                        elif figures == [0, 0, 0, 0, 1]:
                            gesture = "Pinky"
                        elif figures == [1, 0, 0, 0, 0]:
                            gesture = "Thumb"

                        cv2.rectangle(img, (bboxRegion[0], bboxRegion[1] + bboxRegion[3] + 10),
                                      (bboxRegion[0] + bboxRegion[2], bboxRegion[1] + bboxRegion[3] + 60),
                                      (0, 255, 0),
                                      cv2.FILLED)

                        cv2.putText(img, f'{gesture}',
                                    (bboxRegion[0] + 10, bboxRegion[1] + bboxRegion[3] + 50),
                                    cv2.FONT_HERSHEY_PLAIN, 2, (0, 0, 0), 2)
        # Frame initialize
        self.image_frame = img
        buffer = cv2.flip(img, 0).tostring()
        texture = Texture.create(size=(img.shape[1], img.shape[0]), colorfmt="bgr")
        texture.blit_buffer(buffer, colorfmt='bgr', bufferfmt='ubyte')
        self.image.texture = texture

if __name__ == "__main__":
    DroneApp().run()