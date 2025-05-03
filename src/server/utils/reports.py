import json
from datetime import datetime
from typing import List, Dict, Any, cast

from fpdf import FPDF

from src.server.config import Settings


class PDFReportGenerator:
    def __init__(self, history_file: str = "request_history.json", settings: Settings = None):
        self.settings = settings or Settings()

        self.history_file = self.settings.APP_FILES_PATH / history_file
        self.max_line_width = 150  # Максимальная ширина строки в мм
        self.cell_height = 6  # Высота строки в мм

    def generate_report(self) -> bytes:
        """Генерирует PDF отчет на основе истории запросов и возвращает байты файла."""
        if not self.history_file.exists():
            raise FileNotFoundError(f"History file {self.history_file} not found")

        with open(self.history_file, "r") as f:
            history = json.load(f)

        pdf = FPDF()
        pdf.set_auto_page_break(auto=True, margin=15)
        pdf.add_page()

        # Настройка стилей
        pdf.set_font("Arial", size=12)
        pdf.set_fill_color(200, 220, 255)

        self._add_title(pdf, "Request History Report")
        self._add_report_metadata(pdf)

        for i, record in enumerate(history, 1):
            self._add_record(pdf, record, i)
            pdf.ln(10)

        # Возвращаем PDF в виде байтов
        report = cast(str, pdf.output(dest='S'))
        return report.encode("latin-1")

    @staticmethod
    def _add_title(pdf: FPDF, title: str):
        pdf.set_font("Arial", style="B", size=16)
        pdf.cell(0, 10, title, ln=1, align="C")
        pdf.ln(5)

    def _add_report_metadata(self, pdf: FPDF):
        pdf.set_font("Arial", size=10)
        pdf.cell(0, 6, f"Generated at: {datetime.now().isoformat()}", ln=1)
        pdf.cell(0, 6, f"Source file: {self.history_file}", ln=1)
        pdf.ln(10)

    def _add_record(self, pdf: FPDF, record: Dict[str, Any], record_num: int):
        pdf.set_font("Arial", style="B", size=12)
        pdf.cell(0, 8, f"Record #{record_num}", ln=1, fill=True)
        pdf.set_font("Arial", size=10)

        # Базовые поля
        base_fields = ["timestamp", "endpoint", "method", "status", "duration_seconds"]
        for field in base_fields:
            if field in record:
                self._add_field(pdf, field, record[field])

        # Динамические поля
        dynamic_fields = set(record.keys()) - set(base_fields)
        for field in dynamic_fields:
            self._add_field(pdf, field, record[field], is_complex=True)

    def _add_field(self, pdf: FPDF, name: str, value: Any, is_complex: bool = False):
        pdf.set_font("Arial", style="B", size=10)
        pdf.cell(40, self.cell_height, f"{name}:", border=0)
        pdf.set_font("Arial", size=10)

        if is_complex:
            if isinstance(value, dict):
                self._add_dict(pdf, value)
            elif isinstance(value, list):
                self._add_list(pdf, value)
            else:
                self._add_long_text(pdf, str(value))
        else:
            self._add_long_text(pdf, str(value))

    def _add_dict(self, pdf: FPDF, data: Dict[str, Any], indent: int = 0):
        for key, value in data.items():
            pdf.set_font("Arial", style="B", size=10)
            pdf.cell(40 + indent, self.cell_height, f"{key}:", border=0)
            pdf.set_font("Arial", size=10)

            if isinstance(value, dict):
                pdf.ln(self.cell_height)
                self._add_dict(pdf, value, indent + 10)
            elif isinstance(value, list):
                pdf.ln(self.cell_height)
                self._add_list(pdf, value, indent + 10)
            else:
                self._add_long_text(pdf, str(value), indent + 40)

    def _add_list(self, pdf: FPDF, items: List[Any], indent: int = 0):
        for i, item in enumerate(items, 1):
            pdf.set_font("Arial", size=10)
            pdf.cell(10 + indent, self.cell_height, f"{i}.", border=0)

            if isinstance(item, dict):
                pdf.ln(self.cell_height)
                self._add_dict(pdf, item, indent + 10)
            elif isinstance(item, list):
                pdf.ln(self.cell_height)
                self._add_list(pdf, item, indent + 10)
            else:
                self._add_long_text(pdf, str(item), indent + 20)

    def _add_long_text(self, pdf: FPDF, text: str, x_offset: int = 40):
        """Добавляет текст с автоматическими переносами строк"""
        lines = []
        current_line = ""

        for word in text.split():
            test_line = f"{current_line} {word}".strip()
            if pdf.get_string_width(test_line) < (self.max_line_width - x_offset):
                current_line = test_line
            else:
                lines.append(current_line)
                current_line = word

        if current_line:
            lines.append(current_line)

        if lines:
            pdf.cell(0, self.cell_height, lines[0], ln=1)

            for line in lines[1:]:
                pdf.cell(x_offset, self.cell_height, "", border=0)
                pdf.cell(0, self.cell_height, line, ln=1)
        else:
            pdf.ln(self.cell_height)
