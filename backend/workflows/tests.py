from django.test import TestCase

from .serializers import WorkflowItemSerializer


class WorkflowItemSerializerValidationTests(TestCase):
    def valid_data(self, **changes):
        data = {"title": "Write report", "description": "First draft", "status": "pending"}
        data.update(changes)
        return data

    def test_valid_item_is_accepted(self):
        serializer = WorkflowItemSerializer(data=self.valid_data())
        self.assertTrue(serializer.is_valid(), serializer.errors)

    def test_empty_title_is_rejected(self):
        serializer = WorkflowItemSerializer(data=self.valid_data(title="   "))
        self.assertFalse(serializer.is_valid())
        self.assertIn("title", serializer.errors)

    def test_too_short_title_is_rejected(self):
        serializer = WorkflowItemSerializer(data=self.valid_data(title="ab"))
        self.assertFalse(serializer.is_valid())
        self.assertIn("title", serializer.errors)

    def test_too_long_title_is_rejected(self):
        serializer = WorkflowItemSerializer(data=self.valid_data(title="a" * 101))
        self.assertFalse(serializer.is_valid())
        self.assertIn("title", serializer.errors)

    def test_invalid_status_is_rejected(self):
        serializer = WorkflowItemSerializer(data=self.valid_data(status="Done"))
        self.assertFalse(serializer.is_valid())
        self.assertIn("status", serializer.errors)