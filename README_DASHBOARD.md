# Загрузка зависимостей
Создается виртуальная среда, в неё устанавливаются необходимые зависимости
```bash
pip instal -r
```

# Установка URL для обращения к api
Создается папка .streamlit в которой создается файл secrets.toml. Уже в этом файле создается переменные API_DATA_OMS_URL, API_DATA_MSK_URL, API_DETECTORS_URL которые содержат соответствующие пути к api.

# Игнорирование предупреждений streamlit watcher
Также в папке .streamlit создается файл config.toml, в котором прописывается: 
   [server]
    fileWatcherType = "poll"