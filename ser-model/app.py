import boto3
import os
import urllib
from boto3.dynamodb.conditions import Attr
import botocore
import time
import tflite_runtime.interpreter as tflite
import numpy as np
from PIL import Image


s3 = boto3.resource('s3')


def get_model(model_bucket=None, local_path=None):
    """Creates TensorFlowLite Interpreter object allowing to load pretrained model for inference. If local_path is not None and exists, model_bucket is ignored.   

    Args:
        model_bucket (S3_Bucket, optional): Bucket containing pretrained model to load. Defaults to None.
        local_path (str, optional): relative path to .tflight file containing pretrained model's data. Defaults to None.

    Returns:
        tuple: tuple containing tflite interpreter, input of the interpreter, output of the interpreter 
    """
    if (local_path and os.path.exists(local_path)):
        print("##################  LOADING MODEL  ##################\nUsing local model...")
        interpreter = tflite.Interpreter(model_path=local_path)
    elif model_bucket:
        if os.path.exists('/tmp/reko-model-light.tflight'):
            print(
            "##################  LOADING MODEL  ##################\nUsing model from last execution...")
        else:
            print(
                "##################  LOADING MODEL  ##################\nUsing model from S3...")
            result = model_bucket.download_file(
                "models/reko-model-light.tflight", '/tmp/reko-model-light.tflight')
        interpreter = tflite.Interpreter(
            model_path='/tmp/reko-model-light.tflight')
    else:
        print("get_model(): No data for loading model was given, returning None")
        return None

    interpreter.allocate_tensors()
    input_details = interpreter.get_input_details()
    output_details = interpreter.get_output_details()
    return interpreter, input_details, output_details


def get_image(bucket, img_name):
    obj = bucket.download_file(img_name, f'/tmp/{img_name}')
    image = np.float32(np.array(Image.open(f'/tmp/{img_name}').convert('RGB').resize((64, 64)))[None, :, :, :])
    return image


def remove_image(bucket, img_name):
    os.remove(f'/tmp/{img_name}')
    result = s3.Object(bucket, img_name).delete()
    result = result['ResponseMetadata']['HTTPStatusCode']
    return 200 <= result < 300


def get_result(pred_vec):
    """ Returns label of the most probable emotion detected among set of eight

    pred_vec - vector containing 8 values of probabilities coresponding to eight consecutive emotions (ANGRY, CALM, DISGUSTED, FEAR, HAPPY, NEUTRAL, SAD, SURPRISE)  
    """
    emo_list = [
        'angry',
        'calm',
        'disgusted',
        'fear',
        'happy',
        'neutral',
        'sad',
        'surprise',
    ]
    pred_vec = np.squeeze(pred_vec)
    results = {emo_list[i]: pred_vec[i] for i in range(8)}
    return max(results, key=results.get).upper(), int(max(pred_vec)*100)


def lambda_handler(event, context):
    voice = urllib.parse.unquote_plus(
        event['Records'][0]['s3']['object']['key'])
    key = os.path.splitext(voice)[0].split('_')[1]
    user = event['Records'][0]['userIdentity']['principalId']
    print(f"################## My (file)name is : {voice} ##################")
    bucket_name = event['Records'][0]['s3']['bucket']['name']

    bucket = s3.Bucket(bucket_name)
    image = get_image(bucket, voice)
    # for DOCKER IMAGE
    # interpreter, input_details, output_details = get_model(
    #     local_path='/models/reko-model-light.tflight')
    # for REGULAR LAMBDA FUNCTION
    interpreter, input_details, output_details = get_model(model_bucket=bucket)
    interpreter.set_tensor(input_details[0]['index'], image)

    print("##################  MODEL & IMAGE LOADED  ##################")

    interpreter.invoke()
    vec = interpreter.get_tensor(output_details[0]['index'])
    prediction_result = get_result(vec)

    print(
        f"################## MY PREDICTIONS: {prediction_result[0]}, confidence: {prediction_result[1]}%  ##################")

    # remove spectrogram
    deleted = remove_image(bucket_name, voice)

    print(
        f"################## Deleted used image: {deleted} ##################")

    # return prediction_result
    dynamodb = boto3.resource('dynamodb')
    dynamoTable = dynamodb.Table('EmotionsTable')
    item = {
        'userId': user,
        'recordID': f'{key}_voice',
        'emotion': prediction_result[0],
        "confidence": prediction_result[1],
        'time': int(time.time())
    }
    try:
        dynamoTable.put_item(
            Item=item
        )
    except botocore.exceptions.ClientError as e:
        raise
