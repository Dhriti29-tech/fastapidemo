from typing import Optional

from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

class Student(BaseModel):
    name: str
    age: int

class UpdateStudent(BaseModel):
    name: Optional[str] = None
    age: Optional[int] = None

@app.get("/")
def home():
    return {"message": "Welcome to my FastAPI!"}

@app.get("/hello")
def hello():
    return {"message": "Hello World!"}

@app.post("/student")
def create_student(student: Student):
    return {
        "message": "Student Created",
        "student": student
    }

@app.put("/student/{student_id}")
def update_student(student_id: int, student: Student):
    return {
        "message": "Student Updated",
        "id": student_id,
        "student": student
    }

@app.patch("/student/{student_id}")
def patch_student(student_id: int, student: UpdateStudent):
    return {
        "message": "Student Partially Updated",
        "id": student_id,
        "updated_fields": student.model_dump(exclude_unset=True)
    }

@app.delete("/student/{student_id}")
def delete_student(student_id: int):
    return {
        "message": "Student Deleted",
        "id": student_id
    }