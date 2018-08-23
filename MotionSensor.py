# An Accessory for a MotionSensor
from collections import deque
import cv2
import logging
from pyhap.accessory import Accessory
from pyhap.const import CATEGORY_SENSOR
import requests
import threading
import time
import pi_motion_lite as detector
import v4l2_motion

logger = logging.getLogger(__name__)

class MotionSensor(Accessory):

    category = CATEGORY_SENSOR

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        serv_motion = self.add_preload_service('MotionSensor', chars=['Name'])
        serv_motion.configure_char('Name', value='MotionSensor')
        self.char_motion_detected = serv_motion.configure_char('MotionDetected')
        # self.detect_thread = threading.Thread(target=detector.Main, kwargs={"callback": self._detected})
        self.detect_thread = threading.Thread(target=v4l2_motion.track, kwargs={"callback": self._detected})
        self.detecton_series = deque(maxlen=10)

        serv_human_motion = self.add_preload_service('MotionSensor', chars=['Name'])
        serv_human_motion.configure_char('Name', value='HumanSensor')
        self.char_human_detected = serv_human_motion.configure_char('MotionDetected')

    def _detected(self, is_detected, img):
        logger.debug("is_detected: " + str(is_detected))
        if is_detected:
            # timestr = time.strftime("%Y%m%d-%H%M%S")
            # cv2.imwrite('./pics/' + timestr + '.jpg',img)
            if not self.char_motion_detected.value:
                timestr = time.strftime("%Y%m%d-%H%M%S")
                cv2.imwrite('./pics/' + timestr + '.jpg',img)
                logger.info("turn on motion sensor")
                self.char_motion_detected.set_value(True)
            if not self.char_human_detected.value:
                _, img_encoded = cv2.imencode('.jpg', img)
                if self.detect_human(img_encoded):
                    logger.info("turn on human sensor")
                    self.char_human_detected.set_value(True)
        self.detecton_series.append(is_detected)

        # check if it's time to turn off the sensor
        if not any(self.detecton_series):
            if self.char_motion_detected.value:
                logger.info("turn off sensor")
                self.char_motion_detected.set_value(False)
            if self.char_human_detected.value:
                self.char_human_detected.set_value(False)

    def detect_human(self, img):
        # take a high resolution picture from another device and check
        test_url = 'http://localhost:9000'
        headers = {'content-type': 'image/jpeg'}
        response = requests.post(test_url, data=img.tostring(), headers=headers)
        logger.info(response)
        return response.status_code == 200


    def run(self):
        # create background thread to detect motion here??
        self.detect_thread.start()
        super().run()

    def stop(self):
        # FIXME: How to kill the thread??
        super().stop()
