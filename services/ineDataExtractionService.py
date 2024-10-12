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

client = ImageAnalysisClient(
    endpoint=endpoint,
    credential=AzureKeyCredential(key)
)

image_url = "https://centralelectoral.ine.mx/wp-content/uploads/2018/12/Credencial-de-Elector-768x490.jpg"

# Call the Read API
result = client.analyze_from_url(
    image_url=image_url,
    visual_features=[VisualFeatures.READ]
)

if result.read is not None and result.read.blocks:
    extracted_text = []
    for block in result.read.blocks:
        for line in block.lines:
            extracted_text.append(line.text)
    
    json_output = json.dumps({"extracted_text": extracted_text}, ensure_ascii=False, indent=4)
    print(json_output)
else:
    print("No text found in the image.")
