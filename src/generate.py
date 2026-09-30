"""Command-line generator for a portable monthly schedule block."""
import argparse
from datetime import date
import json
from pathlib import Path
import re
import sys

from schedule_renderer import render_html, structured_days_to_blocks


def _object(value, keys, name):
    if not isinstance(value, dict):
        raise ValueError(f"Поле {name}: нужен объект JSON. Как исправить: используйте фигурные скобки")
    missing, extra = sorted(set(keys) - set(value)), sorted(set(value) - set(keys))
    if missing:
        raise ValueError(f"Поле {name}: нет {', '.join(missing)}. Как исправить: добавьте обязательные поля по schema/month.schema.json")
    if extra:
        raise ValueError(f"Поле {name}: лишнее {', '.join(extra)}. Как исправить: удалите поля вне схемы")
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
        if not isinstance(labels, dict):
            raise ValueError(f"{code}: нужен объект с подписями языка")
        required = {"title", "months", "weekdays"}
        optional = {"day_months"}
        if missing := sorted(required - set(labels)):
            raise ValueError(f"{code}: нет обязательных полей {', '.join(missing)}")
        if extra := sorted(set(labels) - required - optional):
            raise ValueError(f"{code}: лишние поля {', '.join(extra)}")
        if not isinstance(labels["title"], str) or not labels["title"].strip():
            raise ValueError(f"{code}.title: нужна непустая строка")
        fields = [("months", 12), ("weekdays", 7)]
        if "day_months" in labels:
            fields.append(("day_months", 12))
        for field, length in fields:
            values = labels[field]
            if not isinstance(values, list) or len(values) != length or any(not isinstance(v, str) or not v.strip() for v in values):
                raise ValueError(f"{code}.{field}: нужно {length} непустых подписей")
    return data


def validate(input_path, settings_path):
    settings = load_settings(settings_path)
    try:
        payload = json.loads(Path(input_path).read_text(encoding="utf-8"))
    except json.JSONDecodeError as error:
        raise ValueError(f"JSON, строка {error.lineno}, столбец {error.colno}: {error.msg}. Как исправить: проверьте кавычки, запятые и скобки; передайте это сообщение нейросети") from error
    payload = _object(payload, ("year", "month", "language", "days"), "input")
    year, month, language = payload["year"], payload["month"], payload["language"]
    if type(year) is not int or not 1900 <= year <= 2099:
        raise ValueError("Поле year: нужен целый год 1900–2099. Как исправить: укажите год из расписания числом")
    if type(month) is not int or not 1 <= month <= 12:
        raise ValueError("Поле month: нужно число 1–12. Как исправить: укажите месяц из расписания числом")
    if not isinstance(language, str) or language not in settings["languages"]:
        raise ValueError("Поле language: нет подписей для этого языка в settings.json. Как исправить: выберите имеющийся код или добавьте его подписи в settings.json")
    blocks = structured_days_to_blocks(payload["days"], year, month)
    return payload, settings, blocks


def generate(input_path, output_path, settings_path):
    payload, settings, blocks = validate(input_path, settings_path)
    html = render_html(blocks, language=payload["language"], year=payload["year"], month=payload["month"], settings=settings)
    Path(output_path).write_text(html, encoding="utf-8")
    return len(blocks)


def main():
    parser = argparse.ArgumentParser(description="Проверить JSON или создать самостоятельный HTML-блок расписания")
    parser.add_argument("input", help="JSON с месяцем и днями")
    parser.add_argument("output", nargs="?", help="путь для HTML-блока")
    parser.add_argument("--check", action="store_true", help="только проверить JSON, без записи HTML")
    parser.add_argument("--settings", default=str(Path(__file__).resolve().parents[1] / "settings.json"))
    args = parser.parse_args()
    if not args.check and not args.output:
        parser.error("укажите выходной HTML или добавьте --check")
    try:
        if args.check:
            _, _, blocks = validate(args.input, args.settings)
            print(f"JSON проверен: дней {len(blocks)}")
        else:
            count = generate(args.input, args.output, args.settings)
            print(f"Создано: {args.output}; дней: {count}")
    except (ValueError, TypeError, OSError) as error:
        print(f"Ошибка: {error}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
