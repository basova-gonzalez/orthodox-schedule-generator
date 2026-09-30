"""Command-line generator for a portable monthly schedule block."""
import argparse
from datetime import date
import json
from pathlib import Path
import re

from schedule_renderer import render_html, structured_days_to_blocks


def _object(value, keys, name):
    if not isinstance(value, dict) or set(value) != set(keys):
        raise ValueError(f"{name}: ожидаются поля {', '.join(keys)}")
    return value


def load_settings(path):
    data = _object(json.loads(Path(path).read_text(encoding="utf-8")),
                   ("colors", "font_family", "max_width_px", "additional_highlight_dates", "languages"), "settings")
    colors = _object(data["colors"], ("text", "accent", "red"), "colors")
    for key, value in colors.items():
        if not isinstance(value, str) or not re.fullmatch(r"#[0-9a-fA-F]{6}", value):
            raise ValueError(f"colors.{key}: нужен шестизначный HEX")
    if not isinstance(data["font_family"], str) or not re.fullmatch(r"[\w ,'-]{1,120}", data["font_family"], re.UNICODE):
        raise ValueError("font_family: допустим список локальных семейств шрифта")
    if type(data["max_width_px"]) is not int or not 320 <= data["max_width_px"] <= 1600:
        raise ValueError("max_width_px: нужно целое число от 320 до 1600")
    dates = data["additional_highlight_dates"]
    if not isinstance(dates, list) or any(not isinstance(v, str) or date.fromisoformat(v).isoformat() != v for v in dates):
        raise ValueError("additional_highlight_dates: нужен список дат YYYY-MM-DD")
    if not isinstance(data["languages"], dict) or not data["languages"]:
        raise ValueError("languages: нужен объект языков")
    for code, labels in data["languages"].items():
        if not re.fullmatch(r"[a-z]{2,8}(?:-[A-Za-z0-9]{2,8})*", code):
            raise ValueError(f"Неверный код языка: {code}")
        _object(labels, ("title", "months", "weekdays"), code)
        if not isinstance(labels["title"], str) or not labels["title"].strip():
            raise ValueError(f"{code}.title: нужна непустая строка")
        for field, length in (("months", 12), ("weekdays", 7)):
            values = labels[field]
            if not isinstance(values, list) or len(values) != length or any(not isinstance(v, str) or not v.strip() for v in values):
                raise ValueError(f"{code}.{field}: нужно {length} непустых подписей")
    return data


def generate(input_path, output_path, settings_path):
    settings = load_settings(settings_path)
    payload = _object(json.loads(Path(input_path).read_text(encoding="utf-8")),
                      ("year", "month", "language", "days"), "input")
    year, month, language = payload["year"], payload["month"], payload["language"]
    if type(year) is not int or type(month) is not int or not 1900 <= year <= 2099 or not 1 <= month <= 12:
        raise ValueError("year/month: нужен год 1900–2099 и месяц 1–12")
    if not isinstance(language, str) or language not in settings["languages"]:
        raise ValueError("language: нет подписей для этого языка в settings.json")
    blocks = structured_days_to_blocks(payload["days"], year, month)
    html = render_html(blocks, language=language, year=year, month=month, settings=settings)
    Path(output_path).write_text(html, encoding="utf-8")
    return len(blocks)


def main():
    parser = argparse.ArgumentParser(description="Создать самостоятельный HTML-блок расписания")
    parser.add_argument("input", help="JSON с месяцем и днями")
    parser.add_argument("output", help="путь для HTML-блока")
    parser.add_argument("--settings", default=str(Path(__file__).resolve().parents[1] / "settings.json"))
    args = parser.parse_args()
    count = generate(args.input, args.output, args.settings)
    print(f"Создано: {args.output}; дней: {count}")


if __name__ == "__main__":
    main()
