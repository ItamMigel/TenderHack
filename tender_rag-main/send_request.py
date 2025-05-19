import requests
import json

def send_question(query):
    url = "http://localhost:8000/ask_question"
    payload = {"query": query}
    headers = {"Content-Type": "application/json"}
    
    response = requests.post(url, json=payload, headers=headers)
    return response.json()

def upload_file():
    response = requests.get("http://localhost:8000/process-local-file")
    if response.status_code == 200:
        data = response.json()
        print(data)
    else:
        print(f"Ошибка: {response.status_code}")

if __name__ == "__main__":
    user_query = "Что означает тармин 223-ФЗ"
    result = send_question(user_query)
    
    print("\nОтвет:")
    print(result["result"])
    
    print("\nРелевантные фрагменты:")
    for i, chunk in enumerate(result["relevant_chunks"]):
        print(f"\nФрагмент {i+1}:")
        print(chunk) 

    print("<------>")
    upload_file()

    print("<------>")
    user_query = "Что означает термин Калуга Астрал"
    result = send_question(user_query)
    
    print("\nОтвет:")
    print(result["result"])
    
    print("\nРелевантные фрагменты:")
    for i, chunk in enumerate(result["relevant_chunks"]):
        print(f"\nФрагмент {i+1}:")
        print(chunk) 



    