import azure.functions as func
import datetime
import json
import logging
from deepface import DeepFace
import tempfile

app = func.FunctionApp()


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

    except Exception as e:
        logging.error(f"Error processing blob {myblob.name}: {e}")
