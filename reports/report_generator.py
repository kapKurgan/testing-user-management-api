# pytest tests/test_user_api.py -v --html=reports/pytest_report.html


import json
import os
from datetime import datetime
from typing import Dict, Any
import pytest


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

    def generate_html_report(self, test_results: Dict[str, Any]) -> str:
        """Генерация HTML отчета"""
        html_content = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <title>Test Report - {self.timestamp}</title>
                <style>
                    body {{ font-family: Arial, sans-serif; margin: 20px; }}
                    .header {{ background: #2c3e50; color: white; padding: 20px; }}
                    .summary {{ display: flex; justify-content: space-around; margin: 20px 0; }}
                    .stat {{ text-align: center; }}
                    .stat-value {{ font-size: 2em; font-weight: bold; }}
                    .passed {{ color: #27ae60; }}
                    .failed {{ color: #e74c3c; }}
                    .skipped {{ color: #f39c12; }}
                    .details {{ margin-top: 30px; }}
                    .test-case {{ 
                        border: 1px solid #ddd; 
                        margin: 10px 0; 
                        padding: 15px; 
                        border-radius: 5px;
                    }}
                    .test-passed {{ border-left: 5px solid #27ae60; }}
                    .test-failed {{ border-left: 5px solid #e74c3c; }}
                    .test-skipped {{ border-left: 5px solid #f39c12; }}
                    pre {{ background: #f4f4f4; padding: 10px; overflow-x: auto; }}
                    .timestamp {{ color: #7f8c8d; font-size: 0.9em; }}
                </style>
            </head>
            <body>
                <div class="header">
                    <h1>Отчет о тестировании API</h1>
                    <p class="timestamp">Сгенеровано: {self.timestamp}</p>
                </div>
            
                <div class="summary">
                    <div class="stat">
                        <div class="stat-value">{test_results['total']}</div>
                        <div>Всего тестов</div>
                    </div>
                    <div class="stat">
                        <div class="stat-value passed">{test_results['passed']}</div>
                        <div class="passed">Пройдено</div>
                    </div>
                    <div class="stat">
                        <div class="stat-value failed">{test_results['failed']}</div>
                        <div class="failed">Не пройдено</div>
                    </div>
                    <div class="stat">
                        <div class="stat-value skipped">{test_results['skipped']}</div>
                        <div class="skipped">Пропущено</div>
                    </div>
                    <div class="stat">
                        <div class="stat-value">{test_results['duration']:.2f}s</div>
                        <div>Длительность</div>
                    </div>
                </div>
            
                <div class="details">
                    <h2>Детали тестов</h2>
            """

        for test in test_results["tests"]:
            status_class = f"test-{test['status']}"
            html_content += f"""
            <div class="test-case {status_class}">
                <h3>{test['name']}</h3>
                <p><strong>Статус:</strong> <span class="{test['status']}">{test['status'].upper()}</span></p>
                <p><strong>Длительность:</strong> {test['duration']:.3f}s</p>
            """

            if test["error"]:
                html_content += f"<p><strong>Ошибка:</strong></p><pre>{test['error']}</pre>"

            html_content += "</div>"

        html_content += """
            </div>
        </body>
        </html>
        """

        report_path = os.path.join(self.report_dir, f"report_{self.timestamp}.html")
        with open(report_path, "w", encoding="utf-8") as f:
            f.write(html_content)

        print(f"[INFO] HTML отчет сохранен: {report_path}")
        return report_path

    def generate_json_report(self, test_results: Dict[str, Any]) -> str:
        """Генерация JSON отчета"""
        report_path = os.path.join(self.report_dir, f"report_{self.timestamp}.json")

        with open(report_path, "w", encoding="utf-8") as f:
            json.dump(test_results, f, indent=2, ensure_ascii=False)

        print(f"[INFO] JSON отчет сохранен: {report_path}")
        return report_path

    def generate_summary_report(self, test_results: Dict[str, Any]) -> str:
        """Генерация текстового сводного отчета"""
        summary = f"""
            {'=' * 60}
            ОТЧЕТ О ТЕСТИРОВАНИИ
            Время: {self.timestamp}
            {'=' * 60}
            
            ОБЗОР:
            - Всего тестов: {test_results['total']}
            - Пройдено: {test_results['passed']} ✅
            - Не пройдено: {test_results['failed']} ❌
            - Пропущено: {test_results['skipped']} ⏭️
            - Длительность: {test_results['duration']:.2f} секунд
            
            ПРОЙДЕННЫЕ ТЕСТЫ:
            """

        for test in test_results["tests"]:
            if test['status'] == 'passed':
                summary += f"  ✅ {test['name']} ({test['duration']:.3f}s)\n"

        if test_results['failed'] > 0:
            summary += "\nНЕ ПРОЙДЕННЫЕ ТЕСТЫ:\n"
            for test in test_results["tests"]:
                if test['status'] == 'failed':
                    summary += f"  ❌ {test['name']} ({test['duration']:.3f}s)\n"
                    if test['error']:
                        summary += f"     Ошибка: {test['error'][:100]}...\n"

        summary += f"\n{'=' * 60}\n"

        report_path = os.path.join(self.report_dir, f"summary_{self.timestamp}.txt")
        with open(report_path, "w", encoding="utf-8") as f:
            f.write(summary)

        print("[INFO] Сводный отчет:")
        print(summary)
        print(f"[INFO] Сводный отчет сохранен: {report_path}")

        return report_path


@pytest.fixture
def report_gen():
    return ReportGenerator()


def pytest_terminal_summary(terminalreporter, exitstatus):
    """Хук для генерации отчета после завершения тестов"""
    print("\n[INFO] Генерация отчетов...")

    stats = terminalreporter.stats

    passed = len(stats.get('passed', []))
    failed = len(stats.get('failed', []))
    skipped = len(stats.get('skipped', []))
    total = passed + failed + skipped

    test_cases = []

    for item in stats.get('passed', []):
        test_cases.append({
            "name": item.nodeid,
            "status": "passed",
            "duration": item.duration,
            "error": None
        })

    for item in stats.get('failed', []):
        test_cases.append({
            "name": item.nodeid,
            "status": "failed",
            "duration": item.duration,
            "error": str(item.longrepr) if item.longrepr else "Unknown error"
        })

    for item in stats.get('skipped', []):
        test_cases.append({
            "name": item.nodeid,
            "status": "skipped",
            "duration": item.duration,
            "error": str(item.longrepr) if item.longrepr else "Skipped"
        })

    duration = getattr(terminalreporter, '_sessionfinish', 0) - getattr(terminalreporter, '_sessionstarttime', 0)

    from datetime import datetime
    results = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "total": total,
        "passed": passed,
        "failed": failed,
        "skipped": skipped,
        "duration": duration,
        "tests": test_cases
    }

    report_gen = ReportGenerator()
    report_gen.generate_json_report(results)
    report_gen.generate_html_report(results)
    report_gen.generate_summary_report(results)

    print(f"[INFO] ✅ Отчеты сгенерированы в папке: {report_gen.report_dir}")
