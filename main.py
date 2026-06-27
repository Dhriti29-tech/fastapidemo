from typing import Optional, Dict
from fastapi import FastAPI, Request, Form, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel

app = FastAPI()
templates = Jinja2Templates(directory="templates")

# ── In-memory store ──────────────────────────────────────────────
todos: Dict[int, dict] = {}
_next_id = 1


def next_id() -> int:
    global _next_id
    i = _next_id
    _next_id += 1
    return i


# ── Pydantic models (JSON API) ───────────────────────────────────
class Todo(BaseModel):
    title: str
    completed: bool = False


class UpdateTodo(BaseModel):
    title: Optional[str] = None
    completed: Optional[bool] = None


# ════════════════════════════════════════════════════════════════
#  UI ROUTES  (HTML)
# ════════════════════════════════════════════════════════════════

@app.get("/", response_class=HTMLResponse)
def home(request: Request, edit: Optional[int] = None):
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={"todos": list(todos.values()), "edit_id": edit, "view_todo": None},
    )


# ── CREATE ───────────────────────────────────────────────────────
@app.post("/ui/todos", response_class=RedirectResponse)
def ui_create_todo(title: str = Form(...)):
    tid = next_id()
    todos[tid] = {"id": tid, "title": title, "completed": False}
    return RedirectResponse(url="/", status_code=303)


# ── GET detail ───────────────────────────────────────────────────
@app.get("/ui/todos/{todo_id}", response_class=HTMLResponse)
def ui_get_todo(todo_id: int, request: Request):
    if todo_id not in todos:
        raise HTTPException(status_code=404, detail="Task not found")
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={"todos": list(todos.values()), "edit_id": None, "view_todo": todos[todo_id]},
    )


# ── UPDATE ───────────────────────────────────────────────────────
@app.post("/ui/todos/{todo_id}/update", response_class=RedirectResponse)
def ui_update_todo(
    todo_id: int,
    title: str = Form(...),
    completed: Optional[str] = Form(None),
):
    if todo_id not in todos:
        raise HTTPException(status_code=404, detail="Task not found")
    todos[todo_id]["title"] = title
    todos[todo_id]["completed"] = completed == "on"
    return RedirectResponse(url="/", status_code=303)


# ── TOGGLE ───────────────────────────────────────────────────────
@app.post("/ui/todos/{todo_id}/toggle", response_class=RedirectResponse)
def ui_toggle_todo(todo_id: int):
    if todo_id not in todos:
        raise HTTPException(status_code=404, detail="Task not found")
    todos[todo_id]["completed"] = not todos[todo_id]["completed"]
    return RedirectResponse(url="/", status_code=303)


# ── DELETE ───────────────────────────────────────────────────────
@app.post("/ui/todos/{todo_id}/delete", response_class=RedirectResponse)
def ui_delete_todo(todo_id: int):
    todos.pop(todo_id, None)
    return RedirectResponse(url="/", status_code=303)


# ════════════════════════════════════════════════════════════════
#  JSON API ROUTES
# ════════════════════════════════════════════════════════════════

@app.get("/todos")
def list_todos():
    return {"todos": list(todos.values())}


@app.post("/todos", status_code=201)
def create_todo(todo: Todo):
    tid = next_id()
    todos[tid] = {"id": tid, **todo.model_dump()}
    return {"message": "Todo created", "todo": todos[tid]}


@app.get("/todos/{todo_id}")
def get_todo(todo_id: int):
    if todo_id not in todos:
        raise HTTPException(status_code=404, detail="Task not found")
    return todos[todo_id]


@app.put("/todos/{todo_id}")
def update_todo(todo_id: int, todo: Todo):
    if todo_id not in todos:
        raise HTTPException(status_code=404, detail="Task not found")
    todos[todo_id] = {"id": todo_id, **todo.model_dump()}
    return {"message": "Todo updated", "todo": todos[todo_id]}


@app.patch("/todos/{todo_id}")
def patch_todo(todo_id: int, todo: UpdateTodo):
    if todo_id not in todos:
        raise HTTPException(status_code=404, detail="Task not found")
    todos[todo_id].update(todo.model_dump(exclude_unset=True))
    return {"message": "Todo partially updated", "todo": todos[todo_id]}


@app.delete("/todos/{todo_id}")
def delete_todo(todo_id: int):
    if todo_id not in todos:
        raise HTTPException(status_code=404, detail="Task not found")
    removed = todos.pop(todo_id)
    return {"message": "Todo deleted", "todo": removed}
