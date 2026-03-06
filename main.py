import os
import uuid
import aiofiles
from contextlib import asynccontextmanager
from typing import List

from fastapi import FastAPI, File, UploadFile, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from database import create_db_and_tables
from config import settings
from routers import foods


# ──────────────────────────────────────────
# Lifespan (แทน on_event deprecated)
# ──────────────────────────────────────────
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    create_db_and_tables()
    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
    yield
    # Shutdown (เพิ่ม cleanup ได้ที่นี่)


# ──────────────────────────────────────────
# App instance
# ──────────────────────────────────────────
app = FastAPI(
    title="Food API",
    version="1.0.0",
    description="FastAPI backend with file upload & food management",
    lifespan=lifespan,
)

# ──────────────────────────────────────────
# CORS
# ──────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ──────────────────────────────────────────
# Static files (serve uploaded files)
# ──────────────────────────────────────────
app.mount("/uploads", StaticFiles(directory=settings.UPLOAD_DIR), name="uploads")


# ──────────────────────────────────────────
# Helpers
# ──────────────────────────────────────────
def validate_file(file: UploadFile) -> None:
    """ตรวจสอบประเภทและขนาดไฟล์"""
    if file.content_type not in settings.ALLOWED_CONTENT_TYPES:
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail=f"ไม่รองรับไฟล์ประเภท '{file.content_type}'. "
                   f"รองรับเฉพาะ: {', '.join(settings.ALLOWED_CONTENT_TYPES)}",
        )


def safe_filename(original: str) -> str:
    """สร้างชื่อไฟล์ที่ปลอดภัย ป้องกัน path traversal"""
    ext = os.path.splitext(original)[-1].lower()
    return f"{uuid.uuid4().hex}{ext}"


async def save_upload(file: UploadFile) -> dict:
    """บันทึกไฟล์แบบ async พร้อม UUID filename"""
    validate_file(file)

    filename = safe_filename(file.filename)
    dest_path = os.path.join(settings.UPLOAD_DIR, filename)

    try:
        async with aiofiles.open(dest_path, "wb") as out_file:
            while chunk := await file.read(settings.CHUNK_SIZE):
                await out_file.write(chunk)
    except Exception as exc:
        # ลบไฟล์ที่อาจบันทึกค้างไว้
        if os.path.exists(dest_path):
            os.remove(dest_path)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"บันทึกไฟล์ไม่สำเร็จ: {str(exc)}",
        )
    finally:
        await file.close()

    return {
        "original_filename": file.filename,
        "saved_filename": filename,
        "content_type": file.content_type,
        "url": f"/uploads/{filename}",
    }


# ──────────────────────────────────────────
# Upload endpoints
# ──────────────────────────────────────────
@app.post(
    "/uploadfile/",
    summary="อัปโหลดไฟล์เดียว",
    status_code=status.HTTP_201_CREATED,
)
async def create_upload_file(file: UploadFile = File(...)):
    """
    อัปโหลดไฟล์ 1 ไฟล์  
    - ตรวจสอบประเภทไฟล์  
    - ใช้ async I/O  
    - คืน URL สำหรับเข้าถึงไฟล์
    """
    result = await save_upload(file)
    return result


@app.post(
    "/uploadfiles/",
    summary="อัปโหลดหลายไฟล์พร้อมกัน",
    status_code=status.HTTP_201_CREATED,
)
async def create_upload_files(files: List[UploadFile] = File(...)):
    """
    อัปโหลดหลายไฟล์พร้อมกัน  
    - รองรับสูงสุด MAX_FILES_PER_REQUEST ไฟล์  
    - ถ้าไฟล์ใดล้มเหลว จะ rollback ไฟล์ที่อัปโหลดสำเร็จแล้วทั้งหมด
    """
    if len(files) > settings.MAX_FILES_PER_REQUEST:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"อัปโหลดได้สูงสุด {settings.MAX_FILES_PER_REQUEST} ไฟล์ต่อครั้ง",
        )

    uploaded: list[dict] = []
    try:
        for file in files:
            info = await save_upload(file)
            uploaded.append(info)
    except HTTPException:
        # Rollback: ลบไฟล์ที่บันทึกไปแล้ว
        for f in uploaded:
            path = os.path.join(settings.UPLOAD_DIR, f["saved_filename"])
            if os.path.exists(path):
                os.remove(path)
        raise

    return {
        "message": f"อัปโหลดสำเร็จ {len(uploaded)} ไฟล์",
        "files": uploaded,
    }


# ──────────────────────────────────────────
# Routers
# ──────────────────────────────────────────
app.include_router(foods.router)