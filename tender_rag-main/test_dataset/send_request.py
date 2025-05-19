import requests
import json
import pandas as pd

def send_question(query):
    url = "http://localhost:1002/ask_question"
    params = {"query": query}
    
    response = requests.get(url, params=params)
    return response.json()

# def upload_file():
#     response = requests.get("http://localhost:8000/process-local-file")
#     if response.status_code == 200:
#         data = response.json()
#         print(data)
#     else:
#         print(f"Ошибка: {response.status_code}")

if __name__ == "__main__":
    # user_query = "Что означает тармин 223-ФЗ"
    # result = send_question(user_query)
    
    # print("\nОтвет:")
    # print(result["result"])
    
    # print("\nРелевантные фрагменты:")
    # for i, chunk in enumerate(result["relevant_chunks"]):
    #     print(f"\nФрагмент {i+1}:")
    #     print(chunk) 
    df = pd.read_csv("/root/tender_rag/test_dataset/questions.csv")
    df["predict"] = ""
    df["predict_folder_1"] = ""
    df["predict_page_1"] = ""
    df["predict_folder_2"] = ""
    df["predict_page_2"] = ""
    df["predict_folder_3"] = ""
    df["predict_page_3"] = ""

    for index, row in df.iterrows():
        # if index == 23:
        #     print("Вот и пришло время")
        #     breakpoint()
        user_query = row["Вопрос"]
        if not isinstance(user_query, str):
            df.at[index, "predict"] = "-"
            df.at[index, "predict_folder_1"] = "-"
            df.at[index, "predict_page_1"] = "-"
            df.at[index, "predict_folder_2"] = "-"
            df.at[index, "predict_page_2"] = "-"
            df.at[index, "predict_folder_3"] = "-"
            df.at[index, "predict_page_3"] = "-"
            continue

        result = send_question(user_query)
        print(index)
        df.at[index, "predict"] = result["result"]
        
        if result["relevant_chunks"]:
            relevant_chunk = result["relevant_chunks"][0]["metadata"]
            df.at[index, "predict_folder_1"] = relevant_chunk["filename"]
            df.at[index, "predict_page_1"] = relevant_chunk["page"]
            relevant_chunk = result["relevant_chunks"][1]["metadata"]
            df.at[index, "predict_folder_2"] = relevant_chunk["filename"]
            df.at[index, "predict_page_2"] = relevant_chunk["page"]
            relevant_chunk = result["relevant_chunks"][2]["metadata"]
            df.at[index, "predict_folder_3"] = relevant_chunk["filename"]
            df.at[index, "predict_page_3"] = relevant_chunk["page"]
    df.to_csv("/root/tender_rag/test_dataset/questions_with_predictions.csv", index=False)

# {'result': 'Чтобы прикрепить МЧД, выполните следующие действия:\n\n1. Перейдите в раздел «Профиль компании» (раздел 11.1).\n2. В блоке «Сведения о пользователях» нажмите кнопку «Операции с МЧД».\n3. Откроется модальное окно «Машиночитаемые доверенности пользователя».\n4. В этом окне загрузите доверенность, добавив xml-файл в поле «Загрузить МЧД из файла».\n5. Нажмите на кнопку «Добавить».\n\nДобавленная доверенность отобразится в таблице.\n\nЕсли в загруженном xml-файле нет подписи, то вам будет предложено добавить файл подписи к МЧД в формате *.p7s, *.sign, *.sig, *.sgn. Для этого:\n\n1. Добавьте файл подписи в соответствующее поле.\n2. Нажмите на кнопку «Сохранить».', 'relevant_chunks': [{'chunk': '# 210\n\n\n## 12.1.5.2 Профиль компании «Операции с МЧД»\n\nДля добавления МЧД сотрудникам организации администратору необходимо перейти в раздел  «Профиль  компании»  (раздел  11.1)  и  в  блоке  «Сведения  о  пользователях»  нажать кнопку «Операции с МЧД» (Рисунок 359).\n\nРисунок 359 - Кнопка «Операции с МЧД»\n\nПри нажатии на кнопку «Операции с МЧД» откроется модальное окно «Машиночитаемые доверенности  пользователя»  (Рисунок  360),  в  котором  администратору необходимо загрузить доверенность,  добавив  xml-файл  в  поле  «Загрузить  МЧД  из  файла» (Рисунок 360 (1)) и нажать на кнопку «Добавить» (Рисунок 360 (2)).\n\nРисунок 360 - Модальное окно «Машиночитаемые доверенности пользователя»\n\nДобавленная доверенность отобразится в таблице, и администратору станут доступны следующие действия, которые описаны в разделе 12.1.5.1.', 'metadata': {'page': 210, 'filename': 'instructions_working with the portal for the supplier'}}, {'chunk': '# 208\n\nМЧД автоматически добавится в таблицу, если в загруженном xml-файле есть подпись лица, имеющего право подписи без доверенности.\n\nЕсли  в  загруженном  xml-файле  нет  подписи,  то  пользователю  отобразится  поле  для добавления файла подписи к МЧД, в которое необходимо добавить файл в формате *.p7s, *.sign, *.sig, *.sgn и нажать на кнопку «Сохранить» (Рисунок 356).\n\nРисунок 356 - Добавление файла подписи к МЧД', 'metadata': {'page': 208, 'filename': 'instructions_working with the portal for the supplier'}}, {'chunk': '## 4.1.5.2. Профиль компании «Операции с МЧД»\n\nДля добавления МЧД сотрудникам организации администратору необходимо перейти в  раздел  «Профиль  компании»  (раздел  5.1)  и  в  блоке  «Сведения  о  пользователях»  нажать кнопку «Операции с МЧД» (Рисунок 117).', 'metadata': {'page': 74, 'filename': 'working_instruction_portal_for_order'}}]}



    