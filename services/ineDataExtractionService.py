import os
from azure.ai.vision.imageanalysis import ImageAnalysisClient
from azure.ai.vision.imageanalysis.models import VisualFeatures
from azure.core.credentials import AzureKeyCredential
import json


try:
    endpoint = os.environ["VISION_ENDPOINT"]
    key = os.environ["VISION_KEY"]
except KeyError:
    print("Missing environment variable 'VISION_ENDPOINT' or 'VISION_KEY'")
    print("Please set them before running this example.")
    exit()
    
def funcionAzure(download_url):
    client = ImageAnalysisClient(
        endpoint=endpoint,
        credential=AzureKeyCredential(key)
    )

    result = client.analyze_from_url(
        image_url=download_url,
        visual_features=[VisualFeatures.READ]
    )

    if result.read is not None and result.read.blocks:
        extracted_text = []
        for block in result.read.blocks:
            for line in block.lines:
                extracted_text.append(line.text)
        
        return {"extracted_text": extracted_text}
    else:
        return {"extracted_text": []}
