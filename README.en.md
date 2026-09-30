[Русский](README.md) | **English**

# Orthodox Service Schedule Generator

Create a self-contained HTML block for your website from a monthly service schedule. Each language needs its own source text, JSON file, and HTML block. The tool does not translate content.

## If you are not a programmer

1. Open ChatGPT, Claude, or another AI chat.
2. Paste the entire [ready-to-use prompt](prompts/schedule-to-json.en.md), followed by your schedule text. Answer questions about your system (Mac or Windows) and any unclear details.
3. Follow the AI's instructions in the same chat: it will help you save the JSON, open a terminal in the generator folder, check Python, validate the file, and create HTML. If an error appears, copy it into the same chat so the AI can explain the next step.
4. Open the finished HTML as text and copy all the code into your website's HTML block: Tilda T123, WordPress “Custom HTML,” or an equivalent block. The AI will explain how to open the file's source code on your system.

Download and extract the generator folder onto your computer first. Python 3.10 or later is required; the prompt includes installation guidance. If you use an agent with file access (such as Codex or Claude Code), give it the text and ask it to follow `AGENTS.md`: it will complete the workflow and tell you where the HTML is saved.

## If you are a programmer

Convert your schedule to the [input schema](schema/month.schema.json) manually or with AI assistance. Example “source text → JSON” pairs: [Russian](examples/raw_ru.txt) → [JSON](examples/month_ru.json), [English](examples/raw_en.txt) → [JSON](examples/month_en.json). All example data is fictional. The program does not parse messy text: conversion requires understanding the source and clarifying ambiguities.

```bash
python3 src/generate.py --check examples/month_ru.json
python3 src/generate.py examples/month_ru.json output/month_ru.html
python3 src/generate.py --check examples/month_en.json
python3 src/generate.py examples/month_en.json output/month_en.html
python3 -m unittest discover -s tests -v
```

![Example blocks in two languages](examples/preview.png)

The generator grew out of monthly work for a Russian Orthodox parish abroad. See the [case study](https://kabago.ru/cases/schedule-generator/).

## JSON contract

One UTF-8 JSON file describes one month in one language. The full schema is in [`schema/month.schema.json`](schema/month.schema.json). A brief example:

```json
{
  "year": 2026,
  "month": 4,
  "language": "en",
  "days": [
    {
      "date": "2026-04-07",
      "description": ["Description of the day"],
      "services": [
        {"time": "10:00", "title": "Service name", "hours": "", "priest": ""}
      ]
    }
  ]
}
```

`year` is 1900–2099; `month` is 1–12; `language` is a code from `settings.json`. `date` is a civil date in `YYYY-MM-DD` format within that month. Dates must be unique; days may appear in any order. `description` is an array of text strings. `services` is an array of services; every service requires `time`, `title`, `hours`, and `priest`, and `title` must not be empty. Times use the 24-hour `HH:MM` format. Opening hours and priest details absent from the source are represented by empty strings. A day without services uses `services: []`. Extra fields are rejected. All strings are safely escaped when rendered as HTML.

`--check` validates the file without creating HTML. Errors identify the day, field, problem, and suggested correction; you can send them to the AI. Invalid JSON syntax is reported with a line and column number. Each rendered day has `data-schedule-date="YYYY-MM-DD"`.

## Calendar and settings

Sundays, Pascha, and the Twelve Great Feasts are highlighted in red based on calendar calculations, rather than uppercase text. Pascha uses the Julian calculation; fixed feasts are converted from Old Style dates to civil dates. Additional dates can be specified manually.

Configure everything in `settings.json` (contract: [`schema/settings.schema.json`](schema/settings.schema.json)): `colors.text`, `colors.accent`, and `colors.red` are six-digit HEX colors; `font_family` specifies system fonts; `max_width_px` sets the width; `additional_highlight_dates` lists extra `YYYY-MM-DD` dates (empty by default). Under `languages`, each code has a `title`; `months` contains 12 month forms for the heading (for example, Russian “апрель 2026”); optional `day_months` contains 12 forms for individual dates (for example, “4 апреля”); and `weekdays` contains seven weekday names, Monday through Sunday. If `day_months` is absent, `months` is used; both forms are identical in English. There is no limit on the number of languages. To use another settings file, pass `--settings path/to/settings.json`.

The HTML includes styles scoped to `.orthodox-schedule` and adapts to narrow screens. No external fonts, scripts, or network resources are required. Some platforms remove `<style>` tags; in that case, add the CSS through the platform's supported mechanism. Generated examples are in `output/`; open `examples/preview.html` to view both together.

## If your requirements differ

You can extend the template manually or ask an agent. For example:

> Add an optional `note` field to each service. Update the schema, prompt, validation, renderer, examples, README, and tests. Preserve HTML escaping, `data-schedule-date`, and calendar highlighting. Do not add keyword-based text parsing.

License: MIT.
