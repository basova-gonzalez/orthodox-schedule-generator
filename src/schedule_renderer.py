"""Render explicitly structured plain text as a portable, self-contained HTML block."""
from datetime import date
from html import escape
import re

from church_calendar import is_highlighted


_INVISIBLE = str.maketrans({ord(char): None for char in '\u200b\u200e\u200f\u2060\ufeff'})


def _text(value, field):
    if not isinstance(value, str):
        raise TypeError(f"{field}: нужна строка")
    return value.translate(_INVISIBLE).strip()


def _lines(value, field):
    if not isinstance(value, list):
        raise TypeError(f"{field}: нужен список строк")
    return [_text(line, f"{field}[{i}]") for i, line in enumerate(value) if _text(line, f"{field}[{i}]")]


def structured_days_to_blocks(days, year, month):
    """Validate language-independent day fields and adapt them to render blocks.

    Unlike the old keyword parser, this never infers a field from its content.
    """
    if not isinstance(days, list):
        raise TypeError("days: нужен список")
    blocks, seen = [], set()
    for i, item in enumerate(days):
        if not isinstance(item, dict) or set(item) != {"date", "description", "services"}:
            raise ValueError(f"days[{i}]: нужны date, description, services")
        raw_date = _text(item["date"], f"days[{i}].date")
        try:
            day = date.fromisoformat(raw_date)
        except ValueError as error:
            raise ValueError(f"days[{i}].date: нужна дата YYYY-MM-DD") from error
        if day.isoformat() != raw_date or (day.year, day.month) != (year, month):
            raise ValueError(f"days[{i}].date: дата вне месяца или не в формате YYYY-MM-DD")
        if day in seen:
            raise ValueError(f"days[{i}].date: повтор даты")
        seen.add(day)
        description = _lines(item["description"], f"days[{i}].description")
        if not isinstance(item["services"], list):
            raise TypeError(f"days[{i}].services: нужен список")
        services = []
        for j, service in enumerate(item["services"]):
            if not isinstance(service, dict) or set(service) != {"time", "title", "hours", "priest"}:
                raise ValueError(f"days[{i}].services[{j}]: нужны time, title, hours, priest")
            time = _text(service["time"], "time")
            if not re.fullmatch(r"(?:[01]\d|2[0-3]):[0-5]\d", time):
                raise ValueError(f"days[{i}].services[{j}].time: нужно HH:MM")
            services.append({key: _text(service[key], key) for key in ("title", "hours", "priest")} | {"time": time})
        blocks.append({"date": day, "description": description, "services": services})
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
        visible_date = f"{day.day} {labels['months'][month - 1]}, {weekday}"
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
