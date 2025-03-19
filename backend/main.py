from fastapi import FastAPI, UploadFile, File, HTTPException, Depends, Form
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import create_engine, Column, Integer, String, DateTime, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
import os
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr

# Database configuration
SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/human_detector")

engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

app = FastAPI(title="Human Detector API")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Database Models
class Detection(Base):
    __tablename__ = "detections"

    id = Column(Integer, primary_key=True, index=True)
    original_image_path = Column(String, nullable=False)
    visualized_image_path = Column(String, nullable=True)
    number_of_persons = Column(Integer)
    author_name = Column(String(100), nullable=False)
    author_email = Column(String(255), nullable=True)
    title = Column(String(200), nullable=True)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    status = Column(String(50), default="pending", nullable=False)  # pending, processing, completed, failed
    processing_time = Column(Integer, nullable=True)  # in milliseconds

# Pydantic models for request/response
class DetectionCreate(BaseModel):
    author_name: str
    author_email: Optional[EmailStr] = None
    title: Optional[str] = None
    description: Optional[str] = None

class DetectionResponse(BaseModel):
    id: int
    original_image_path: str
    visualized_image_path: Optional[str]
    number_of_persons: int
    author_name: str
    author_email: Optional[str]
    title: Optional[str]
    description: Optional[str]
    created_at: datetime
    updated_at: datetime
    status: str
    processing_time: Optional[int]

    class Config:
        from_attributes = True

class PaginatedResponse(BaseModel):
    items: list[DetectionResponse]
    total: int

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/api/detect", response_model=DetectionResponse)
async def detect_persons(
    file: UploadFile = File(...),
    author_name: str = Form(...),
    author_email: Optional[str] = Form(None),
    title: Optional[str] = Form(None),
    description: Optional[str] = Form(None),
    db: Session = Depends(get_db)
):
    try:
        start_time = datetime.now()
        
        # Create uploads directory if it doesn't exist
        upload_dir = "uploads"
        os.makedirs(upload_dir, exist_ok=True)
        
        # Create subdirectories for original and visualized images
        original_dir = os.path.join(upload_dir, "original")
        visualized_dir = os.path.join(upload_dir, "visualized")
        os.makedirs(original_dir, exist_ok=True)
        os.makedirs(visualized_dir, exist_ok=True)
        
        # Generate unique filename using timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        file_extension = os.path.splitext(file.filename)[1]
        unique_filename = f"{timestamp}_{file.filename}"
        
        # Save the original uploaded file
        original_path = os.path.join(original_dir, unique_filename)
        with open(original_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)
        
        # TODO: Implement actual person detection logic here
        # For now, we'll just return a dummy value
        number_of_persons = 1
        
        # TODO: Generate visualized image with detection boxes
        # For now, we'll just use the same image
        visualized_path = os.path.join(visualized_dir, unique_filename)
        with open(visualized_path, "wb") as buffer:
            buffer.write(content)  # In real implementation, this would be the visualized image
        
        # Calculate processing time
        processing_time = int((datetime.now() - start_time).total_seconds() * 1000)
        
        # Save to database
        detection = Detection(
            original_image_path=original_path,
            visualized_image_path=visualized_path,
            number_of_persons=number_of_persons,
            author_name=author_name,
            author_email=author_email,
            title=title or file.filename,
            description=description,
            status="completed",
            processing_time=processing_time
        )
        db.add(detection)
        db.commit()
        db.refresh(detection)
        
        return detection
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/detections", response_model=PaginatedResponse)
def get_detections(
    skip: int = 0,
    limit: int = 10,
    search: Optional[str] = None,
    sort_by: Optional[str] = "created_at",
    order: Optional[str] = "desc",
    db: Session = Depends(get_db)
):
    query = db.query(Detection)
    
    # Apply search filter if provided
    if search:
        query = query.filter(
            Detection.title.ilike(f"%{search}%") |
            Detection.author_name.ilike(f"%{search}%") |
            Detection.description.ilike(f"%{search}%")
        )
    
    # Apply sorting
    if order == "desc":
        query = query.order_by(getattr(Detection, sort_by).desc())
    else:
        query = query.order_by(getattr(Detection, sort_by).asc())
    
    # Get total count
    total = query.count()
    
    # Get paginated items
    items = query.offset(skip).limit(limit).all()
    
    return {"items": items, "total": total}

@app.get("/api/detections/{detection_id}", response_model=DetectionResponse)
def get_detection(detection_id: int, db: Session = Depends(get_db)):
    detection = db.query(Detection).filter(Detection.id == detection_id).first()
    if detection is None:
        raise HTTPException(status_code=404, detail="Detection not found")
    return detection

# Create database tables
Base.metadata.create_all(bind=engine) 