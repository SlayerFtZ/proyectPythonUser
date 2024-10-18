import os
from azure.ai.vision.imageanalysis import ImageAnalysisClient
from azure.ai.vision.imageanalysis.models import VisualFeatures
from azure.core.credentials import AzureKeyCredential

endpoint = os.environ["VISION_ENDPOINT"]
key = os.environ["VISION_KEY"]

def functionAzure(download_url):
    client = ImageAnalysisClient(
        endpoint=endpoint,
        credential=AzureKeyCredential(key)
    )

    try:
        result = client.analyze_from_url(
            image_url=download_url,
            visual_features=[VisualFeatures.READ] 
        )

        extracted_text = []
        if result.read is not None and result.read.blocks:
            for block in result.read.blocks:
                for line in block.lines:
                    extracted_text.append(line.text)

        json_output = {
            "extracted_text": extracted_text,
            "text_count": len(extracted_text)
        }
        return json_output if extracted_text else {"error": "No text was extracted from the image."}
    
    except Exception as e:
        return {"error": str(e)}
