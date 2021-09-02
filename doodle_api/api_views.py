import cv2
from distributed.protocol.tests.test_keras import keras
from django.core.files.storage import default_storage
from django.shortcuts import render
from rest_framework.views import APIView
import numpy as np
from rest_framework.response import Response
from doodle_api.models import  Label
from rest_framework import status


class PredictAPIView(APIView):

    def get_preprocessed_image(image_path, size=28):
        test_img = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)

        kernel = np.ones((3, 3), np.uint8)
        test_img = cv2.erode(test_img, kernel, iterations=5)

        test_img = cv2.resize(test_img, dsize=(size, size), interpolation=cv2.INTER_AREA)

        thresh = 200
        test_img = cv2.threshold(test_img, thresh, 255, cv2.THRESH_BINARY_INV)[1]

        test_img = test_img.reshape((1, size, size, 1)).astype(np.float32)

        return test_img / 255

    def post(self, request, *args, **kwargs):
        size = 28
        file = request.FILES['image']

        file_name = default_storage.save('image.png', file)
        file_path = default_storage.path(file_name)

        test_img = cv2.imread(file_path, 0)

        # kernel for morphological operations - erode
        kernel = np.ones((3, 3), np.uint8)

        test_img = cv2.erode(test_img, kernel, iterations=1)

        # print(test_img.shape)
        test_img = cv2.resize(test_img, dsize=(size, size), interpolation=cv2.INTER_AREA)

        thresh = 200
        test_img = cv2.threshold(test_img, thresh, 255, cv2.THRESH_BINARY_INV)[1]

        test_img = test_img.reshape((1, size, size, 1)).astype(np.float32)

        # normalize image
        test_img /= 255.0

        # 128 BATCH
        class_names = {
            0: 'ant',
            1: 'bird',
            2: 'crown',
            3: 'envelope',
            4: 'face',
            5: 'fish',
            6: 'flower',
            7: 'house',
            8: 'star',
            9: 'sun'
        }

        # get predictions
        reconstructed_model = keras.models.load_model('static/model/model_deep_updated_no_last_maxpool_batch_128 two conv 64.h5', compile=False)
        pred = reconstructed_model.predict(test_img)[0]

        spred = (-pred).argsort()

        all_preds= {class_names[i]: pred[i] for i in spred}

        prediction = class_names[spred[0]]

        image = Label.objects.get(name=prediction.lower()).image.name

        context = {
            'prediction': prediction,
            'all_predictions': all_preds,
            'accuracy': max(pred),
            'image': image
        }

        default_storage.delete('image.png')
        return Response(context)