import unittest

from study_utils import (
    calculate_statistics,
    format_total_time,
    normalize_session,
    session_matches_date,
    session_matches_search,
)


class TestFormatTotalTime(unittest.TestCase):

    def test_minutes_only(self):
        self.assertEqual(
            format_total_time(45),
            "45 min",
        )

    def test_exact_hour(self):
        self.assertEqual(
            format_total_time(60),
            "1 hr",
        )

    def test_hours_and_minutes(self):
        self.assertEqual(
            format_total_time(90),
            "1 hr 30 min",
        )

    def test_zero_minutes(self):
        self.assertEqual(
            format_total_time(0),
            "0 min",
        )


class TestNormalizeSession(unittest.TestCase):

    def test_valid_session(self):
        session = {
            "id": "123",
            "subject": "Programming",
            "minutes": 60,
            "notes": "Python practice",
            "date": "2026-09-01",
            "time": "09:00 AM",
        }

        result = normalize_session(session)

        self.assertEqual(
            result["subject"],
            "Programming",
        )

        self.assertEqual(
            result["minutes"],
            60,
        )

    def test_negative_minutes_become_zero(self):
        session = {
            "subject": "Mathematics",
            "minutes": -20,
        }

        result = normalize_session(session)

        self.assertEqual(
            result["minutes"],
            0,
        )

    def test_invalid_minutes_become_zero(self):
        session = {
            "subject": "Science",
            "minutes": "hello",
        }

        result = normalize_session(session)

        self.assertEqual(
            result["minutes"],
            0,
        )

    def test_empty_subject_becomes_unknown(self):
        session = {
            "subject": "",
            "minutes": 30,
        }

        result = normalize_session(session)

        self.assertEqual(
            result["subject"],
            "Unknown",
        )

    def test_non_dictionary_returns_none(self):
        self.assertIsNone(
            normalize_session("invalid")
        )


class TestSessionSearch(unittest.TestCase):

    def setUp(self):
        self.session = {
            "subject": "Programming",
            "minutes": 60,
            "notes": "Practiced Python functions",
            "date": "2026-09-01",
            "time": "09:30 AM",
        }

    def test_search_by_subject(self):
        self.assertTrue(
            session_matches_search(
                self.session,
                "Programming",
            )
        )

    def test_search_is_case_insensitive(self):
        self.assertTrue(
            session_matches_search(
                self.session,
                "PROGRAMMING",
            )
        )

    def test_search_by_notes(self):
        self.assertTrue(
            session_matches_search(
                self.session,
                "Python",
            )
        )

    def test_search_by_minutes(self):
        self.assertTrue(
            session_matches_search(
                self.session,
                "60",
            )
        )

    def test_search_by_date(self):
        self.assertTrue(
            session_matches_search(
                self.session,
                "2026-09-01",
            )
        )

    def test_missing_search_term(self):
        self.assertFalse(
            session_matches_search(
                self.session,
                "Chemistry",
            )
        )

    def test_empty_search_matches(self):
        self.assertTrue(
            session_matches_search(
                self.session,
                "",
            )
        )


class TestDateFilter(unittest.TestCase):

    def setUp(self):
        self.session = {
            "date": "2026-09-01",
        }

    def test_all_dates_matches(self):
        self.assertTrue(
            session_matches_date(
                self.session,
                "All Dates",
            )
        )

    def test_matching_date(self):
        self.assertTrue(
            session_matches_date(
                self.session,
                "2026-09-01",
            )
        )

    def test_different_date(self):
        self.assertFalse(
            session_matches_date(
                self.session,
                "2026-08-31",
            )
        )


class TestStatistics(unittest.TestCase):

    def test_statistics(self):
        sessions = [
            {
                "subject": "Programming",
                "minutes": 60,
            },
            {
                "subject": "Mathematics",
                "minutes": 30,
            },
            {
                "subject": "Programming",
                "minutes": 45,
            },
        ]

        result = calculate_statistics(sessions)

        self.assertEqual(
            result["total_sessions"],
            3,
        )

        self.assertEqual(
            result["total_minutes"],
            135,
        )

        self.assertEqual(
            result["top_subject"],
            "Programming",
        )

    def test_empty_statistics(self):
        result = calculate_statistics([])

        self.assertEqual(
            result["total_sessions"],
            0,
        )

        self.assertEqual(
            result["total_minutes"],
            0,
        )

        self.assertIsNone(
            result["top_subject"]
        )


if __name__ == "__main__":
    unittest.main()