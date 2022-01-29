import pygame
import pygame.camera
from awsutils import upload_file
from model import GenerateReportRequest, Metadata
import logging

def generate_img_name(metadata: Metadata):
    return metadata.recordID + "_img.jpg"

def process_face(metadata: Metadata, request: GenerateReportRequest):
    logging.info("Capturing face...")
    img_path = "/tmp/face.jpg"
    capture_face(img_path)
    
    generated_img_name = generate_img_name(metadata)
    logging.info('[OK] Face captured.')
    upload_file(img_path, generated_img_name, request)
            
def capture_face(img_path: str):
    pygame.init()
    pygame.camera.init()
    cam = pygame.camera.Camera("/dev/video0", (640,480))
    cam.start()
    img = cam.get_image()
    pygame.image.save(img, img_path)
    cam.stop()
    pygame.quit()