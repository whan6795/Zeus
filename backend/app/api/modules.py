from fastapi import APIRouter, Depends, HTTPException
from app.schemas.schemas import TaskCreate, TaskStatus
from app.api.dependencies import get_current_user, require_permission
from app.core.tasks import execute_medical_script
from celery.result import AsyncResult
from app.core.celery_app import celery_app

router = APIRouter()


@router.post("/module1/execute", response_model=dict)
async def execute_module1(
    task_data: TaskCreate,
    current_user = Depends(require_permission("module1"))
):
    """
    Execute Module 1: Patient Data Analysis
    Requires 'module1' permission
    """
    task = execute_medical_script.apply_async(
        args=["module1", task_data.parameters]
    )
    return {
        "task_id": task.id,
        "status": "pending",
        "message": "Task submitted successfully"
    }


@router.post("/module2/execute", response_model=dict)
async def execute_module2(
    task_data: TaskCreate,
    current_user = Depends(require_permission("module2"))
):
    """
    Execute Module 2: Medical Image Processing
    Requires 'module2' permission
    """
    task = execute_medical_script.apply_async(
        args=["module2", task_data.parameters]
    )
    return {
        "task_id": task.id,
        "status": "pending",
        "message": "Task submitted successfully"
    }


@router.post("/module3/execute", response_model=dict)
async def execute_module3(
    task_data: TaskCreate,
    current_user = Depends(require_permission("module3"))
):
    """
    Execute Module 3: Drug Interaction Analysis
    Requires 'module3' permission
    """
    task = execute_medical_script.apply_async(
        args=["module3", task_data.parameters]
    )
    return {
        "task_id": task.id,
        "status": "pending",
        "message": "Task submitted successfully"
    }


@router.get("/tasks/{task_id}", response_model=TaskStatus)
async def get_task_status(
    task_id: str,
    current_user = Depends(get_current_user)
):
    """
    Get status of a task by task ID
    Returns task status and result if completed
    """
    task_result = AsyncResult(task_id, app=celery_app)
    
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
    elif task_result.state == 'SUCCESS':
        response = {
            "task_id": task_id,
            "status": "success",
            "result": task_result.result,
            "error": None
        }
    else:
        response = {
            "task_id": task_id,
            "status": task_result.state.lower(),
            "result": task_result.info if hasattr(task_result, 'info') else None,
            "error": None
        }
    
    return response


@router.get("/list")
async def list_modules(current_user = Depends(get_current_user)):
    """
    List available modules based on user permissions
    """
    modules = []
    
    if "module1" in current_user.permissions:
        modules.append({
            "id": "module1",
            "name": "Patient Data Analysis",
            "description": "Analyze patient data and generate reports"
        })
    
    if "module2" in current_user.permissions:
        modules.append({
            "id": "module2",
            "name": "Medical Image Processing",
            "description": "Process and analyze medical images"
        })
    
    if "module3" in current_user.permissions:
        modules.append({
            "id": "module3",
            "name": "Drug Interaction Analysis",
            "description": "Analyze drug interactions and provide recommendations"
        })
    
    return {"modules": modules}
