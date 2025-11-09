import os
import shutil  # #  Es util para darte los permisos y habildad para copiar y mover archivos
import uuid

from fastapi import File, HTTPException, UploadFile, status

MEDIA_DIR = "app/media"
ALLOW_MIME = ["image/png", "image/jpeg"]


async def save_upload_image(file: UploadFile = File(...)):
    if file.content_type not in ALLOW_MIME:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Solo se permiten imagene jpg o png",
        )

    ext = os.path.splitext(file.filename)[1]
    filename = f"{uuid.uuid4().hex}{ext}"
    file_path = os.path.join(MEDIA_DIR, filename)

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    return {
        "filename": filename,
        "content_type": file.content_type,
        "url": f"/media/{filename}",
    }
