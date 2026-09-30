import json
import sys
import tempfile
import unittest
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from church_calendar import FIXED_TWELVE, great_feasts, is_highlighted, julian_to_gregorian, pascha
from generate import generate, load_settings
from schedule_renderer import render_html, structured_days_to_blocks


class CalendarTests(unittest.TestCase):
    def test_pascha_against_known_civil_dates(self):
        known = {2016: "05-01", 2017: "04-16", 2018: "04-08", 2019: "04-28",
                 2020: "04-19", 2021: "05-02", 2022: "04-24", 2023: "04-16",
                 2024: "05-05", 2025: "04-20", 2026: "04-12"}
        for year, month_day in known.items():
            with self.subTest(year=year):
                self.assertEqual(pascha(year), date.fromisoformat(f"{year}-{month_day}"))

    def test_all_twelve_feasts_for_two_years(self):
        expected_fixed = {"nativity_theotokos": "09-21", "exaltation_cross": "09-27",
                          "entry_theotokos": "12-04", "nativity_christ": "01-07",
                          "theophany": "01-19", "presentation": "02-15",
                          "annunciation": "04-07", "transfiguration": "08-19",
                          "dormition": "08-28"}
        movable = {2026: ("04-05", "05-21", "05-31"),
                   2027: ("04-25", "06-10", "06-20")}
        for year in (2026, 2027):
            feasts = great_feasts(year)
            self.assertEqual(len(feasts), 13)
            self.assertEqual(set(FIXED_TWELVE), set(expected_fixed))
            for key, month_day in expected_fixed.items():
                self.assertEqual(feasts[key], date.fromisoformat(f"{year}-{month_day}"))
            for key, month_day in zip(("entry_jerusalem", "ascension", "pentecost"), movable[year]):
                self.assertEqual(feasts[key], date.fromisoformat(f"{year}-{month_day}"))
            self.assertEqual(feasts["pascha"], pascha(year))

    def test_sunday_and_custom_date(self):
        self.assertTrue(is_highlighted(date(2026, 4, 19)))
        self.assertFalse(is_highlighted(date(2026, 4, 20)))
        self.assertTrue(is_highlighted(date(2026, 4, 20), {date(2026, 4, 20)}))


class GeneratorTests(unittest.TestCase):
    def test_examples_produce_separate_safe_blocks(self):
        for lang in ("ru", "en"):
            with self.subTest(lang=lang), tempfile.TemporaryDirectory() as directory:
                output = Path(directory) / "month.html"
                self.assertEqual(generate(ROOT / "examples" / f"month_{lang}.json", output, ROOT / "settings.json"), 4)
                html = output.read_text(encoding="utf-8")
                self.assertEqual(html.count('data-schedule-date="'), 4)
                self.assertIn('data-schedule-date="2026-04-05"', html)
                self.assertIn('class="os-day os-highlight" data-schedule-date="2026-04-05"', html)
                self.assertIn('class="os-day" data-schedule-date="2026-04-04"', html)
                self.assertIn(f'lang="{lang}"', html)
                self.assertIn("<style>", html)
                self.assertNotIn("@import", html)

    def test_all_user_text_is_escaped(self):
        marker = '<img src=x onerror="alert(1)"> &'
        days = [{"date": "2026-04-07", "description": [marker],
                 "services": [{"time": "10:00", "title": marker, "hours": marker, "priest": marker}]}]
        blocks = structured_days_to_blocks(days, 2026, 4)
        html = render_html(blocks, language="en", year=2026, month=4,
                           settings=load_settings(ROOT / "settings.json"))
        self.assertNotIn("<img", html)
        self.assertEqual(html.count("&lt;img"), 4)
        self.assertIn('data-schedule-date="2026-04-07"', html)

    def test_rejects_bad_input_and_style_injection(self):
        with self.assertRaisesRegex(ValueError, "повтор"):
            structured_days_to_blocks([{"date": "2026-04-07", "description": [], "services": []}] * 2, 2026, 4)
        with self.assertRaisesRegex(ValueError, "вне месяца"):
            structured_days_to_blocks([{"date": "2026-05-01", "description": [], "services": []}], 2026, 4)
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "settings.json"
            data = load_settings(ROOT / "settings.json")
            data["font_family"] = "Arial; body {display:none}"
            path.write_text(json.dumps(data), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "font_family"):
                load_settings(path)


if __name__ == "__main__":
    unittest.main()


class InputContractTests(unittest.TestCase):
    def test_schema_matches_examples_and_raw_text(self):
        schema = json.loads((ROOT / "schema/month.schema.json").read_text(encoding="utf-8"))
        self.assertEqual(schema["$schema"], "https://json-schema.org/draft/2020-12/schema")
        self.assertFalse(schema["additionalProperties"])
        self.assertEqual(set(schema["required"]), {"year", "month", "language", "days"})
        for lang in ("ru", "en"):
            raw = (ROOT / "examples" / f"raw_{lang}.txt").read_text(encoding="utf-8")
            payload = json.loads((ROOT / "examples" / f"month_{lang}.json").read_text(encoding="utf-8"))
            for day in payload["days"]:
                for line in day["description"]:
                    self.assertIn(line, raw)
                for service in day["services"]:
                    self.assertIn(service["time"], raw)
                    for field in ("title", "hours", "priest"):
                        if service[field]:
                            self.assertIn(service[field], raw)

    def test_error_identifies_day_field_and_repair(self):
        from generate import validate
        sample = json.loads((ROOT / "examples/month_ru.json").read_text(encoding="utf-8"))
        sample["days"][1]["services"][0]["time"] = "9 утра"
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "bad.json"
            path.write_text(json.dumps(sample, ensure_ascii=False), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, r"День 2 .*поле services\[1\]\.time:.*Как исправить"):
                validate(path, ROOT / "settings.json")
            path.write_text('{"year": 2026,', encoding="utf-8")
            with self.assertRaisesRegex(ValueError, r"строка 1, столбец .*Как исправить"):
                validate(path, ROOT / "settings.json")

    def test_check_mode_does_not_write_html(self):
        import subprocess
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory) / "should-not-exist.html"
            result = subprocess.run([sys.executable, str(ROOT / "src/generate.py"), "--check",
                                     str(ROOT / "examples/month_ru.json"), str(target)],
                                    capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("JSON проверен: дней 4", result.stdout)
            self.assertFalse(target.exists())
