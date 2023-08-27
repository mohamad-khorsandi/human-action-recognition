import copy

import joblib
import numpy as np

import utils


class Person:
    def __init__(self, keypoints, box_points=None):
        self.keypoints = keypoints
        self._feature_list = None
        self.action = None
        if box_points is not list:
            self.box_start_point = box_points[0:2]
            self.box_end_point = box_points[2:4]

    action_recognition_model = joblib.load(utils.read_config('action_recognition_model'))

    @classmethod
    def from_yolo_res(self, yolo_res):
        keypoints = yolo_res.keypoints.xy.numpy()[0]
        box_xyxy = yolo_res.boxes.xyxy[0].numpy().astype(int)
        return Person(keypoints, box_xyxy)

    @classmethod
    def from_keypoint_path(cls, path):
        keypoints = np.load(path)
        return Person(keypoints)

    def save_keypoints(self, tar_path):
        np.save(tar_path, self.keypoints)

    def _flatten(self):
        return self._feature_list.reshape(34,)

    def _max_normalization(self):
        return self._feature_list / np.max(self._feature_list, axis=0)

    def _loc_normalization(self):
        return self._feature_list - np.min(self._feature_list, axis=0)

    def preprocess(self):
        #todo check inplace of flatten
        self._feature_list = copy.copy(self.keypoints)
        self._feature_list = self._loc_normalization()
        self._feature_list = self._max_normalization()
        self._feature_list = self._flatten()
        return self._feature_list

    def predict_action(self):
        features = self.preprocess()
        features = features.reshape(1, -1)
        self.action = self.action_recognition_model.predict(features)[0]
