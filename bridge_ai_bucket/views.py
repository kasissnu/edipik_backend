from django.shortcuts import render
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.exceptions import (
    NotAuthenticated,
    AuthenticationFailed,
    NotFound,
    ParseError,
)
import boto3
from django.conf import settings
import os
from django.http import JsonResponse
from .ai_image_editing.main import pipeline
import json
from .tasks import process_image_with_ai
# Create your views here.


class ProcessImage(generics.GenericAPIView):
    permission_classes = [permissions.AllowAny]
    s3 = boto3.client('s3')

    def process_images(self, folderName, files):

        print(files)
        enhanced_image_urls = []
        response = ""
        for file_key in files:
            file_key = f"{folderName}/{file_key}"
            # Download the file from AWS S3
            local_file_path = f'/tmp/{file_key.split("/")[-1]}'
            print(local_file_path)
            try:
                self.download_large_file(
                    settings.BUCKET_NAME, file_key, local_file_path)
            except Exception as e:
                print(f"Failed to download {file_key}: {e}")
                continue

            # Process the image using your AI module
            process_image_with_ai.delay(local_file_path, file_key, folderName)

            # Upload the enhanced image to AWS S3
            enhanced_image_key = f"{os.path.dirname(file_key)}/enhanced-{os.path.basename(file_key)}"
            try:
                self.s3.upload_file(local_file_path,
                                    settings.BUCKET_NAME, enhanced_image_key)
            except Exception as e:
                print(f"Failed to upload enhanced image for {file_key}: {e}")
                continue

            # Save the URL of the enhanced image
            enhanced_image_url = f"https://{settings.BUCKET_NAME}.s3.amazonaws.com/{enhanced_image_key}"
            enhanced_image_urls.append(enhanced_image_url)

            data = {'enhancedImageUrls': enhanced_image_urls}
            json_data = json.dumps(data)
            response = JsonResponse(json_data, safe=False)
            response = {"message": "Image is proccessing"}
        # Return the list of enhanced image URLs
        return response

    def post(self, request):
        data = request.data
        folderName = data["folderName"]
        files = data["uploadFiles"]

        resData = self.process_images(folderName, files)

        return Response(
            {"data": resData, "message": "Image enhanced successfully"},
            status=status.HTTP_200_OK,
         )
