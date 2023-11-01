import json
from channels.generic.websocket import AsyncWebsocketConsumer
from .tasks import process_image_with_ai
from django.conf import settings
import os
from celery.result import AsyncResult


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

        for file_key_one in files:
            file_key = f"{folderName}/{file_key_one}"
            os.chmod(self.image_path, 0o777)

            # Download the file from AWS S3
            local_file_path = f'{self.image_path}/{file_key.split("/")[-1]}'

            # Process the image using your AI module
            result = process_image_with_ai.apply(args=[local_file_path, file_key, folderName]
                                                 )
            # print(result)
            task_id = result.id

            print(task_id)
            # task = AsyncResult(task_id)
            # if task.state == 'SUCCESS':
            #     print("Result:", task.result)
            # else:
            #     print("Exception:", task.result)

            enhanced_image_name = f"{folderName}/enhanced-{os.path.basename(file_key)}"

            await self.send(enhanced_image_name)
        # await self.send('output')
