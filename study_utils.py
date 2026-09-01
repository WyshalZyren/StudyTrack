def format_total_time(total_minutes):
    hours = total_minutes // 60
    minutes = total_minutes % 60

    if hours == 0:
        return f"{minutes} min"

    if minutes == 0:
        return f"{hours} hr"

    return f"{hours} hr {minutes} min"


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
        session.get("id", "")
    ).strip()

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


def session_matches_search(
    session,
    search_term,
):
    search_term = (
        search_term
        .strip()
        .lower()
    )

    if not search_term:
        return True

    searchable_values = [
        session.get("subject", ""),
        session.get("notes", ""),
        session.get("date", ""),
        session.get("time", ""),
        str(session.get("minutes", "")),
    ]

    combined_text = " ".join(
        str(value).lower()
        for value in searchable_values
    )

    return search_term in combined_text


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


def calculate_statistics(study_sessions):
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

    if not study_sessions:
        return {
            "total_sessions": 0,
            "total_minutes": 0,
            "top_subject": None,
        }

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

    return {
        "total_sessions": total_sessions,
        "total_minutes": total_minutes,
        "top_subject": top_subject,
    }