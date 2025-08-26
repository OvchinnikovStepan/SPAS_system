# Загрузка зависимостей
Создается виртуальная среда, в неё устанавливаются необходимые зависимости
```bash
pip instal -r
```

# Установка URL для обращения к api
Создается папка .streamlit в dashboard/app в которой создается файл secrets.toml. Уже в этом файле создается переменные API_DATA_OMS_URL, API_DATA_MSK_URL, API_DETECTORS_URL которые содержат соответствующие пути к api.
Данные переменные будут содержать ваши ссылки на апи. Если запрос должен отправляться на какой-то endpoint, то их нужно нужно добавить свой endpoint, либо наоборот, если ссылка является конечной, убрать endpoint. Для переменных API_DATA_OMS_URL, API_DATA_MSK_URL, нужно поправить файл upload_data.py, функцию _get_data_url_for_source, в return либо убрать добавление, либо указать свой endpoint. Для переменной API_DETECTORS_URL, в файле request_parameters.py либо полностью считывать переменную, если ссылка конечная либо указать свой endpoint.

# Игнорирование предупреждений streamlit watcher
Также в папке .streamlit создается файл config.toml, в котором прописывается: 
   [server]
    fileWatcherType = "poll"