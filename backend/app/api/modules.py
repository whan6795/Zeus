from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from app.schemas.schemas import TaskCreate, TaskStatus
from app.api.dependencies import get_current_user, require_permission, require_script_permission
from app.core.tasks import execute_medical_script
from app.db.database import get_db
from app.db import models
from celery.result import AsyncResult
from app.core.celery_app import celery_app
from typing import Optional

router = APIRouter()


def record_task_in_db(
    db: Session,
    task_id: str,
    module_name: str,
    user_id: int,
    parameters: dict,
    script_name: str = None
) -> models.Task:
    """Helper function to record task in database"""
    db_task = models.Task(
        task_id=task_id,
        module_name=module_name,
        script_name=script_name,
        user_id=user_id,
        status="pending",
        parameters=parameters
    )
    db.add(db_task)
    try:
        db.commit()
        db.refresh(db_task)
        return db_task
    except IntegrityError:
        db.rollback()
        # If task_id already exists, update existing record
        db_task = db.query(models.Task).filter(models.Task.task_id == task_id).first()
        if db_task:
            db_task.status = "pending"
            db_task.parameters = parameters
            db.commit()
            db.refresh(db_task)
        return db_task
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Failed to record task in database: {str(e)}"
        )


@router.post("/module1/execute", response_model=dict)
async def execute_module1(
    task_data: TaskCreate,
    current_user = Depends(require_permission("module1")),
    db: Session = Depends(get_db)
):
    """
    Execute Module 1: Patient Data Analysis
    Requires 'module1' permission
    """
    try:
        # Submit task to Celery
        task = execute_medical_script.apply_async(
            args=["module1", task_data.parameters]
        )
        
        # Record task in database
        record_task_in_db(db, task.id, "module1", current_user.id, task_data.parameters)
        
        return {
            "task_id": task.id,
            "status": "pending",
            "message": "Task submitted successfully"
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to execute task: {str(e)}"
        )


@router.post("/module2/execute", response_model=dict)
async def execute_module2(
    task_data: TaskCreate,
    current_user = Depends(require_permission("module2")),
    db: Session = Depends(get_db)
):
    """
    Execute Module 2: Medical Image Processing
    Requires 'module2' permission
    """
    try:
        # Submit task to Celery
        task = execute_medical_script.apply_async(
            args=["module2", task_data.parameters]
        )
        
        # Record task in database
        record_task_in_db(db, task.id, "module2", current_user.id, task_data.parameters)
        
        return {
            "task_id": task.id,
            "status": "pending",
            "message": "Task submitted successfully"
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to execute task: {str(e)}"
        )


@router.post("/module3/execute", response_model=dict)
async def execute_module3(
    task_data: TaskCreate,
    current_user = Depends(require_permission("module3")),
    db: Session = Depends(get_db)
):
    """
    Execute Module 3: Drug Interaction Analysis
    Requires 'module3' permission
    """
    try:
        # Submit task to Celery
        task = execute_medical_script.apply_async(
            args=["module3", task_data.parameters]
        )
        
        # Record task in database
        record_task_in_db(db, task.id, "module3", current_user.id, task_data.parameters)
        
        return {
            "task_id": task.id,
            "status": "pending",
            "message": "Task submitted successfully"
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to execute task: {str(e)}"
        )


@router.get("/tasks/{task_id}", response_model=TaskStatus)
async def get_task_status(
    task_id: str,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get status of a task by task ID
    Returns task status and result if completed
    """
    task_result = AsyncResult(task_id, app=celery_app)
    
    # Get task from database
    db_task = db.query(models.Task).filter(models.Task.task_id == task_id).first()
    
    if task_result.state == 'PENDING':
        response = {
            "task_id": task_id,
            "status": "pending",
            "result": None,
            "error": None
        }
    elif task_result.state == 'FAILURE':
        response = {
            "task_id": task_id,
            "status": "failed",
            "result": None,
            "error": str(task_result.info)
        }
        # Update database
        if db_task:
            try:
                db_task.status = "failed"
                db_task.error = str(task_result.info)
                db.commit()
            except Exception:
                db.rollback()
    elif task_result.state == 'SUCCESS':
        response = {
            "task_id": task_id,
            "status": "success",
            "result": task_result.result,
            "error": None
        }
        # Update database
        if db_task:
            try:
                db_task.status = "success"
                db_task.result = task_result.result
                db.commit()
            except Exception:
                db.rollback()
    else:
        response = {
            "task_id": task_id,
            "status": task_result.state.lower(),
            "result": task_result.info if hasattr(task_result, 'info') else None,
            "error": None
        }
        # Update database
        if db_task:
            try:
                db_task.status = task_result.state.lower()
                db.commit()
            except Exception:
                db.rollback()
    
    return response


@router.get("/list")
async def list_modules(
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    List available modules with their scripts based on user permissions
    """
    modules = []
    
    # Get all scripts the user has permission to access
    user_script_permissions = set(current_user.script_permissions)
    
    # Define module metadata
    module_metadata = {
        "module1": {
            "name": "Patient Data Analysis",
            "description": "Analyze patient data and generate reports"
        },
        "module2": {
            "name": "Medical Image Processing",
            "description": "Process and analyze medical images"
        },
        "module3": {
            "name": "Drug Interaction Analysis",
            "description": "Analyze drug interactions and provide recommendations"
        }
    }
    
    # Check each module
    for module_id in ["module1", "module2", "module3"]:
        # Check if user has module-level permission
        if module_id in current_user.permissions:
            # Get scripts for this module that user has permission to access
            module_scripts = db.query(models.Script).filter(
                models.Script.module_name == module_id
            ).all()
            
            # Filter scripts by user permissions
            allowed_scripts = []
            for script in module_scripts:
                script_key = f"{script.module_name}.{script.name}"
                if script_key in user_script_permissions:
                    allowed_scripts.append({
                        "id": script.name,
                        "name": script.display_name,
                        "description": script.description,
                        "module_name": script.module_name
                    })
            
            # Only add module if user has at least one script permission
            if allowed_scripts:
                module_info = module_metadata.get(module_id, {})
                modules.append({
                    "id": module_id,
                    "name": module_info.get("name", module_id),
                    "description": module_info.get("description", ""),
                    "scripts": allowed_scripts
                })
    
    return {"modules": modules}


@router.post("/execute", response_model=dict)
async def execute_script(
    module_name: str,
    script_name: str,
    task_data: TaskCreate,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Execute a specific script within a module
    Requires script-level permission
    """
    # Check module permission
    if module_name not in current_user.permissions:
        raise HTTPException(
            status_code=403,
            detail=f"Permission denied. Required module permission: {module_name}"
        )
    
    # Check script permission
    script_key = f"{module_name}.{script_name}"
    if script_key not in current_user.script_permissions:
        raise HTTPException(
            status_code=403,
            detail=f"Permission denied. Required script permission: {script_key}"
        )
    
    try:
        # Submit task to Celery with script name
        task = execute_medical_script.apply_async(
            args=[module_name, task_data.parameters, script_name]
        )
        
        # Record task in database
        record_task_in_db(db, task.id, module_name, current_user.id, task_data.parameters, script_name)
        
        return {
            "task_id": task.id,
            "status": "pending",
            "message": "Task submitted successfully"
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to execute task: {str(e)}"
        )
