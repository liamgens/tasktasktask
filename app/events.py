from app import db, socketio
from .models import Task, TaskList


@socketio.on("create_task_list")
def create_task_list(data=None):
    """Create a task list (with an optional task_id for making it a sublist of a task)."""

    task_id = data and data.get("task_id")
    task = None

    if isinstance(task_id, int):
        task = Task.query.filter_by(id=task_id).first()
        if task is None:
            socketio.emit("create_task_list", {"error": "create_task_list with invalid task_id"})
            return
        elif task.sublist is not None:
            socketio.emit("create_task_list", {"error": "create_task_list overwriting existing task_id"})
            return

    task_list = TaskList()
    db.session.add(task_list)
    db.session.commit()

    if task is not None:
        task.sublist_id = task_list.id
        db.session.commit()
        socketio.emit("update_task", task.as_json())

    socketio.emit("create_task_list", task_list.as_json())


@socketio.on("read_task_list")
def read_task_list(data):
    """Read a task list (specified via task_list_id)."""

    task_list_id = data.get("id")

    if not isinstance(task_list_id, int):
        socketio.emit("read_task_list", {"error": "read_task_list with invalid task_list_id"})
        return

    task_list = TaskList.query.filter_by(id=task_list_id).first()
    if task_list is None:
        socketio.emit("read_task_list", {"error": "read_task_list with invalid task_list_id"})
        return

    socketio.emit("read_task_list", task_list.as_json())


@socketio.on("create_task")
def create_task(data):
    """Create a new task and associate it with a specified list."""

    description = data.get("description")
    list_id = data.get("list_id")

    if not isinstance(description, str):
        socketio.emit("create_task", {"error": "create_task with invalid description"})
        return
    elif not isinstance(list_id, int):
        socketio.emit("create_task", {"error": "create_task with invalid list_id"})
        return

    task = Task(description=description, list_id=list_id)
    db.session.add(task)
    db.session.commit()

    socketio.emit("create_task", task.as_json())


@socketio.on("update_task")
def update_task(data):
    """Update the state of a task, given the id of the task and the data to be updated."""

    task_id = data.get("task_id")
    if not isinstance(task_id, int):
        socketio.emit("update_task", {"error": "update_task with invalid task_id"})
        return

    task = Task.query.filter_by(id=task_id).first()
    if not isinstance(task_id, int):
        socketio.emit("update_task", {"error": "update_task with invalid task_id"})
        return

    task.description = data.get("description", task.description)
    task.is_complete = data.get("is_complete", task.is_complete)


@socketio.on("remove_task")
def remove_task(data):
    """Delete an existing task and its sublist tree (including other tasks and sublists)"""

    task_id = data.get("task_id")
    if not isinstance(task_id, int):
        socketio.emit("remove_task", {"error": "remove_task with invalid task_id"})
        return

    task = Task.query.filter_by(id=task_id).first()
    if not isinstance(task_id, int):
        socketio.emit("remove_task", {"error": "remove_task with invalid task_id"})
        return

    _remove_task_list(task.sublist)

    db.session.delete(task)
    db.session.commit()


def _remove_task_list(task_list):
    if not task_list:
        return
    for task in task_list.tasks:
        _remove_task_list(task.sublist)
        db.session.delete(task)  # commit must be made from calling function
