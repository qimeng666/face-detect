import azure.functions as func
import datetime
import json
import logging
from deepface import DeepFace
import tempfile
import requests

app = func.FunctionApp()
url = "https://feelxpert.azurewebsites.net/api/upload_image?"


@app.blob_trigger(arg_name="myblob", path="qimengimage",
                               connection="AzureWebJobsStorage") 
def AnalyzeImages(myblob: func.InputStream):
    logging.info(f"Python blob trigger function processed blob"
                f"Name: {myblob.name}"
                f"Blob Size: {myblob.length} bytes")
    try:
        # Save the blob to a temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as temp_file:
            temp_file.write(myblob.read())
            temp_file_path = temp_file.name

        # Analyze the image using DeepFace
        analysis_result = DeepFace.analyze(img_path=temp_file_path, actions=['emotion'])

        # Log the analysis result
        logging.info(f"Analysis result for {myblob.name}: {analysis_result}")
        logging.info(analysis_result[0]['dominant_emotion'])
        blob_url = f"https://qimeng.blob.core.windows.net/qimengimage/{myblob.name}"
        data = {
            "userid": "80001",
            "status": "completed",
            "emotion": analysis_result[0]['dominant_emotion'],
            "originaldatafile": myblob.name,
            "datafilekey": blob_url, 
        }
        headers = {"Content-Type": "application/json"}
        try:
            response = requests.post(url, headers=headers, json=data)
            response.raise_for_status()
            logging.info(str(response))
            if response.status_code == 200:
                logging.info("Data successfully uploaded")
            else:
                logging.info("Unexpected response")
        except requests.exceptions.RequestException as e:
            logging.info("Error occurred:", e)
    except Exception as e:
        logging.error(f"Error processing blob {myblob.name}: {e}")

