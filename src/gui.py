"""Small offline desktop window for JSON → HTML, using the CLI renderer."""
from pathlib import Path
import sys

from generate import render_from_text

ROOT = Path(__file__).resolve().parents[1]


def main():
    import tkinter as tk
    from tkinter import filedialog, messagebox, scrolledtext

    window = tk.Tk()
    window.title("Расписание: JSON → HTML")
    window.geometry("760x600")
    window.minsize(560, 440)

    heading = tk.Frame(window, padx=18, pady=16)
    heading.pack(fill="x")
    tk.Label(heading, text="Создать HTML из JSON", font=("Arial", 18, "bold"), anchor="w").pack(fill="x")
    tk.Label(heading, text="Вставьте JSON из ответа нейросети или откройте сохранённый .json-файл.\nЗатем нажмите «Проверить и сохранить HTML». Всё работает локально.", justify="left", anchor="w").pack(fill="x", pady=(8, 0))

    last_html = {"value": ""}
    editor = scrolledtext.ScrolledText(window, wrap="none", undo=True, font=("Courier", 11))
    editor.pack(fill="both", expand=True, padx=18)

    def show_error(message):
        error_box.configure(state="normal")
        error_box.delete("1.0", "end")
        error_box.insert("1.0", message)
        error_box.configure(state="disabled")

    def load_file():
        path = filedialog.askopenfilename(title="Выберите JSON", filetypes=[("JSON", "*.json"), ("Все файлы", "*")])
        if not path:
            return
        try:
            data = Path(path).read_text(encoding="utf-8")
        except OSError as error:
            show_error(f"Не удалось открыть файл: {error}")
            return
        editor.delete("1.0", "end")
        editor.insert("1.0", data)
        show_error("")

    def paste_json():
        try:
            data = window.clipboard_get()
        except tk.TclError:
            show_error("Буфер обмена пуст. Скопируйте JSON из чата и попробуйте ещё раз.")
            return
        editor.delete("1.0", "end")
        editor.insert("1.0", data)
        show_error("")

    def save_html():
        raw = editor.get("1.0", "end-1c")
        if not raw.strip():
            show_error("JSON пуст. Вставьте ответ нейросети или откройте .json-файл.")
            return
        try:
            html, count = render_from_text(raw, ROOT / "settings.json")
        except (ValueError, TypeError, OSError) as error:
            show_error(str(error))
            return
        show_error("")
        path = filedialog.asksaveasfilename(title="Куда сохранить HTML", defaultextension=".html", initialfile="schedule.html", filetypes=[("HTML", "*.html")])
        if not path:
            return
        try:
            Path(path).write_text(html, encoding="utf-8")
        except OSError as error:
            show_error(f"Не удалось сохранить HTML: {error}")
            return
        last_html["value"] = html
        window.clipboard_clear()
        window.clipboard_append(html)
        messagebox.showinfo("Готово", f"HTML сохранён:\n{path}\nДней: {count}\n\nHTML также скопирован в буфер. Вставьте его в блок «Свой HTML» на сайте.")

    controls = tk.Frame(window, padx=18, pady=12)
    controls.pack(fill="x")
    tk.Button(controls, text="Вставить JSON из буфера", command=paste_json).pack(side="left", padx=(0, 8))
    tk.Button(controls, text="Открыть .json-файл", command=load_file).pack(side="left", padx=(0, 8))
    tk.Button(controls, text="Проверить и сохранить HTML", command=save_html).pack(side="right")

    def copy_html():
        if not last_html["value"]:
            show_error("Сначала создайте HTML из JSON.")
            return
        window.clipboard_clear()
        window.clipboard_append(last_html["value"])
        show_error("HTML скопирован. Вставьте его в блок «Свой HTML» на сайте.")
    tk.Button(window, text="Скопировать HTML для сайта", command=copy_html).pack(anchor="e", padx=18)

    tk.Label(window, text="Ошибка проверки (её можно скопировать и отправить нейросети):", anchor="w", padx=18).pack(fill="x")
    error_box = tk.Text(window, height=4, wrap="word", font=("Arial", 11), background="#fff5f5")
    error_box.pack(fill="x", padx=18, pady=(4, 8))
    error_box.configure(state="disabled")

    def copy_error():
        message = error_box.get("1.0", "end-1c")
        if message:
            window.clipboard_clear()
            window.clipboard_append(message)
    tk.Button(window, text="Скопировать ошибку", command=copy_error).pack(anchor="e", padx=18, pady=(0, 12))
    window.mainloop()


if __name__ == "__main__":
    sys.exit(main())
