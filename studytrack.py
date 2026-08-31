import json
import tkinter as tk
from datetime import datetime
from pathlib import Path
from tkinter import messagebox, ttk
from uuid import uuid4


# PATHS

BASE_DIR = Path(__file__).resolve().parent
DATA_FILE = BASE_DIR / "study_data.json"

# COLORS

BACKGROUND = "#F4F7FB"
WHITE = "#FFFFFF"

NAVY = "#14213D"
NAVY_HOVER = "#243A5E"

TEXT = "#1F2937"
GRAY = "#667085"
BORDER = "#D6DCE5"

GREEN = "#188038"
RED = "#C62828"

LIGHT_BUTTON = "#E8ECF2"
LIGHT_BUTTON_HOVER = "#D8DEE8"

# DATA

study_sessions = []


def create_empty_data_file():
    try:
        with open(DATA_FILE, "w", encoding="utf-8") as file:
            json.dump([], file, indent=4)

    except OSError as error:
        messagebox.showerror(
            "Data Error",
            f"Could not create the data file.\n\n{error}",
        )


def normalize_session(session):
    if not isinstance(session, dict):
        return None

    subject = str(
        session.get("subject", "Unknown")
    ).strip()

    notes = str(
        session.get("notes", "")
    ).strip()

    date = str(
        session.get("date", "")
    ).strip()

    time = str(
        session.get("time", "")
    ).strip()

    session_id = str(
        session.get("id", uuid4())
    )

    try:
        minutes = int(
            session.get("minutes", 0)
        )
    except (TypeError, ValueError):
        minutes = 0

    if not subject:
        subject = "Unknown"

    if minutes < 0:
        minutes = 0

    return {
        "id": session_id,
        "subject": subject,
        "minutes": minutes,
        "notes": notes,
        "date": date,
        "time": time,
    }


def load_sessions():
    global study_sessions

    if not DATA_FILE.exists():
        study_sessions = []
        create_empty_data_file()
        return

    try:
        with open(
            DATA_FILE,
            "r",
            encoding="utf-8",
        ) as file:
            data = json.load(file)

        if not isinstance(data, list):
            raise ValueError(
                "Saved data must contain a list of study sessions."
            )

        loaded_sessions = []

        for item in data:
            normalized = normalize_session(item)

            if normalized is not None:
                loaded_sessions.append(normalized)

        study_sessions = loaded_sessions

        # Save again so older data gets upgraded
        # with IDs and normalized fields.
        save_sessions(show_error=False)

    except json.JSONDecodeError:
        study_sessions = []

        messagebox.showwarning(
            "Invalid Data File",
            "StudyTrack found an invalid study_data.json file.\n\n"
            "The app will start with an empty study history.",
        )

    except (OSError, ValueError) as error:
        study_sessions = []

        messagebox.showwarning(
            "Data Loading Error",
            f"StudyTrack could not load the saved sessions.\n\n{error}",
        )


def save_sessions(show_error=True):
    try:
        with open(
            DATA_FILE,
            "w",
            encoding="utf-8",
        ) as file:
            json.dump(
                study_sessions,
                file,
                indent=4,
                ensure_ascii=False,
            )

        return True

    except OSError as error:
        if show_error:
            messagebox.showerror(
                "Save Error",
                f"StudyTrack could not save your data.\n\n{error}",
            )

        return False

# HELPERS

def format_total_time(total_minutes):
    hours = total_minutes // 60
    minutes = total_minutes % 60

    if hours == 0:
        return f"{minutes} min"

    if minutes == 0:
        return f"{hours} hr"

    return f"{hours} hr {minutes} min"


def clear_inputs():
    subject_entry.delete(
        0,
        tk.END,
    )

    minutes_entry.delete(
        0,
        tk.END,
    )

    notes_text.delete(
        "1.0",
        tk.END,
    )

    subject_entry.focus_set()


def validate_session(subject, minutes_text):
    if not subject:
        messagebox.showwarning(
            "Missing Subject",
            "Please enter a subject.",
        )

        return None

    if not minutes_text:
        messagebox.showwarning(
            "Missing Time",
            "Please enter the number of minutes studied.",
        )

        return None

    try:
        minutes = int(minutes_text)

    except ValueError:
        messagebox.showwarning(
            "Invalid Time",
            "Minutes must be a whole number.",
        )

        return None

    if minutes <= 0:
        messagebox.showwarning(
            "Invalid Time",
            "Minutes must be greater than zero.",
        )

        return None

    if minutes > 1440:
        messagebox.showwarning(
            "Invalid Time",
            "A study session cannot exceed 1,440 minutes.",
        )

        return None

    return minutes


# SESSION ACTIONS

def add_session():
    subject = (
        subject_entry
        .get()
        .strip()
    )

    minutes_text = (
        minutes_entry
        .get()
        .strip()
    )

    notes = (
        notes_text
        .get(
            "1.0",
            "end-1c",
        )
        .strip()
    )

    minutes = validate_session(
        subject,
        minutes_text,
    )

    if minutes is None:
        return

    now = datetime.now()

    session = {
        "id": str(uuid4()),
        "subject": subject,
        "minutes": minutes,
        "notes": notes,
        "date": now.strftime("%Y-%m-%d"),
        "time": now.strftime("%I:%M %p"),
    }

    study_sessions.append(session)

    if not save_sessions():
        study_sessions.pop()
        return

    refresh_table()
    update_statistics()
    clear_inputs()

    status_label.config(
        text="Session saved successfully.",
        fg=GREEN,
    )


def delete_selected():
    selected_items = session_table.selection()

    if not selected_items:
        messagebox.showwarning(
            "No Selection",
            "Please select a study session first.",
        )

        return

    selected_item = selected_items[0]

    session_id = session_table.item(
        selected_item,
        "tags",
    )

    if not session_id:
        return

    session_id = session_id[0]

    confirm = messagebox.askyesno(
        "Delete Session",
        "Are you sure you want to delete the selected session?",
    )

    if not confirm:
        return

    session_to_delete = None

    for session in study_sessions:
        if session.get("id") == session_id:
            session_to_delete = session
            break

    if session_to_delete is None:
        messagebox.showerror(
            "Delete Error",
            "The selected session could not be found.",
        )
        return

    study_sessions.remove(
        session_to_delete
    )

    save_sessions()
    refresh_table()
    update_statistics()

    status_label.config(
        text="Session deleted.",
        fg=RED,
    )


def clear_all_sessions():
    if not study_sessions:
        messagebox.showinfo(
            "No Sessions",
            "There are no study sessions to clear.",
        )

        return

    confirm = messagebox.askyesno(
        "Clear All Sessions",
        "This will permanently remove all saved study sessions.\n\n"
        "Do you want to continue?",
    )

    if not confirm:
        return

    study_sessions.clear()

    save_sessions()
    refresh_table()
    update_statistics()

    status_label.config(
        text="All study sessions cleared.",
        fg=RED,
    )

# TABLE


def refresh_table():
    for row in session_table.get_children():
        session_table.delete(row)

    for index, session in enumerate(
        study_sessions,
        start=1,
    ):
        session_table.insert(
            "",
            tk.END,
            values=(
                index,
                session.get("date", ""),
                session.get("time", ""),
                session.get("subject", ""),
                session.get("minutes", 0),
                session.get("notes", ""),
            ),
            tags=(
                session.get("id", ""),
            ),
        )


# STATISTICS


def update_statistics():
    total_sessions = len(
        study_sessions
    )

    total_minutes = sum(
        int(
            session.get(
                "minutes",
                0,
            )
        )
        for session in study_sessions
    )

    total_sessions_value.config(
        text=str(total_sessions)
    )

    total_time_value.config(
        text=format_total_time(
            total_minutes
        )
    )

    if not study_sessions:
        top_subject_value.config(
            text="--"
        )

        return

    subjects = {}

    for session in study_sessions:
        subject = session.get(
            "subject",
            "Unknown",
        )

        minutes = int(
            session.get(
                "minutes",
                0,
            )
        )

        subjects[subject] = (
            subjects.get(
                subject,
                0,
            )
            + minutes
        )

    top_subject = max(
        subjects,
        key=subjects.get,
    )

    top_subject_value.config(
        text=top_subject
    )


# WINDOW

root = tk.Tk()

root.title(
    "StudyTrack"
)

root.geometry(
    "1100x780"
)

root.minsize(
    920,
    680,
)

root.configure(
    bg=BACKGROUND
)

# HEADER


header = tk.Frame(
    root,
    bg=NAVY,
    height=100,
)

header.pack(
    fill="x"
)

header.pack_propagate(
    False
)


header_left = tk.Frame(
    header,
    bg=NAVY,
)

header_left.pack(
    side="left",
    padx=40,
    pady=18,
)


title_label = tk.Label(
    header_left,
    text="StudyTrack",
    font=(
        "Segoe UI",
        26,
        "bold",
    ),
    fg=WHITE,
    bg=NAVY,
)

title_label.pack(
    anchor="w"
)


subtitle_label = tk.Label(
    header_left,
    text="Personal Study Session Tracker",
    font=(
        "Segoe UI",
        10,
    ),
    fg="#CDD6E5",
    bg=NAVY,
)

subtitle_label.pack(
    anchor="w"
)

# MAIN


main = tk.Frame(
    root,
    bg=BACKGROUND,
)

main.pack(
    fill="both",
    expand=True,
    padx=35,
    pady=25,
)

# INPUT CARD

input_card = tk.Frame(
    main,
    bg=WHITE,
    highlightbackground=BORDER,
    highlightthickness=1,
)

input_card.pack(
    fill="x"
)


input_content = tk.Frame(
    input_card,
    bg=WHITE,
)

input_content.pack(
    fill="x",
    padx=25,
    pady=20,
)


input_title = tk.Label(
    input_content,
    text="Add Study Session",
    font=(
        "Segoe UI",
        16,
        "bold",
    ),
    fg=TEXT,
    bg=WHITE,
)

input_title.pack(
    anchor="w",
    pady=(0, 15),
)


fields_frame = tk.Frame(
    input_content,
    bg=WHITE,
)

fields_frame.pack(
    fill="x"
)

# SUBJECT

subject_frame = tk.Frame(
    fields_frame,
    bg=WHITE,
)

subject_frame.pack(
    side="left",
    fill="x",
    expand=True,
    padx=(0, 10),
)


subject_label = tk.Label(
    subject_frame,
    text="Subject",
    font=(
        "Segoe UI",
        10,
        "bold",
    ),
    fg=TEXT,
    bg=WHITE,
)

subject_label.pack(
    anchor="w"
)


subject_entry = tk.Entry(
    subject_frame,
    font=(
        "Segoe UI",
        11,
    ),
    relief="solid",
    bd=1,
)

subject_entry.pack(
    fill="x",
    ipady=7,
    pady=(6, 0),
)

# MINUTES

minutes_frame = tk.Frame(
    fields_frame,
    bg=WHITE,
)

minutes_frame.pack(
    side="left",
    padx=(10, 0),
)


minutes_label = tk.Label(
    minutes_frame,
    text="Minutes",
    font=(
        "Segoe UI",
        10,
        "bold",
    ),
    fg=TEXT,
    bg=WHITE,
)

minutes_label.pack(
    anchor="w"
)


minutes_entry = tk.Entry(
    minutes_frame,
    width=15,
    font=(
        "Segoe UI",
        11,
    ),
    relief="solid",
    bd=1,
)

minutes_entry.pack(
    ipady=7,
    pady=(6, 0),
)

# NOTES


notes_label = tk.Label(
    input_content,
    text="Notes",
    font=(
        "Segoe UI",
        10,
        "bold",
    ),
    fg=TEXT,
    bg=WHITE,
)

notes_label.pack(
    anchor="w",
    pady=(15, 6),
)


notes_text = tk.Text(
    input_content,
    height=3,
    font=(
        "Segoe UI",
        10,
    ),
    wrap="word",
    relief="solid",
    bd=1,
    padx=8,
    pady=8,
)

notes_text.pack(
    fill="x"
)

# BUTTONS


button_frame = tk.Frame(
    input_content,
    bg=WHITE,
)

button_frame.pack(
    fill="x",
    pady=(15, 0),
)


add_button = tk.Button(
    button_frame,
    text="Add Session",
    command=add_session,
    font=(
        "Segoe UI",
        10,
        "bold",
    ),
    fg=WHITE,
    bg=NAVY,
    activebackground=NAVY_HOVER,
    activeforeground=WHITE,
    relief="flat",
    padx=24,
    pady=8,
)

add_button.pack(
    side="left"
)


clear_button = tk.Button(
    button_frame,
    text="Clear Input",
    command=clear_inputs,
    font=(
        "Segoe UI",
        10,
    ),
    fg=TEXT,
    bg=LIGHT_BUTTON,
    activebackground=LIGHT_BUTTON_HOVER,
    relief="flat",
    padx=24,
    pady=8,
)

clear_button.pack(
    side="left",
    padx=10,
)


status_label = tk.Label(
    button_frame,
    text="Ready",
    font=(
        "Segoe UI",
        9,
    ),
    fg=GRAY,
    bg=WHITE,
)

status_label.pack(
    side="right"
)

# STATISTICS

stats_frame = tk.Frame(
    main,
    bg=BACKGROUND,
)

stats_frame.pack(
    fill="x",
    pady=(18, 0),
)


def create_stat_card(parent, title):
    card = tk.Frame(
        parent,
        bg=WHITE,
        highlightbackground=BORDER,
        highlightthickness=1,
    )

    title_widget = tk.Label(
        card,
        text=title,
        font=(
            "Segoe UI",
            9,
        ),
        fg=GRAY,
        bg=WHITE,
    )

    title_widget.pack(
        pady=(13, 3)
    )

    value_widget = tk.Label(
        card,
        text="--",
        font=(
            "Segoe UI",
            17,
            "bold",
        ),
        fg=TEXT,
        bg=WHITE,
    )

    value_widget.pack(
        pady=(0, 13)
    )

    return card, value_widget


sessions_card, total_sessions_value = create_stat_card(
    stats_frame,
    "Total Sessions",
)

sessions_card.pack(
    side="left",
    fill="x",
    expand=True,
    padx=(0, 8),
)


time_card, total_time_value = create_stat_card(
    stats_frame,
    "Total Study Time",
)

time_card.pack(
    side="left",
    fill="x",
    expand=True,
    padx=8,
)


subject_card, top_subject_value = create_stat_card(
    stats_frame,
    "Most Studied Subject",
)

subject_card.pack(
    side="left",
    fill="x",
    expand=True,
    padx=(8, 0),
)

# HISTORY CARD

history_card = tk.Frame(
    main,
    bg=WHITE,
    highlightbackground=BORDER,
    highlightthickness=1,
)

history_card.pack(
    fill="both",
    expand=True,
    pady=(18, 0),
)


history_header = tk.Frame(
    history_card,
    bg=WHITE,
)

history_header.pack(
    fill="x",
    padx=20,
    pady=(15, 10),
)


history_title = tk.Label(
    history_header,
    text="Study History",
    font=(
        "Segoe UI",
        15,
        "bold",
    ),
    fg=TEXT,
    bg=WHITE,
)

history_title.pack(
    side="left"
)


clear_all_button = tk.Button(
    history_header,
    text="Clear All",
    command=clear_all_sessions,
    font=(
        "Segoe UI",
        9,
    ),
    fg=TEXT,
    bg=LIGHT_BUTTON,
    activebackground=LIGHT_BUTTON_HOVER,
    relief="flat",
    padx=15,
    pady=6,
)

clear_all_button.pack(
    side="right"
)


delete_button = tk.Button(
    history_header,
    text="Delete Selected",
    command=delete_selected,
    font=(
        "Segoe UI",
        9,
        "bold",
    ),
    fg=WHITE,
    bg=RED,
    activebackground="#A61F1F",
    activeforeground=WHITE,
    relief="flat",
    padx=15,
    pady=6,
)

delete_button.pack(
    side="right",
    padx=8,
)

# HISTORY TABLE

table_frame = tk.Frame(
    history_card,
    bg=WHITE,
)

table_frame.pack(
    fill="both",
    expand=True,
    padx=20,
    pady=(0, 18),
)


columns = (
    "number",
    "date",
    "time",
    "subject",
    "minutes",
    "notes",
)


session_table = ttk.Treeview(
    table_frame,
    columns=columns,
    show="headings",
    selectmode="browse",
)


headings = {
    "number": "#",
    "date": "Date",
    "time": "Time",
    "subject": "Subject",
    "minutes": "Minutes",
    "notes": "Notes",
}


for column, heading in headings.items():
    session_table.heading(
        column,
        text=heading,
    )


session_table.column(
    "number",
    width=45,
    anchor="center",
    stretch=False,
)

session_table.column(
    "date",
    width=110,
    anchor="center",
    stretch=False,
)

session_table.column(
    "time",
    width=110,
    anchor="center",
    stretch=False,
)

session_table.column(
    "subject",
    width=180,
    anchor="w",
)

session_table.column(
    "minutes",
    width=90,
    anchor="center",
    stretch=False,
)

session_table.column(
    "notes",
    width=350,
    anchor="w",
)


vertical_scrollbar = ttk.Scrollbar(
    table_frame,
    orient="vertical",
    command=session_table.yview,
)


horizontal_scrollbar = ttk.Scrollbar(
    table_frame,
    orient="horizontal",
    command=session_table.xview,
)


session_table.configure(
    yscrollcommand=vertical_scrollbar.set,
    xscrollcommand=horizontal_scrollbar.set,
)


vertical_scrollbar.pack(
    side="right",
    fill="y",
)


horizontal_scrollbar.pack(
    side="bottom",
    fill="x",
)


session_table.pack(
    side="left",
    fill="both",
    expand=True,
)

# FOOTER

footer = tk.Label(
    root,
    text="StudyTrack • Local Study Session Tracker",
    font=(
        "Segoe UI",
        8,
    ),
    fg=GRAY,
    bg=BACKGROUND,
)

footer.pack(
    pady=(0, 10)
)


# KEYBOARD SHORTCUTS

subject_entry.bind(
    "<Return>",
    lambda event: minutes_entry.focus_set(),
)


minutes_entry.bind(
    "<Return>",
    lambda event: notes_text.focus_set(),
)


# STARTUP

load_sessions()

refresh_table()

update_statistics()

if study_sessions:
    status_label.config(
        text=f"Loaded {len(study_sessions)} saved session(s).",
        fg=GREEN,
    )

else:
    status_label.config(
        text="No saved sessions yet.",
        fg=GRAY,
    )


subject_entry.focus_set()

root.mainloop()