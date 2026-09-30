"""Render explicitly structured plain text as a portable, self-contained HTML block."""
from datetime import date
from html import escape
import re

from church_calendar import is_highlighted


_INVISIBLE = str.maketrans({ord(char): None for char in '\u200b\u200e\u200f\u2060\ufeff'})


def _problem(day_number, day_value, field, problem, fix):
    label = f"День {day_number} ({day_value})" if day_value else f"День {day_number}"
    raise ValueError(f"{label}, поле {field}: {problem}. Как исправить: {fix}")


def _text(value, day_number, day_value, field):
    if not isinstance(value, str):
        _problem(day_number, day_value, field, "нужна строка", "поставьте текст в двойных кавычках; если сведений нет — пустую строку")
    return value.translate(_INVISIBLE).strip()


def _keys(value, expected, day_number, day_value, field):
    if not isinstance(value, dict):
        _problem(day_number, day_value, field, "нужен объект JSON", "используйте фигурные скобки с полями " + ", ".join(expected))
    missing = sorted(set(expected) - set(value))
    extra = sorted(set(value) - set(expected))
    if missing:
        _problem(day_number, day_value, field, "нет поля " + ", ".join(missing), "добавьте обязательное поле; для неизвестных hours/priest используйте пустую строку")
    if extra:
        _problem(day_number, day_value, field, "лишнее поле " + ", ".join(extra), "удалите его или перенесите текст в подходящее поле схемы")


def structured_days_to_blocks(days, year, month):
    """Validate explicit fields and adapt them to safe render blocks."""
    if not isinstance(days, list):
        raise ValueError("Поле days: нужен список дней. Как исправить: заключите дни в квадратные скобки")
    blocks, seen = [], set()
    for index, item in enumerate(days, 1):
        raw_label = item.get("date") if isinstance(item, dict) else None
        label = raw_label if isinstance(raw_label, str) else None
        _keys(item, ("date", "description", "services"), index, label, "day")
        raw_date = _text(item["date"], index, label, "date")
        if not re.fullmatch(r"[0-9]{4}-[0-9]{2}-[0-9]{2}", raw_date):
            _problem(index, label, "date", "нужен формат YYYY-MM-DD", "запишите гражданскую дату, например 2026-04-07")
        try:
            day = date.fromisoformat(raw_date)
        except ValueError:
            _problem(index, label, "date", "такой календарной даты нет", "сверьте число, месяц и год с исходным расписанием")
        if (day.year, day.month) != (year, month):
            _problem(index, label, "date", "дата вне месяца year/month", "сверьте дату с year и month в начале JSON")
        if day in seen:
            _problem(index, label, "date", "повтор даты", "оставьте один объект для этой даты и объедините службы")
        seen.add(day)
        description = item["description"]
        if not isinstance(description, list):
            _problem(index, label, "description", "нужен список строк", "заключите строки описания в квадратные скобки")
        clean_description = [_text(line, index, label, f"description[{n}]") for n, line in enumerate(description, 1)]
        clean_description = [line for line in clean_description if line]
        services = item["services"]
        if not isinstance(services, list):
            _problem(index, label, "services", "нужен список служб", "заключите службы в квадратные скобки; если их нет, используйте []")
        clean_services = []
        for n, service in enumerate(services, 1):
            prefix = f"services[{n}]"
            _keys(service, ("time", "title", "hours", "priest"), index, label, prefix)
            clean = {key: _text(service[key], index, label, f"{prefix}.{key}") for key in ("time", "title", "hours", "priest")}
            if not clean["title"]:
                _problem(index, label, f"{prefix}.title", "название службы пустое", "перенесите название из исходника; если оно неясно, спросите составителя")
            if not re.fullmatch(r"(?:[01]\d|2[0-3]):[0-5]\d", clean["time"]):
                _problem(index, label, f"{prefix}.time", "нужно время HH:MM в 24-часовом формате", "сверьте время с источником и запишите, например, 09:00; если оно неизвестно, спросите составителя")
            clean_services.append(clean)
        blocks.append({"date": day, "description": clean_description, "services": clean_services})
    return sorted(blocks, key=lambda block: block["date"])


def render_html(blocks, *, language, year, month, settings):
    """Escape all content; scope all style selectors to this block's root class."""
    labels = settings["languages"][language]
    colors = settings["colors"]
    font = settings["font_family"]
    width = settings["max_width_px"]
    additional = {date.fromisoformat(value) for value in settings["additional_highlight_dates"]}
    css = f"""<style>
.orthodox-schedule {{box-sizing:border-box;max-width:{width}px;margin:0 auto;padding:24px 20px;color:{colors['text']};font-family:{font};line-height:1.5}}
.orthodox-schedule * {{box-sizing:border-box}}
.orthodox-schedule .os-title {{margin:0 0 20px;font-size:clamp(1.5rem,3vw,2rem);color:{colors['accent']}}}
.orthodox-schedule .os-day {{display:grid;grid-template-columns:minmax(0,1fr) minmax(0,1.4fr);gap:24px;padding:22px 0;border-bottom:1px solid #dddddd}}
.orthodox-schedule .os-day:last-child {{border-bottom:0}}
.orthodox-schedule .os-date {{font-size:1.25rem;font-weight:700;color:{colors['accent']}}}
.orthodox-schedule .os-day.os-highlight .os-date {{color:{colors['red']}}}
.orthodox-schedule .os-description {{margin-top:8px;white-space:pre-line}}
.orthodox-schedule .os-service + .os-service {{margin-top:16px}}
.orthodox-schedule .os-time {{font-weight:700}}
.orthodox-schedule .os-hours,.orthodox-schedule .os-priest {{margin-top:4px}}
@media(max-width:640px) {{.orthodox-schedule .os-day {{grid-template-columns:1fr;gap:10px}}.orthodox-schedule {{padding:16px}}}}
</style>"""
    title = f"{labels['title']} — {labels['months'][month - 1]} {year}"
    out = [css, f'<section class="orthodox-schedule" lang="{escape(language, quote=True)}">', f'<h2 class="os-title">{escape(title, quote=True)}</h2>']
    for block in blocks:
        day = block["date"]
        highlight = ' os-highlight' if is_highlighted(day, additional) else ''
        weekday = labels["weekdays"][day.weekday()]
        day_months = labels.get("day_months", labels["months"])
        visible_date = f"{day.day} {day_months[month - 1]}, {weekday}"
        out.append(f'<div class="os-day{highlight}" data-schedule-date="{day.isoformat()}">')
        out.append('<div class="os-left">')
        out.append(f'<div class="os-date">{escape(visible_date, quote=True)}</div>')
        if block["description"]:
            out.append(f'<div class="os-description">{escape(chr(10).join(block["description"]), quote=True)}</div>')
        out.append('</div><div class="os-right">')
        for service in block["services"]:
            out.append('<div class="os-service">')
            out.append(f'<div><span class="os-time">{service["time"]}</span> — {escape(service["title"], quote=True)}</div>')
            if service["hours"]:
                out.append(f'<div class="os-hours">{escape(service["hours"], quote=True)}</div>')
            if service["priest"]:
                out.append(f'<div class="os-priest">{escape(service["priest"], quote=True)}</div>')
            out.append('</div>')
        out.append('</div></div>')
    out.append('</section>')
    return '\n'.join(out) + '\n'
