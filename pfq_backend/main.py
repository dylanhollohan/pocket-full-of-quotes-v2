from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from mangum import Mangum
from pydantic import BaseModel
import boto3
from boto3.dynamodb.conditions import Key
import os
from typing import Optional, List
from datetime import datetime
import uuid

# Initialize FastAPI app
app = FastAPI(title="DynamoDB API", version="1.0.0")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize DynamoDB
dynamodb = boto3.resource('dynamodb')
TABLE_NAME = os.environ.get('DYNAMODB_TABLE', 'MyResourcesTable')
table = dynamodb.Table(TABLE_NAME)

# Pydantic models
class ResourceCreate(BaseModel):
    name: str
    description: Optional[str] = None
    data: Optional[dict] = None

class ResourceUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    data: Optional[dict] = None

class Resource(BaseModel):
    id: str
    name: str
    description: Optional[str] = None
    data: Optional[dict] = None
    created_at: str
    updated_at: str

# Routes
@app.get("/")
def root():
    return {"message": "FastAPI DynamoDB API is running"}

@app.post("/resources", response_model=Resource)
def create_resource(resource: ResourceCreate):
    """Create a new resource in DynamoDB"""
    try:
        resource_id = str(uuid.uuid4())
        timestamp = datetime.utcnow().isoformat()
        
        item = {
            'id': resource_id,
            'name': resource.name,
            'description': resource.description,
            'data': resource.data,
            'created_at': timestamp,
            'updated_at': timestamp
        }
        
        table.put_item(Item=item)
        return Resource(**item)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/resources", response_model=List[Resource])
def list_resources(limit: int = 100):
    """List all resources"""
    try:
        response = table.scan(Limit=limit)
        items = response.get('Items', [])
        return [Resource(**item) for item in items]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/resources/{resource_id}", response_model=Resource)
def get_resource(resource_id: str):
    """Get a specific resource by ID"""
    try:
        response = table.get_item(Key={'id': resource_id})
        item = response.get('Item')
        
        if not item:
            raise HTTPException(status_code=404, detail="Resource not found")
        
        return Resource(**item)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.put("/resources/{resource_id}", response_model=Resource)
def update_resource(resource_id: str, resource: ResourceUpdate):
    """Update a resource"""
    try:
        # Check if resource exists
        response = table.get_item(Key={'id': resource_id})
        if 'Item' not in response:
            raise HTTPException(status_code=404, detail="Resource not found")
        
        # Build update expression
        update_expr = "SET updated_at = :updated_at"
        expr_values = {':updated_at': datetime.utcnow().isoformat()}
        
        if resource.name is not None:
            update_expr += ", #n = :name"
            expr_values[':name'] = resource.name
        
        if resource.description is not None:
            update_expr += ", description = :description"
            expr_values[':description'] = resource.description
        
        if resource.data is not None:
            update_expr += ", #d = :data"
            expr_values[':data'] = resource.data
        
        # Update item
        response = table.update_item(
            Key={'id': resource_id},
            UpdateExpression=update_expr,
            ExpressionAttributeNames={'#n': 'name', '#d': 'data'},
            ExpressionAttributeValues=expr_values,
            ReturnValues='ALL_NEW'
        )
        
        return Resource(**response['Attributes'])
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/resources/{resource_id}")
def delete_resource(resource_id: str):
    """Delete a resource"""
    try:
        # Check if resource exists
        response = table.get_item(Key={'id': resource_id})
        if 'Item' not in response:
            raise HTTPException(status_code=404, detail="Resource not found")
        
        table.delete_item(Key={'id': resource_id})
        return {"message": "Resource deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Lambda handler
handler = Mangum(app)