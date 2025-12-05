import json
import os
from datetime import datetime

class ReportGenerator:
    """Генератор отчетов о тестировании"""

    def __init__(self, report_dir: str = "reports"):
        self.report_dir = report_dir
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.ensure_report_dir()

    def ensure_report_dir(self):
        """Создание директории для отчетов"""
        if not os.path.exists(self.report_dir):
            os.makedirs(self.report_dir)
            print(f"[INFO] Создана директория отчетов: {self.report_dir}")
