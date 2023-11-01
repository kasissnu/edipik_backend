from time import sleep
from celery import shared_task, current_task, states
from .ai_image_editing.main import get_enhanced_image
import os
from django.conf import settings
import boto3


@shared_task(bind=True)
def process_image_with_ai(self, image, filename, folderName):
    s3 = boto3.client('s3')

    try:
        download_large_file(s3,
            settings.BUCKET_NAME, filename, image)
    except Exception as e:
        print(f"Failed to download {filename}: {e}")
        self.update_state(state=states.FAILURE, meta={
                          'result': 'failed', 'message': str(e)})
        return {'status': 'failed', 'message': f"Failed to upload enhanced image for {filename}: {e}"}

    enhanced_image_name = f"enhanced-{os.path.basename(filename)}"
    enhanced_image_path = get_enhanced_image(image, enhanced_image_name)
    enhanced_image_key = f"{folderName}/{enhanced_image_name}"

    try:
        s3.upload_file(enhanced_image_path,
                       settings.BUCKET_NAME, enhanced_image_key, Callback=upload_callback_wrapper(image, enhanced_image_path))
    except Exception as e:
        print(f"Failed to upload enhanced image for {filename}: {e}")
        self.update_state(state=states.FAILURE, meta={
                          'result': 'failed', 'message': str(e)})
        return {'status': 'failed', 'message': f"Failed to upload enhanced image for {filename}: {e}"}

    self.update_state(state=states.SUCCESS, meta={'result': 'succeed'})
    return {'status': 'pending', 'task_id': self.request.id}


def upload_callback_wrapper(image, enhanced_image_path):
    def upload_callback(response):
        if os.path.exists(image):
            os.unlink(image)
        if os.path.exists(enhanced_image_path):
            os.unlink(enhanced_image_path)
    return upload_callback


def download_large_file(s3, bucket_name, file_key, local_file_path):
    # Get the size of the S3 object
    response = s3.head_object(Bucket=bucket_name, Key=file_key)
    total_size = response['ContentLength']

    # Determine the number of parts to download the file in
    part_size = 8 * 1024 * 1024  # 8 MB
    num_parts = int(total_size / part_size) + 1

    # Download the file in parts
    with open(local_file_path, 'wb') as f:
        for i in range(num_parts):
            start_byte = i * part_size
            end_byte = min((i + 1) * part_size - 1, total_size - 1)

            range_header = 'bytes={}-{}'.format(start_byte, end_byte)
            response = s3.get_object(
                Bucket=bucket_name, Key=file_key, Range=range_header)

            f.write(response['Body'].read())

    return os.path.exists(local_file_path)
