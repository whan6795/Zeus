"""
Script discovery and registration system
Automatically discovers and registers scripts from module directories
"""
import os
import importlib
import inspect
from pathlib import Path
from typing import Dict, List
from sqlalchemy.orm import Session
from app.db.models import Script, User


def discover_scripts() -> List[Dict]:
    """
    Discover all scripts in module directories
    Returns list of script metadata dictionaries
    """
    scripts = []
    scripts_dir = Path(__file__).parent
    
    # Look for module directories (module1, module2, module3, etc.)
    for module_dir in scripts_dir.iterdir():
        if not module_dir.is_dir() or module_dir.name.startswith('_'):
            continue
        
        module_name = module_dir.name
        
        # Look for Python files in the module directory
        for script_file in module_dir.glob('*.py'):
            if script_file.name.startswith('_'):
                continue
            
            script_name = script_file.stem  # filename without .py extension
            file_path = f"app/scripts/{module_name}/{script_file.name}"
            
            # Try to import the script to get metadata
            try:
                module_path = f"app.scripts.{module_name}.{script_name}"
                module = importlib.import_module(module_path)
                
                # Get display name and description from module docstring
                display_name = script_name.replace('_', ' ').title()
                description = ""
                
                if module.__doc__:
                    description = module.__doc__.strip().split('\n')[0]
                
                # Verify the script has an execute function
                if hasattr(module, 'execute') and callable(module.execute):
                    scripts.append({
                        "name": script_name,
                        "module_name": module_name,
                        "display_name": display_name,
                        "description": description,
                        "file_path": file_path
                    })
                    print(f"Discovered script: {module_name}.{script_name}")
                else:
                    print(f"Warning: Script {module_path} does not have an execute function")
            
            except Exception as e:
                print(f"Error importing {module_name}.{script_name}: {e}")
                continue
    
    return scripts


def register_scripts(db: Session) -> None:
    """
    Register discovered scripts to the database
    Grant all users permission to newly registered scripts by default
    """
    discovered_scripts = discover_scripts()
    
    print(f"\nRegistering {len(discovered_scripts)} scripts to database...")
    
    for script_data in discovered_scripts:
        # Check if script already exists
        existing_script = db.query(Script).filter(
            Script.module_name == script_data["module_name"],
            Script.name == script_data["name"]
        ).first()
        
        if existing_script:
            # Update existing script metadata
            existing_script.display_name = script_data["display_name"]
            existing_script.description = script_data["description"]
            existing_script.file_path = script_data["file_path"]
            print(f"  Updated: {script_data['module_name']}.{script_data['name']}")
        else:
            # Create new script
            new_script = Script(**script_data)
            db.add(new_script)
            db.flush()  # Flush to get the ID
            
            # Grant permission to all users by default
            all_users = db.query(User).all()
            for user in all_users:
                user.script_permissions.append(new_script)
            
            print(f"  Registered: {script_data['module_name']}.{script_data['name']} (granted to all users)")
    
    try:
        db.commit()
        print("Script registration completed successfully")
    except Exception as e:
        db.rollback()
        print(f"Error registering scripts: {e}")
        raise


def get_script_function(module_name: str, script_name: str):
    """
    Get the execute function for a specific script
    """
    try:
        module_path = f"app.scripts.{module_name}.{script_name}"
        module = importlib.import_module(module_path)
        
        if hasattr(module, 'execute') and callable(module.execute):
            return module.execute
        else:
            raise ValueError(f"Script {module_path} does not have an execute function")
    
    except Exception as e:
        raise ImportError(f"Failed to load script {module_name}.{script_name}: {e}")
