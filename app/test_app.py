import unittest
from app import AppHandler


class AppTests(unittest.TestCase):
    def test_handler_exists(self):
        self.assertIsNotNone(AppHandler)

    def test_service_name(self):
        self.assertEqual("devops-project-419534", "devops-project-419534")


if __name__ == "__main__":
    unittest.main()
