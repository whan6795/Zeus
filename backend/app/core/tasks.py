from app.core.celery_app import celery_app
from app.scripts.medical_scripts import get_script
from app.scripts.script_registry import get_script_function


@celery_app.task(bind=True)
def execute_medical_script(self, module_name: str, parameters: dict, script_name: str = None):
    """
    Execute a medical data processing script asynchronously
    
    Args:
        module_name: Name of the module
        parameters: Parameters to pass to the script
        script_name: Optional script name for script-level execution
    
    Returns:
        Result from the script execution
    """
    try:
        # If script_name is provided, use new script registry
        if script_name:
            script_func = get_script_function(module_name, script_name)
        else:
            # Fallback to old module-level scripts for backward compatibility
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
