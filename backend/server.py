from fastapi import FastAPI, APIRouter, HTTPException, UploadFile, File
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field, ConfigDict
from typing import List
from datetime import datetime
from supabase import create_client, Client

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

supabase_url = os.environ.get('SUPABASE_URL')
supabase_key = os.environ.get('SUPABASE_ANON_KEY')
supabase: Client = create_client(supabase_url, supabase_key)

app = FastAPI()
api_router = APIRouter(prefix="/api")

class Resource(BaseModel):
    model_config = ConfigDict(extra="ignore")

    id: str = ""
    url: str
    login: str
    password: str
    is_active: bool = True
    created_at: str = ""

class ResourceCreate(BaseModel):
    url: str
    login: str
    password: str

class ResourceUpdate(BaseModel):
    is_active: bool

@api_router.get("/")
async def root():
    return {"message": "Resource Manager API"}

@api_router.post("/resources", response_model=Resource)
async def create_resource(input: ResourceCreate):
    try:
        data = {
            "url": input.url,
            "login": input.login,
            "password": input.password,
            "is_active": True
        }

        response = supabase.table("resources").insert(data).execute()

        if response.data and len(response.data) > 0:
            return Resource(**response.data[0])
        else:
            raise HTTPException(status_code=500, detail="Failed to create resource")
    except Exception as e:
        logging.error(f"Error creating resource: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/resources", response_model=List[Resource])
async def get_resources():
    try:
        response = supabase.table("resources").select("*").order("created_at", desc=True).execute()
        return [Resource(**item) for item in response.data]
    except Exception as e:
        logging.error(f"Error fetching resources: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.put("/resources/{resource_id}", response_model=Resource)
async def update_resource(resource_id: str, update: ResourceUpdate):
    try:
        response = supabase.table("resources").update(
            {"is_active": update.is_active}
        ).eq("id", resource_id).execute()

        if response.data and len(response.data) > 0:
            return Resource(**response.data[0])
        else:
            raise HTTPException(status_code=404, detail="Resource not found")
    except Exception as e:
        logging.error(f"Error updating resource: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.delete("/resources/{resource_id}")
async def delete_resource(resource_id: str):
    try:
        response = supabase.table("resources").delete().eq("id", resource_id).execute()

        if response.data and len(response.data) > 0:
            return {"message": "Resource deleted"}
        else:
            raise HTTPException(status_code=404, detail="Resource not found")
    except Exception as e:
        logging.error(f"Error deleting resource: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.post("/resources/import")
async def import_resources(file: UploadFile = File(...)):
    try:
        contents = await file.read()
        text = contents.decode('utf-8')

        lines = text.strip().split('\n')
        imported = 0
        errors = []

        for i, line in enumerate(lines, 1):
            line = line.strip()
            if not line:
                continue

            parts = line.rsplit(':', 2)
            if len(parts) != 3:
                errors.append(f"Line {i}: invalid format (expected url:login:pass)")
                continue

            url, login, password = [p.strip() for p in parts]

            if not url or not login or not password:
                errors.append(f"Line {i}: empty fields")
                continue

            try:
                data = {
                    "url": url,
                    "login": login,
                    "password": password,
                    "is_active": True
                }
                supabase.table("resources").insert(data).execute()
                imported += 1
            except Exception as e:
                errors.append(f"Line {i}: {str(e)}")

        return {
            "message": f"Imported resources: {imported}",
            "imported": imported,
            "errors": errors
        }

    except Exception as e:
        logging.error(f"Error importing resources: {str(e)}")
        raise HTTPException(status_code=400, detail=f"Import error: {str(e)}")

app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get('CORS_ORIGINS', '*').split(','),
    allow_methods=["*"],
    allow_headers=["*"],
)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)
