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

        #   print(test_img.shape)
        test_img = cv2.resize(test_img, dsize=(size, size), interpolation=cv2.INTER_AREA)

        thresh = 200
        test_img = cv2.threshold(test_img, thresh, 255, cv2.THRESH_BINARY_INV)[1]

        test_img = test_img.reshape((1, size, size, 1)).astype(np.float32)
        cv2.imshow('img', test_img.reshape(28, 28))
        cv2.waitKey(0)
        # normalize image
        test_img /= 255.0

        # class_names = {0: 'sun', 1: 'apple', 2: 'face', 3: 'bird', 4: 'ant'}
        # model kgle
        # class_names = {0: 'house', 1: 'face', 2: 'ant', 3: 'fish', 4: 'crown', 5: 'envelope', 6: 'flower', 7: 'bird', 8: 'sun', 9: 'star'}
        # deep model
        # class_names = {0: 'flower', 1: 'bird', 2: 'ant', 3: 'envelope', 4: 'crown', 5: 'star', 6: 'sun', 7: 'fish', 8: 'face', 9: 'house'}
        # model deep perfect
        class_names = {0: 'envelope', 1: 'house', 2: 'face', 3: 'sun', 4: 'star', 5: 'bird', 6: 'flower', 7: 'ant', 8: 'fish',
         9: 'crown'}
        # class_names = {
        #     0: 'pineapple', 1: 'saxophone',
        #     2: 'rabbit', 3: 'envelope',
        #     4: 'crown', 5: 'face',
        #     6: 'moon', 7: 'apple',
        #     8: 'ant', 9: 'bird',
        #     10: 'sword', 11: 'eyeglasses',
        #     12: 'airplane', 13: 'sun',
        #     14: 'umbrella', 15: 'snail',
        #     16: 'cup', 17: 'teapot',
        #     18: 'shark', 19: 'scissors',
        #     20: 'fish', 21: 'house',
        #     22: 'television', 23: 'star',
        #     24: 'flower', 25: 'strawberry',
        #     26: 'octopus'
        # }
        # get predictions
        reconstructed_model = keras.models.load_model('static/model/model_deep_perfect.h5', compile=False)
        pred = reconstructed_model.predict(test_img)[0]

        spred = (-pred).argsort()

        print(pred)
        print(['{}: {}'.format(class_names[i], pred[i]) for i in spred])

        other_predictions = {}
        for i in spred:
            other_predictions[class_names[i]] = pred[i]

        prediction = class_names[spred[0]]

        image = Label.objects.get(name=prediction.lower()).image.name

        context = {
            'prediction': prediction,
            'other_predictions': other_predictions,
            'accuracy': max(pred),
            'image': image
        }
        print('\n\n\n', context)
        default_storage.delete('image.png')
        return Response(context)