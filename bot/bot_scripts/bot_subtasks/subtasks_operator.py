import asyncio


subtasks_list = (

)

def start_subtasks():
    for subtask in subtasks_list:
        asyncio.create_task(subtask())