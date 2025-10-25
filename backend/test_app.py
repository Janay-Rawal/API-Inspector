from fastapi import FastAPI

app = FastAPI(title="Test API")

@app.get("/hello")
def hello():
    return {"message": "Hello World"}

@app.post("/items")
def create_item(name: str):
    return {"item": name}