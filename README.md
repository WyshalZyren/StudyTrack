# StudyTrack

StudyTrack is a Python desktop application for recording and managing personal study sessions.

It allows users to track subjects, study duration, notes, and session history while automatically calculating basic study statistics.

## Features

* Built with Tkinter
* Add study sessions
* Record subject names
* Record study duration in minutes
* Add optional study notes
* Automatic date and time recording
* Persistent local data storage using JSON
* Study history table
* Delete selected sessions
* Clear all saved sessions
* Total study session count
* Total accumulated study time
* Most studied subject
* Input validation
* Local-only study data

## Study Statistics

StudyTrack automatically displays:

* Total number of study sessions
* Total study time
* Most studied subject

## Data Storage

Study sessions are stored locally in:

```text
study_data.json
```

The file is automatically created by StudyTrack when needed.

## Requirements

* Python 3
* Tkinter

## Running the Application

Open a terminal inside the project folder and run:

```bash
py studytrack.py
```

The StudyTrack desktop window will open.

## Adding a Study Session

Enter:

1. Subject
2. Number of minutes studied
3. Optional notes

Then click:

```text
Add Session
```

The session will automatically appear in the Study History table and be saved locally.

## Built With

* Python
* Tkinter
* JSON
* pathlib
* datetime
* uuid

## Privacy

StudyTrack stores study history locally on the user's computer.

The application does not upload study history to an external server.

## Future Improvements

Potential future improvements include:

* Search and filter study sessions
* Weekly and monthly study statistics
* Study charts and graphs
* Study goals
* Pomodoro timer
* Dark mode
* Export study history
* SQLite database support
* Windows executable packaging

## License

This project may be distributed under the MIT License.
