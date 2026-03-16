# app/routers/todo.py
from fastapi import APIRouter, HTTPException, Depends
from sqlmodel import select
from app.database import SessionDep
from app.models import *
from app.auth import AuthDep, TodoCreate, TodoUpdate
from fastapi import status

todo_router = APIRouter(tags=["Todo Management"])

# Get all todos for the current user
@todo_router.get('/todos', response_model=list[TodoResponse])
def get_todos(db: SessionDep, user: AuthDep):
    return user.todos

# Get a single todo by ID for the current user
@todo_router.get('/todo/{id}', response_model=TodoResponse)
def get_todo_by_id(id: int, db: SessionDep, user: AuthDep):
    todo = db.exec(select(Todo).where(Todo.id == id, Todo.user_id == user.id)).one_or_none()
    if not todo:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Unauthorized",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return todo

# Create a new todo
@todo_router.post('/todos', response_model=TodoResponse)
def create_todo(db: SessionDep, user: AuthDep, todo_data: TodoCreate):
    todo = Todo(text=todo_data.text, user_id=user.id)
    try:
        db.add(todo)
        db.commit()
        db.refresh(todo)
        return todo
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="An error occurred while creating an item",
        )

# Update an existing todo
@todo_router.put('/todo/{id}', response_model=TodoResponse)
def update_todo(id: int, db: SessionDep, user: AuthDep, todo_data: TodoUpdate):
    todo = db.exec(select(Todo).where(Todo.id == id, Todo.user_id == user.id)).one_or_none()
    if not todo:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Unauthorized",
        )
    if todo_data.text is not None:
        todo.text = todo_data.text
    if todo_data.done is not None:
        todo.done = todo_data.done
    try:
        db.add(todo)
        db.commit()
        db.refresh(todo)
        return todo
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="An error occurred while updating an item",
        )

# Delete a todo
@todo_router.delete('/todo/{id}', status_code=status.HTTP_200_OK)
def delete_todo(id: int, db: SessionDep, user: AuthDep):
    todo = db.exec(select(Todo).where(Todo.id == id, Todo.user_id == user.id)).one_or_none()
    if not todo:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Unauthorized",
        )
    try:
        db.delete(todo)
        db.commit()
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="An error occurred while deleting an item",
        )
