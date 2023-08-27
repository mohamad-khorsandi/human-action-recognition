import configparser
import copy
import os.path

from moviepy.video.io.VideoFileClip import VideoFileClip

from action_picture import ActionPicture
import cv2
from dataset import Dataset
from sklearn import svm
import numpy as np
from model import Model
from motrackers import IOUTracker
from motrackers.utils import draw_tracks

def train(model_dir):
    dataset = Dataset('data/points')
    dataset.load()
    x_train, x_test, y_train, y_test = dataset.train_test_split()

    model = Model(svm.SVC(kernel='rbf'))
    model.fit(x_train, y_train)
    model.evaluate(x_test, y_test, dataset.get_label_list())

    model.save(model_dir)


def video_inference(model_filename, video_path=None):
    cap = None
    if video_path:
        cap = cv2.VideoCapture(video_path)
    else:
        cap = cv2.VideoCapture(0)

    dataset = Dataset('data/points')
    dataset.load_labels()
    model = Model.from_file(model_filename)

    frame_count = 0

    cv2.namedWindow("Resized_Window", cv2.WINDOW_NORMAL)
    cv2.resizeWindow("Resized_Window", 1500, 2300)
    tracker = IOUTracker(
            max_lost=20,
            iou_threshold=0.6,
            min_detection_confidence=0.6,
            max_detection_confidence=0.7,
            tracker_output_format="mot_challenge",
        )

    while True:
        ret, frame = cap.read()
        frame_count += 1
        if frame_count % 5 != 0 or not ret:
            continue

        action_pic = ActionPicture(frame)
        action_pic.yolo_inference()
        bbox = (action_pic.box_start_point[0], action_pic.box_start_point[1], action_pic.box_end_point[0] - action_pic.box_start_point[0], action_pic.box_end_point[1] - action_pic.box_start_point[1] )
        tracked_objects = tracker.update(bbox, detection_scores=action_pic.acc_scores, class_ids=np.zeros(len(action_pic.acc_scores)))
        tracked_image = draw_tracks(frame, tracked_objects)
        if len(action_pic.person_list) == 0:
            continue

        # for person in action_pic.person_list:
        #     person.predict_action()
        #     frame = action_pic.draw_rectangle()
        #     frame = action_pic.draw_keypoints()
        #     frame = cv2.putText(frame, dataset.labels[person.action], person.box_start_point, cv2.FONT_HERSHEY_SIMPLEX,1, (255, 0, 0), 1, cv2.LINE_AA)

        cv2.imshow("Resized_Window", tracked_image)
        cv2.waitKey(1)


def picture_inference(model_filename, img):
    model = Model.from_file(model_filename)
    dataset = Dataset('data/points')
    dataset.load_labels()

    action_pic = ActionPicture(img)
    action_pic.yolo_inference()

    pred = model.predict(action_pic.person_list[0].preprocess())[0]
    print(dataset.labels[pred])


def test_model(model_filename):
    dataset = Dataset('data/points')
    dataset.load()

    x_train, y_train, x_test, y_test = dataset.train_test_split(.9)
    model = Model.from_file(model_filename)
    model.evaluate(x_test, y_test, dataset.get_label_list())


def trim_video(video_path, start_time, end_time, output_path):
    clip = VideoFileClip(video_path)
    subclip = clip.subclip(start_time, end_time)
    subclip.write_videofile(output_path, codec='libx264')
    clip.reader.close()


if __name__ == '__main__':
    # train('models')

    # test_model('models/svm0.78')

    # dataset = Dataset('data/points')
    # dataset.add_all_images_to_category('2_standing', 'data/walk or run/walk_or_run_train/train/walk')

    video_path = "rtsp://admin:nimda110@192.168.10.56:554/cam/realmonitor?channel=3&subtype=0"
    # video_path = "rtsp://admin:admin123@192.168.10.68:554/cam/realmonitor?channel=1&subtype=0"
    # if not os.path.exists(video_path):
    #     trim_video('data/namaz.mp4', 60.0, 400.0, video_path)

    video_inference('models/svm_2_0.85', video_path)

    # picture_inference('svm0.83', 'data/walk or run/walk_or_run_train/train/walk/walk_12f08de0.png')
