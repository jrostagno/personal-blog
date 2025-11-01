import os
import shutil     ##  Es util para darte los permisos y habildad para copiar y mover archivos
import uuid

from fastapi import APIRouter, File, HTTPException, UploadFile, status


router= APIRouter(prefix='/upload',tags=['uploads'])




MEDIA_DIR= 'app/media'
# ... quiere decir REQUERIDO
@router.post("/bytes")
async def upload_bytes(file:bytes=File(...)):
    return {"file_name":"Archivo subido","size_bytes":len(file)}

@router.post("/file")
async def upload_file(file:UploadFile=File(...)):
    
    return{
        'file_name':file.filename,
        'content_type':file.content_type
    }
    
    
@router.post("/save")
async def save_files(file:UploadFile=File(...)):
    if file.content_type not in ["image/png","image/jpeg"]:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail="Solo se permiten imagene jpg o png")
    
    ext=os.path.splitext(file.filename)[1]
    filename= f'{uuid.uuid4().hex}{ext}'
    file_path=os.path.join(MEDIA_DIR,filename)
    
    with open(file_path,"wb") as buffer:
        shutil.copyfileobj(file.file,buffer)
        
    return {
        "filename":filename,
        "content_type":file.content_type,
        "url":f'/media/{filename}'
    }