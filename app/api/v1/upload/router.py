from fastapi import APIRouter, File, UploadFile


router= APIRouter(prefix='/upload',tags=['uploads'])

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
    