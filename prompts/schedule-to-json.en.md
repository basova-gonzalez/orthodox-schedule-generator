# Help me create service schedule HTML for my website

I am not a programmer and do not know how to use a terminal. I will paste my schedule text below. Convert it to JSON for the generator and guide me step by step until I have the finished HTML. Speak English, use plain language, and explain what to click, what to copy, and what result to expect.

## Ask first

If I have not specified my system, first ask: “Are you using Mac or Windows?” Wait for my answer; do not infer my system from the schedule's language. If I have not downloaded and extracted the generator folder, help me do that. Do not invent a download link; ask for the link or archive I was given.

If the year, month, language, date, time, or the service a line belongs to is unclear, ask. Do not produce the final JSON until these ambiguities are resolved.

## Prepare the JSON

Do not invent anything. Do not add services, times, priests, or calendar descriptions. Preserve the text of saints and services as given; only fix spacing and technical line breaks. Do not translate the schedule. If you cannot tell whether a line describes a service or the day itself, ask. The generator handles calendar-based highlighting.

One file represents one month in one language. All fields are required; no extra fields are allowed. The full schema is in `schema/month.schema.json`; here is the brief contract:

```json
{
  "year": 2026,
  "month": 4,
  "language": "en",
  "days": [
    {
      "date": "2026-04-07",
      "description": ["Description of the day as given in the source"],
      "services": [
        {"time": "10:00", "title": "Service name", "hours": "", "priest": ""}
      ]
    }
  ]
}
```

`year` is an integer from 1900 to 2099; `month` is 1–12. `language` is a code from `settings.json` (`ru` and `en` are provided initially); for another language, help add a `title`, 12 `months` forms for month headings, 12 `day_months` forms for individual dates, and seven `weekdays` labels from Monday through Sunday to settings.json. For languages with grammatical cases, use the appropriate form: for example, Russian `months` uses “апрель” while `day_months` uses “апреля”. If the forms are identical, `day_months` may be omitted; the generator then uses `months`. `date` is a real civil date in `YYYY-MM-DD` format within the specified month; duplicates are forbidden. `description` is a list of strings; `services` is a list of services. `time` must be `HH:MM`; `title` must be a nonempty string. `hours` is the full line about church opening hours (for example, “Open from 16:30”), and `priest` is the full priest label (for example, “Priest: example”). Preserve these labels and prefixes as supplied. If the information is absent, use `""`. If it is unclear which service the hours or priest belong to, ask. A day without services may use `services: []`.

After clarification, provide the JSON in a separate copyable block. Do not put comments or instructions inside it. After the JSON, give the steps below **only for my system**. Do not expect me to understand code. If I get stuck, explain the next single step and wait for the result.

## Guide me from JSON to HTML

1. **Save the JSON.** Explain that I need the folder containing `src`, `settings.json`, and `README.md`. Save `schedule.json` alongside them, not inside `src`. Copy only the contents of the JSON block, without triple-backtick lines or explanations.
   - Mac: open TextEdit, create a document, choose “Format → Make Plain Text,” paste the JSON, and save it as `schedule.json` using UTF-8. Decline any offer to append `.txt`. If the file is already called `schedule.json.txt`, rename it in Finder and confirm the `.json` extension.
   - Windows: open Notepad, paste the JSON, choose “Save As,” select “All files,” enter `schedule.json`, and choose UTF-8 encoding. Make sure the file is not named `schedule.json.txt`; show extensions using “View → Show → File name extensions” in File Explorer.
2. **Open a terminal in the folder.** Explain that a terminal is a window for entering commands; paste one command at a time and press Enter.
   - Mac: open Terminal through Spotlight (Cmd+Space). Type `cd` followed by a space, drag the generator folder from Finder into the Terminal window, and press Enter. Then run `ls`: the list should include `src`, `settings.json`, and `schedule.json`.
   - Windows: open the generator folder in File Explorer, click the address bar, type `powershell`, and press Enter. Then run `dir`: the same files should be visible. Do not ask me to enter an invented absolute path.
3. **Check Python.** On Mac, give me `python3 --version`; on Windows, `py -3 --version`. Version 3.10 or later is required. If Windows cannot find `py`, try `python --version`; if that works, use `python` in both subsequent commands.
   - If a developer tools installation dialog appears on Mac, you can close it and install Python from [python.org](https://www.python.org/downloads/).
   - If Python is missing or older than 3.10, help me install a supported version from the official [python.org/downloads](https://www.python.org/downloads/) page. On Mac, open the downloaded `.pkg` and follow the installer. On Windows, follow the official installation page to install Python Install Manager and Python 3; if the manager has not installed an interpreter automatically, run `py install 3`. Do not suggest installing extra libraries; none are needed. If the installer looks different, clarify the next step from its message.
   - After installation, close and reopen the terminal **in the generator folder** and check the version again. Do not proceed until the command reports a suitable version. Ask me to paste any unexpected message into the chat.
4. **Validate and create the HTML.** Give me two commands in separate copyable blocks, with an explanation after each. Run the second only after the first succeeds.
   - Mac:
     `python3 src/generate.py --check schedule.json`
     then `python3 src/generate.py schedule.json schedule.html`.
   - Windows:
     `py -3 src/generate.py --check schedule.json`
     then `py -3 src/generate.py schedule.json schedule.html`.
     If the version check worked only with `python`, replace `py -3` with `python` in both commands.
   The program currently prints messages in Russian. Explain their meaning in English: the first command should print `JSON проверен: дней …` (“JSON validated: … days”); the second should print `Создано: schedule.html; дней: …` (“Created: schedule.html; … days”). The file appears alongside `schedule.json`. Do not promise English program output.
5. **Handle errors.** Ask me to copy the complete terminal message into this same chat, even if it is in Russian. Explain it in English. For a JSON error, provide the complete corrected JSON without losing the source text, ask me to replace the contents of `schedule.json`, and run `--check` again. Ask for missing information rather than guessing. If a file cannot be found, help check the folder and the `.json.txt` extension. Do not suggest disabling validation. Do not say that a file was created unless I received the success message.
6. **Paste HTML into the website.** Double-clicking `schedule.html` opens a browser preview for checking the appearance. The website needs the file's source code:
   - Mac: in Terminal, from the generator folder, run `pbcopy < schedule.html` to copy all the HTML, then paste it into the website's HTML field.
   - Windows: right-click `schedule.html`, choose “Open with → Notepad,” then press Ctrl+A and Ctrl+C; paste it into the website's HTML field.
   Mention Tilda T123, WordPress “Custom HTML,” or an equivalent block. Do not suggest copying the visible text from the browser preview. For a second language, repeat the workflow with separate JSON and HTML filenames so the first result is not overwritten.

Do not claim that you ran code or created a file: in this chat workflow, I run the commands and you guide me based on my replies.

## My schedule text

I will paste my schedule text after this prompt:
