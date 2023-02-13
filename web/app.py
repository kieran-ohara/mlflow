import grpc
import cv2
import numpy as np
import tensorflow as tf
import uuid

from flask import Flask, render_template, request
from tensorflow_serving.apis import prediction_service_pb2_grpc, predict_pb2

GRPC_PORT = "8500"
GRPC_MAX_RECEIVE_MESSAGE_LENGTH = 4096 * 4096 * 3  # Max LENGTH the GRPC should handle

channel = grpc.insecure_channel(f'localhost:{GRPC_PORT}',
    options=[('grpc.max_receive_message_length', GRPC_MAX_RECEIVE_MESSAGE_LENGTH)])

prediction_service = prediction_service_pb2_grpc.PredictionServiceStub(channel)

app = Flask(__name__)
@app.route("/", methods=(["GET", "POST"]))
def index():
    if (request.method == 'GET'):
        return render_template('index.html.j2')
    elif (request.method == 'POST'):
        prediction = predict(request)
        max = np.array2string(np.argmax(prediction))
        sorted = np.argsort(prediction)
        return render_template(
            'index.html.j2',
             max=max,
             sorted=sorted
        )

def predict(request):
    filename = f'/home/vscode/src/predict-handwritten-numbers/web/uploads/${uuid.uuid4()}.png'
    file = request.files['file']
    file.save(filename)

    imageData = cv2.imread(filename, cv2.IMREAD_GRAYSCALE).astype('float32')

    resizedImageData = cv2.resize(imageData, (28, 28))

    tensorInput = tf.expand_dims(resizedImageData, -1)
    tensorInput = tf.expand_dims(tensorInput, axis=0)

    grpc_request = predict_pb2.PredictRequest()
    grpc_request.model_spec.name = 'model'
    grpc_request.model_spec.signature_name = 'serving_default'
    grpc_request.inputs['conv2d_input'].CopyFrom(
        tf.make_tensor_proto(tensorInput, shape=np.shape(tensorInput))
    )

    grpc_response = prediction_service.Predict(grpc_request)

    output = grpc_response.outputs['dense']
    tensor_shape = tf.TensorShape(output.tensor_shape)

    reshaped_output = np.array(output.float_val).reshape(tensor_shape.as_list())

    return reshaped_output