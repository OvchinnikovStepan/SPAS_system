#Список всех детекторов доступных для использования

DETECTORS = {
    "avalanche": {
        "path": "api.app.src.detectors.avalanche_detector.avalanche_detector",
        "description": "Анализ лавинной скорости",
        "params": {
            "statistic": "pd.Series",
            "last_point": "pd.Timestamp",
            "sensity": "str",
            "bound_coef": "int",
            "hi_percent": "float",
            "low_percent": "float",
            "statistic_len": "int",
            "statistic_len_for_mean": "int"
        }
    },
    "freezing": {
        "path": "api.app.src.detectors.freezing_detector.freezing_detector",
        "description": "Анализ залипаний",
        "params": {
            "freezing_count": "int",
            "rel_tol": "float",
        }
    },
    "outlier": {
        "path": "api.app.src.detectors.outlier_detector.outlier_detector",
        "description": "Анализ выбросов",
        "params": {
            "statistic": "pd.Series",
            "last_point": "pd.Timestamp",
            "sensity": "str",
            "bound_coef": "int",
            "hi_percent": "float",
            "low_percent": "float",
            "statistic_len": "int",
            "statistic_len_for_mean": "int"
        }
    }
}


