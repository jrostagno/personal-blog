from fastapi import APIRouter, File, UploadFile

from app.services.save_file import save_upload_image

router = APIRouter(prefix="/upload", tags=["uploads"])


MEDIA_DIR = "app/media"


# ... quiere decir REQUERIDO
@router.post("/bytes")
async def upload_bytes(file: bytes = File(...)):
    return {"file_name": "Archivo subido", "size_bytes": len(file)}


@router.post("/file")
async def upload_file(file: UploadFile = File(...)):

    return {"file_name": file.filename, "content_type": file.content_type}


@router.post("/save")
async def save_files(file: UploadFile = File(...)):
    save = await save_upload_image(file)

    return {
        "filename": save["filename"],
        "conten_type": save["content_type"],
        "url": save["url"],
    }
