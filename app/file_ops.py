import os
from datetime import datetime, timedelta
from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from fastapi.responses import FileResponse
from jose import jwt, JWTError
from app.auth import get_current_user

router = APIRouter()

UPLOAD_FOLDER = "uploads"
SECRET_KEY = "your-very-secure-secret-key"  
ALGORITHM = "HS256"

#  File Upload Route — Only Ops Users
ALLOWED_EXTENSIONS = {".docx", ".pptx", ".xlsx"}
@router.post("/upload")
async def upload_file(
    file: UploadFile = File(...),
    user: dict = Depends(get_current_user)
):
    if user["role"].lower() != "ops":
        raise HTTPException(status_code=403, detail="Only Ops can upload files")

    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    file_path = os.path.join(UPLOAD_FOLDER, file.filename)

    contents = await file.read()
    print("Uploaded file size:", len(contents))  

    if not contents:
        raise HTTPException(status_code=400, detail="⚠️ Uploaded file is empty")

    with open(file_path, "wb") as f:
        f.write(contents)

    return {
        "filename": file.filename,
        "uploaded_by": user["email"],
        "message": "File uploaded successfully"
    }
#  (Optional)Public Direct Download Route — for testing only
@router.get("/download/{filename}")
def download_file(
    filename: str,
    user: dict = Depends(get_current_user)
):
    file_path = os.path.join(UPLOAD_FOLDER, filename)

    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found")

    return FileResponse(
        path=file_path,
        filename=filename,
        media_type="application/octet-stream"
    )


#List Files — Only Client Can List
@router.get("/list-files")
def list_files(user: dict = Depends(get_current_user)):
    if user["role"].lower() != "client":
        raise HTTPException(status_code=403, detail="Only clients can list files")

    files = os.listdir(UPLOAD_FOLDER)
    return {"files": files}


# Generate Secure Encrypted Download Link — Client Only
@router.get("/download-file/{filename}")
def get_secure_link(filename: str, user: dict = Depends(get_current_user)):
    if user["role"].lower() != "client":
        raise HTTPException(status_code=403, detail="Only clients can get download links")

    file_path = os.path.join(UPLOAD_FOLDER, filename)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found")

    expire = datetime.utcnow() + timedelta(minutes=10)
    payload = {"sub": filename, "exp": expire}
    token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

    url = f"http://localhost:8000/files/secure-download/{token}"
    return {"download_url": url}


#  Secure Download Route — Valid Token Required
@router.get("/secure-download/{token}")
def secure_download(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        filename = payload.get("sub")
    except JWTError:
        raise HTTPException(status_code=403, detail="Invalid or expired token")

    file_path = os.path.join(UPLOAD_FOLDER, filename)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found")

    return FileResponse(
        path=file_path,
        filename=filename,
        media_type="application/octet-stream"
    )
