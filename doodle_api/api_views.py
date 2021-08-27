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
        print(request.FILES['image'])
        file_name = default_storage.save('imagesd.png', file)
        file_path = default_storage.path(file_name)

        test_img = cv2.imread(file_path, cv2.IMREAD_GRAYSCALE)

        # kernel for morphological operations - erode
        kernel = np.ones((3, 3), np.uint8)

        test_img = cv2.erode(test_img, kernel, iterations=1)
        #   print(test_img.shape)
        test_img = cv2.resize(test_img, dsize=(size, size), interpolation=cv2.INTER_AREA)
        thresh = 200
        test_img = cv2.threshold(test_img, thresh, 255, cv2.THRESH_BINARY_INV)[1]
        #   cv2.imwrite('1s.png', test_img)
        # plt.imshow(test_img)
        test_img = test_img.reshape((1, size, size, 1)).astype(np.float32)



        # print(test_img)

        class_names = {0: 'sun', 1: 'apple', 2: 'face', 3: 'bird', 4: 'ant'}
        # get predictions
        reconstructed_model = keras.models.load_model('static/model/model.h5', compile=False)
        pred = reconstructed_model.predict(test_img)[0]

        spred = (-pred).argsort()

        prediction = class_names[spred[0]]

        image = Label.objects.get(name=prediction.lower()).image.name

        context = {
            'prediction': prediction,
            'accuracy': max(pred),
            'image': image
        }
        print('\n\n\n', context)
        return Response(context)