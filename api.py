import os
import torch
import torch.nn as nn
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from transformers import AutoModel, AutoTokenizer
from fastapi.middleware.cors import CORSMiddleware


# Определение класса модели (словарь CLASS_NAMES можно удалить, если не используется)
CLASS_NAMES = {
    0: 'Электронная Подпись (ЭП) и МЧД',
    1: 'Закупки и Участие',
    2: 'Контракты',
    3: 'Информация, Справка и Функционал',
    4: 'Управление Аккаунтом и Доступом',
    5: 'ЭДО и Электронное Исполнение',
    6: 'Уведомления',
    7: 'Оферты и Каталог (СТЕ)',
    8: 'Прайс-листы',
    9: 'Документооборот (Общий)',
    10: 'Технические Вопросы и Поддержка',
    11: 'Навигация, Поиск и Интерфейс'
}

# Архитектура модели
class BertCLF(nn.Module):
    def __init__(self, hid_size=768, num_classes=12):
        super(BertCLF, self).__init__()
        self.model = AutoModel.from_pretrained(
            'Tochka-AI/ruRoPEBert-e5-base-2k',
            trust_remote_code=True,
            low_cpu_mem_usage=True,
            device_map="auto" if torch.cuda.is_available() else None
        )
        self.ln1 = nn.Linear(hid_size, hid_size // 2)
        self.relu = nn.LeakyReLU()
        self.ln2 = nn.Linear(hid_size // 2, num_classes)

    def forward(self, x, attn_mask):
        embeddings = self.model(x, attention_mask=attn_mask).pooler_output
        return self.ln2(self.relu(self.ln1(embeddings)))

# Инициализация FastAPI приложения
app = FastAPI(
    title="Text Classification API", 
    description="API для классификации текстовых запросов пользователей"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Модель запроса
class ClassificationRequest(BaseModel):
    text: str

# Модель ответа (возвращается только id класса)
class ClassificationResponse(BaseModel):
    class_id: int

# Загрузка модели и токенизатора при старте приложения
@app.on_event("startup")
async def load_model():
    global model, tokenizer, device
    
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    print(f"Using device: {device}")
    
    model_path = 'ruropebert_clf1.pth'
    if not os.path.exists(model_path):
        raise RuntimeError(f"Model file {model_path} not found. Please download it first.")
    
    try:
        print("Loading tokenizer...")
        tokenizer = AutoTokenizer.from_pretrained(
            'Tochka-AI/ruRoPEBert-e5-base-2k', 
            trust_remote_code=True
        )
        print("Tokenizer loaded successfully")
        
        print("Loading model...")
        model = BertCLF(hid_size=768, num_classes=12)
        model.load_state_dict(torch.load(model_path, map_location=device))
        model.to(device)
        model.eval()
        print("Model loaded successfully")
    except Exception as e:
        print(f"Error loading model: {e}")
        raise RuntimeError(f"Failed to load model: {e}")

# Эндпоинт для классификации
@app.post("/classify", response_model=ClassificationResponse)
async def classify_text(request: ClassificationRequest):
    try:
        inputs = tokenizer(
            request.text, 
            truncation=True, 
            max_length=128, 
            padding='max_length', 
            return_tensors='pt'
        )
        input_ids = inputs['input_ids'].to(device)
        attention_mask = inputs['attention_mask'].to(device)
        
        with torch.no_grad():
            outputs = model(input_ids, attn_mask=attention_mask)
        
        predicted_class_id = outputs.argmax(dim=-1).item()
        return ClassificationResponse(class_id=predicted_class_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Classification error: {str(e)}")

# Эндпоинт для проверки работоспособности сервиса
@app.get("/")
async def root():
    return {"status": "ok", "message": "Text classification API is running"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=1001)
