from pathlib import Path
import inspect

PROJECT_DIRECTORY = Path.cwd()

def define_caller(is_full_path : bool = False, from_source : bool = False):
    """
    Defines caller`s name. 

    If passed parameter from_source has value False then this function must be called only from logging function (record_log, regist_error) that acts as a wrapper.
    Returns string with full path or relative path. 
    Examples:
        1) "backend.scripts.script1.func1"
        2) "/home/root/project/backend.scripts.script1.func1" - if is_full_path passed as True
    
    Parameters:
    -----------
    is_full_path : bool = False
        returned value will be full path of caller
    
    Returns:
    --------
    str
        a path of caller
    """
    
    frame = inspect.stack()[2]
    module_path = Path(frame.filename)

    if is_full_path:
        return f"{str(module_path)} {frame.function}"

    module_relative_path = str(module_path.relative_to(PROJECT_DIRECTORY)).replace('/', '.').replace('\\', '.').rstrip('.py')
    return f"{module_relative_path}.{frame.function}()"