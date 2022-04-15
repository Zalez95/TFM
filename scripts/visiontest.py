from google.cloud import vision

client = vision.ImageAnnotatorClient()
response = client.annotate_image({
  'image': {'source': {'image_uri': 'gs://indigo-pod-344620/happy.jpg'}},
  'features': [{'type_': vision.Feature.Type.FACE_DETECTION}]
})

print("response:")
print(response)

