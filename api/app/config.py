#Список всех детекторов доступных для использования

DETECTORS_CLASS = {
    "avalanche": {
        "name": "AvalancheDetector",
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
        "name": "FreezingDetector",
        "description": "Анализ залипаний",
        "params": {
            "freezing_count": "int",
            "rel_tol": "float",
        }
    },
    "outlier": {
        "name": "OutliersDetector",
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
        "path": "api.app.src.detectors.outliers_detector.outliers_detector",
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

DETECTORS_PATH = "api.app.src.detectors_class.univariate"


