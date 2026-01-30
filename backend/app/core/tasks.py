from app.core.celery_app import celery_app
from app.scripts.medical_scripts import get_script


@celery_app.task(bind=True)
def execute_medical_script(self, module_name: str, parameters: dict):
    """
    Execute a medical data processing script asynchronously
    
    Args:
        module_name: Name of the module/script to execute
        parameters: Parameters to pass to the script
    
    Returns:
        Result from the script execution
    """
    try:
        # Get the script function
        script_func = get_script(module_name)
        if not script_func:
            raise ValueError(f"Unknown module: {module_name}")
        
        # Execute the script
        result = script_func(parameters)
        return result
    except Exception as e:
        # Update task state to FAILURE with error info
        self.update_state(
            state='FAILURE',
            meta={'error': str(e)}
        )
        raise
