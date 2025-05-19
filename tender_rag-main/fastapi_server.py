from fastapi import FastAPI, Request
from another_pipeline import reload_all_bd, ask_question, add_pdf
import uvicorn
from pathlib import Path
import shutil
from pyprojroot import here


app = FastAPI()
db_collection = reload_all_bd()
history_chat = []

@app.get("/ask_question")
async def ask_question_endpoint(query: str = ""):
    if not query:
        return {"error": "Query is required"}
    print("история:", history_chat)
    result, relevant_chunks = ask_question(query, db_collection, history_chat)
    # history_chat.append((query, result))
    
    return {"result": result, "relevant_chunks": relevant_chunks}

@app.get("/process-local-file/")
async def process_local_file():
    # Путь к локальному файлу
    file_path = here() / "uploads" / "pdf_reports" / "54321.pdf"
    pdf_path = Path(file_path)
    
    # Проверяем существование файла
    if not pdf_path.exists():
        return {"status": "error", "message": "Файл не найден"}
    
    # Копируем файл в директорию uploads
    filename = pdf_path.name
    destination = f"uploads/{filename}"
    
    Path("uploads").mkdir(exist_ok=True)
    shutil.copy(file_path, destination)

    # Добавляем PDF в базу данных
    try:
        add_pdf(db_collection, destination)
        return {"status": "success", "filename": filename}
    except Exception as e:
        return {"status": "error", "message": str(e)}
    

# @app.post("/receive-file/")
# async def receive_file(file: UploadFile = File(...)):
#     # Обработка файла (например, сохранение)
#     Path("uploads").mkdir(exist_ok=True)
#     destination = f"uploads/{file.filename}"
#     with open(destination, "wb") as f:
#         while chunk := await file.read(1024*1024):  # Чтение по 1 МБ
#             f.write(chunk)

#     add_pdf(db_collection, destination)
#     return {"status": "success", "filename": file.filename}

# @app.get("/process-local-file/")
# async def process_local_file():
#     # Путь к локальному файлу
#     file_path = here() / "54321.pdf"
#     pdf_path = Path(file_path)
    
#     # Проверяем существование файла
#     if not pdf_path.exists():
#         return {"status": "error", "message": "Файл не найден"}
    
#     # Копируем файл в директорию uploads
#     filename = pdf_path.name
#     destination = f"uploads/{filename}"
#     shutil.copy(file_path, destination)
    
#     return {"status": "success", "filename": filename}


if __name__ == "__main__":
    uvicorn.run("fastapi_server:app", host="0.0.0.0", port=1002, reload=False)
# destination = here() / "uploads" / "pdf_reports" / "54321.pdf"
# add_pdf(db_collection, destination)