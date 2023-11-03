import json
from channels.generic.websocket import AsyncWebsocketConsumer
from .tasks import process_image_with_ai
from django.conf import settings
import os
from celery.result import AsyncResult
import zipfile
from io import BytesIO
import boto3
import os
import shutil


class CeleryResultConsumer(AsyncWebsocketConsumer):
    image_folder = 'bridge_ai_bucket/assets'
    image_path = os.path.abspath(os.path.join(
        os.path.dirname(__name__), image_folder))

    async def connect(self):
        print("connected...")
        await self.accept()

    async def receive(self, text_data=None, bytes_data=None, **kwargs):
        print("Recive and processing...")

        data = json.loads(text_data)
        folderName = data["folderName"]
        files = data["uploadFiles"]

        s3 = boto3.client('s3')
        # Create a BytesIO object to store the zip file in memory
        zip_buffer = BytesIO()
        
        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
            for file_key_one in files:
                file_key = f"{folderName}/{file_key_one}"
                os.chmod(self.image_path, 0o777)

                # Download the file from AWS S3
                local_file_path = f'{self.image_path}/{file_key.split("/")[-1]}'

                # Process the image using your AI module
                result = process_image_with_ai.apply(args=[local_file_path, file_key, folderName, zip_file]
                                                    )
                # print(result)
                task_id = result.id
                print("enhanced image name------------------------------------------------------------------------")
                print(task_id)
                # task = AsyncResult(task_id)
                # if task.state == 'SUCCESS':
                #     print("Result:", task.result)
                # else:
                #     print("Exception:", task.result)

                enhanced_image_name = f"{folderName}/enhanced-{os.path.basename(file_key)}"
                print("enhanced image name------------------------------------------------------------------------")
                print(enhanced_image_name)
                await self.send(enhanced_image_name)

        # Reset the zip_buffer's position to the beginning
        zip_buffer.seek(0)

        # Upload the zip folder to S3
        zip_key = f"{folderName}/enhanced_images.zip"
        s3.upload_fileobj(zip_buffer, settings.BUCKET_NAME, zip_key)
        zip_buffer.close()
        shutil.rmtree(self.image_path)
        os.makedirs(self.image_path)
        # os.remove(zip_key)
        # await self.send("output")

