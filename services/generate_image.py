import os
import requests
import time
from pathlib import Path
from runware import Runware, IImageInference

async def generate_images_with_runware(prompts, wait_seconds=2, output_dir="data/images"):
    """
    Genera imágenes usando Runware por cada escena.
    :param scenes: Lista de escenas (cada escena es un dict con clave 'Imagen')
    :param video_type: Tipo de video ("long" = horizontal, otro = vertical)
    :param wait_seconds: Tiempo de espera entre cada imagen
    :param output_dir: Carpeta donde guardar las imágenes
    :return: Lista de rutas de archivos de imágenes generadas
    """
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    image_files = []
    width, height = (1024, 1024)

    RUN_API_KEY = os.getenv("RUNWARE_API_KEY")
    print(f"🔑 Usando Runware API Key: {RUN_API_KEY} ")
    runware = Runware(api_key=RUN_API_KEY) 
    await runware.connect()

    for idx, prompt in enumerate(prompts, start=1):
        try:
            request = IImageInference(
                positivePrompt=prompt,
                model="runware:101@1", 
                width=width,
                height=height,
            )
            result = await runware.imageInference(requestImage=request)
            if not result:
                return []
            image_url = result[0].imageURL  

            file_path = os.path.join(output_dir, f"image_{idx}.jpg")            
            download_image(image_url, file_path)
            image_files.append(file_path)

        except Exception as e:
            return []

        if wait_seconds > 0:
            time.sleep(wait_seconds)

    await runware.disconnect()
    return image_files

def download_image(image_url, save_path):
    """Descarga una imagen desde una URL y la guarda localmente."""
    resp = requests.get(image_url)
    resp.raise_for_status()
    with open(save_path, "wb") as f:
        f.write(resp.content)
    return save_path
