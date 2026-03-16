from fastapi import APIRouter, HTTPException, status
from sqlmodel import select
from app.database import SessionDep
from app.models import *
from app.auth import AuthDep

category_router = APIRouter(tags=["Category Management"])


# CREATE CATEGORY
@category_router.post("/category", response_model=Category)
def create_category(text: str, db: SessionDep, user: AuthDep):
    category = Category(text=text, user_id=user.id)

    db.add(category)
    db.commit()
    db.refresh(category)

    return category


# ADD CATEGORY TO TODO
@category_router.post("/todo/{todo_id}/category/{cat_id}")
def add_category(todo_id: int, cat_id: int, db: SessionDep, user: AuthDep):

    todo = db.exec(select(Todo).where(Todo.id == todo_id, Todo.user_id == user.id)).one_or_none()
    if not todo:
        raise HTTPException(status_code=401, detail="Unauthorized")

    category = db.exec(select(Category).where(Category.id == cat_id, Category.user_id == user.id)).one_or_none()
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")

    todo.categories.append(category)

    db.add(todo)
    db.commit()

    return {"message": "Category added to todo"}


# REMOVE CATEGORY FROM TODO
@category_router.delete("/todo/{todo_id}/category/{cat_id}")
def remove_category(todo_id: int, cat_id: int, db: SessionDep, user: AuthDep):

    todo = db.exec(select(Todo).where(Todo.id == todo_id, Todo.user_id == user.id)).one_or_none()
    if not todo:
        raise HTTPException(status_code=401, detail="Unauthorized")

    category = db.get(Category, cat_id)

    if category not in todo.categories:
        raise HTTPException(status_code=404, detail="Category not assigned")

    todo.categories.remove(category)

    db.add(todo)
    db.commit()

    return {"message": "Category removed from todo"}


# GET TODOS FOR CATEGORY
@category_router.get("/category/{cat_id}/todos", response_model=list[TodoResponse])
def get_todos_for_category(cat_id: int, db: SessionDep, user: AuthDep):

    category = db.exec(select(Category).where(Category.id == cat_id, Category.user_id == user.id)).one_or_none()

    if not category:
        raise HTTPException(status_code=401, detail="Unauthorized")

    return category.todos
