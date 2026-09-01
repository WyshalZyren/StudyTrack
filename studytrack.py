import json
import tkinter as tk
from datetime import datetime
from pathlib import Path
from tkinter import messagebox, ttk
from uuid import uuid4


BASE_DIR = Path(__file__).resolve().parent
DATA_FILE = BASE_DIR / "study_data.json"

BACKGROUND = "#F4F7FB"
WHITE = "#FFFFFF"
NAVY = "#14213D"
NAVY_HOVER = "#243A5E"
TEXT = "#1F2937"
GRAY = "#667085"
BORDER = "#D6DCE5"
GREEN = "#188038"
RED = "#C62828"
BLUE = "#2563EB"
LIGHT_BUTTON = "#E8ECF2"
LIGHT_BUTTON_HOVER = "#D8DEE8"

study_sessions = []
editing_session_id = None


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
        session.get("id") or uuid4()
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
            f"StudyTrack could not load saved sessions.\n\n{error}",
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


def format_total_time(total_minutes):
    hours = total_minutes // 60
    minutes = total_minutes % 60

    if hours == 0:
        return f"{minutes} min"

    if minutes == 0:
        return f"{hours} hr"

    return f"{hours} hr {minutes} min"


def clear_inputs():
    global editing_session_id

    editing_session_id = None

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

    add_button.config(
        text="Add Session",
        command=add_session,
        bg=NAVY,
        activebackground=NAVY_HOVER,
    )

    cancel_edit_button.pack_forget()

    status_label.config(
        text="Ready",
        fg=GRAY,
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


def add_session():
    subject = subject_entry.get().strip()
    minutes_text = minutes_entry.get().strip()

    notes = (
        notes_text
        .get("1.0", "end-1c")
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

    update_date_filter()
    refresh_table()
    update_statistics()
    clear_inputs()

    status_label.config(
        text="Session saved successfully.",
        fg=GREEN,
    )


def get_selected_session():
    selected_items = session_table.selection()

    if not selected_items:
        messagebox.showwarning(
            "No Selection",
            "Please select a study session first.",
        )
        return None

    selected_item = selected_items[0]

    tags = session_table.item(
        selected_item,
        "tags",
    )

    if not tags:
        messagebox.showerror(
            "Selection Error",
            "Could not identify the selected session.",
        )
        return None

    session_id = tags[0]

    for session in study_sessions:
        if session.get("id") == session_id:
            return session

    messagebox.showerror(
        "Selection Error",
        "The selected session could not be found.",
    )

    return None


def edit_selected():
    global editing_session_id

    session = get_selected_session()

    if session is None:
        return

    editing_session_id = session.get("id")

    subject_entry.delete(
        0,
        tk.END,
    )

    subject_entry.insert(
        0,
        session.get("subject", ""),
    )

    minutes_entry.delete(
        0,
        tk.END,
    )

    minutes_entry.insert(
        0,
        str(session.get("minutes", "")),
    )

    notes_text.delete(
        "1.0",
        tk.END,
    )

    notes_text.insert(
        "1.0",
        session.get("notes", ""),
    )

    add_button.config(
        text="Save Changes",
        command=save_edited_session,
        bg=BLUE,
        activebackground="#1D4ED8",
    )

    cancel_edit_button.pack(
        side="left",
        padx=(0, 10),
    )

    status_label.config(
        text="Editing selected session.",
        fg=BLUE,
    )

    subject_entry.focus_set()


def save_edited_session():
    global editing_session_id

    if editing_session_id is None:
        return

    subject = subject_entry.get().strip()
    minutes_text = minutes_entry.get().strip()

    notes = (
        notes_text
        .get("1.0", "end-1c")
        .strip()
    )

    minutes = validate_session(
        subject,
        minutes_text,
    )

    if minutes is None:
        return

    selected_session = None

    for session in study_sessions:
        if session.get("id") == editing_session_id:
            selected_session = session
            break

    if selected_session is None:
        messagebox.showerror(
            "Edit Error",
            "The session being edited could not be found.",
        )

        clear_inputs()
        return

    old_subject = selected_session.get("subject")
    old_minutes = selected_session.get("minutes")
    old_notes = selected_session.get("notes")

    selected_session["subject"] = subject
    selected_session["minutes"] = minutes
    selected_session["notes"] = notes

    if not save_sessions():
        selected_session["subject"] = old_subject
        selected_session["minutes"] = old_minutes
        selected_session["notes"] = old_notes
        return

    update_date_filter()
    refresh_table()
    update_statistics()
    clear_inputs()

    status_label.config(
        text="Session updated successfully.",
        fg=GREEN,
    )


def cancel_edit():
    clear_inputs()

    status_label.config(
        text="Edit cancelled.",
        fg=GRAY,
    )


def delete_selected():
    session = get_selected_session()

    if session is None:
        return

    confirm = messagebox.askyesno(
        "Delete Session",
        "Are you sure you want to delete the selected session?",
    )

    if not confirm:
        return

    study_sessions.remove(session)

    save_sessions()
    update_date_filter()
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
    update_date_filter()
    refresh_table()
    update_statistics()
    clear_inputs()

    status_label.config(
        text="All study sessions cleared.",
        fg=RED,
    )


def session_matches_search(
    session,
    search_term,
):
    if not search_term:
        return True

    values = [
        session.get("subject", ""),
        session.get("notes", ""),
        session.get("date", ""),
        session.get("time", ""),
        str(session.get("minutes", "")),
    ]

    combined = " ".join(
        str(value).lower()
        for value in values
    )

    return search_term in combined


def session_matches_date(
    session,
    selected_date,
):
    if selected_date == "All Dates":
        return True

    return (
        session.get("date", "")
        == selected_date
    )


def refresh_table(event=None):
    for row in session_table.get_children():
        session_table.delete(row)

    search_term = (
        search_var
        .get()
        .strip()
        .lower()
    )

    selected_date = (
        date_filter_var
        .get()
        .strip()
    )

    matching_sessions = []

    for session in study_sessions:
        matches_search = session_matches_search(
            session,
            search_term,
        )

        matches_date = session_matches_date(
            session,
            selected_date,
        )

        if matches_search and matches_date:
            matching_sessions.append(session)

    for index, session in enumerate(
        matching_sessions,
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

    if (
        search_term
        or selected_date != "All Dates"
    ):
        search_count_label.config(
            text=(
                f"{len(matching_sessions)} "
                f"of {len(study_sessions)} session(s)"
            )
        )

    else:
        search_count_label.config(
            text=f"{len(study_sessions)} session(s)"
        )


def update_date_filter():
    dates = sorted(
        {
            session.get("date", "")
            for session in study_sessions
            if session.get("date", "")
        },
        reverse=True,
    )

    values = [
        "All Dates",
        *dates,
    ]

    current_value = (
        date_filter_var.get()
    )

    date_filter_combo[
        "values"
    ] = values

    if current_value not in values:
        date_filter_var.set(
            "All Dates"
        )


def clear_filters():
    search_var.set("")
    date_filter_var.set(
        "All Dates"
    )

    refresh_table()
    search_entry.focus_set()


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

    subject_totals = {}

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

        subject_totals[subject] = (
            subject_totals.get(
                subject,
                0,
            )
            + minutes
        )

    top_subject = max(
        subject_totals,
        key=subject_totals.get,
    )

    top_subject_value.config(
        text=top_subject
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


root = tk.Tk()

root.title("StudyTrack")
root.geometry("1100x830")
root.minsize(920, 700)
root.configure(bg=BACKGROUND)

header = tk.Frame(
    root,
    bg=NAVY,
    height=100,
)

header.pack(fill="x")
header.pack_propagate(False)

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

cancel_edit_button = tk.Button(
    button_frame,
    text="Cancel Edit",
    command=cancel_edit,
    font=(
        "Segoe UI",
        10,
    ),
    fg=TEXT,
    bg=LIGHT_BUTTON,
    activebackground=LIGHT_BUTTON_HOVER,
    relief="flat",
    padx=20,
    pady=8,
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

stats_frame = tk.Frame(
    main,
    bg=BACKGROUND,
)

stats_frame.pack(
    fill="x",
    pady=(18, 0),
)

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

edit_button = tk.Button(
    history_header,
    text="Edit Selected",
    command=edit_selected,
    font=(
        "Segoe UI",
        9,
        "bold",
    ),
    fg=WHITE,
    bg=BLUE,
    activebackground="#1D4ED8",
    activeforeground=WHITE,
    relief="flat",
    padx=15,
    pady=6,
)

edit_button.pack(
    side="right"
)

filter_frame = tk.Frame(
    history_card,
    bg=WHITE,
)

filter_frame.pack(
    fill="x",
    padx=20,
    pady=(0, 12),
)

search_label = tk.Label(
    filter_frame,
    text="Search",
    font=(
        "Segoe UI",
        9,
        "bold",
    ),
    fg=TEXT,
    bg=WHITE,
)

search_label.pack(
    side="left",
    padx=(0, 8),
)

search_var = tk.StringVar()

search_entry = tk.Entry(
    filter_frame,
    textvariable=search_var,
    width=28,
    font=(
        "Segoe UI",
        10,
    ),
    relief="solid",
    bd=1,
)

search_entry.pack(
    side="left",
    ipady=5,
)

date_filter_label = tk.Label(
    filter_frame,
    text="Date",
    font=(
        "Segoe UI",
        9,
        "bold",
    ),
    fg=TEXT,
    bg=WHITE,
)

date_filter_label.pack(
    side="left",
    padx=(15, 8),
)

date_filter_var = tk.StringVar(
    value="All Dates"
)

date_filter_combo = ttk.Combobox(
    filter_frame,
    textvariable=date_filter_var,
    state="readonly",
    width=15,
)

date_filter_combo.pack(
    side="left"
)

clear_filters_button = tk.Button(
    filter_frame,
    text="Clear Filters",
    command=clear_filters,
    font=(
        "Segoe UI",
        9,
    ),
    fg=TEXT,
    bg=LIGHT_BUTTON,
    activebackground=LIGHT_BUTTON_HOVER,
    relief="flat",
    padx=12,
    pady=5,
)

clear_filters_button.pack(
    side="left",
    padx=(10, 0),
)

search_count_label = tk.Label(
    filter_frame,
    text="0 session(s)",
    font=(
        "Segoe UI",
        9,
    ),
    fg=GRAY,
    bg=WHITE,
)

search_count_label.pack(
    side="right"
)

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

subject_entry.bind(
    "<Return>",
    lambda event: minutes_entry.focus_set(),
)

minutes_entry.bind(
    "<Return>",
    lambda event: notes_text.focus_set(),
)

search_var.trace_add(
    "write",
    lambda *args: refresh_table(),
)

date_filter_combo.bind(
    "<<ComboboxSelected>>",
    refresh_table,
)

session_table.bind(
    "<Double-1>",
    lambda event: edit_selected(),
)

load_sessions()
update_date_filter()
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