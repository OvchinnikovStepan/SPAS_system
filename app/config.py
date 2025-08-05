#Список всех детекторов доступных для использования

DETECTORS = {
    "avalanche": "app.src.detectors.avalanche_detector.avalanche_detector",
    "freezing": "app.src.detectors.freezing_detector.freezing_detector",
    "outlier": "app.src.detectors.outlier_detector.outlier_detector"
}

#Описание каждого детектора

DETECTORS_DESCRIPTION = {
    "avalanche": "Анализ лавинной скорости",
    "freezing": "Анализ залипаний",
    "outlier": "Анализ выбросов"
}
