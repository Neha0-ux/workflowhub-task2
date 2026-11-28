from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase

from .models import WorkflowItem
from django.test import TestCase
from .serializers import WorkflowItemSerializer

User = get_user_model()


class AuthTests(APITestCase):
    def test_register_login_logout(self):
        response = self.client.post(
            "/api/auth/register/",
            {"username": "alice", "email": "alice@example.com", "password": "Str0ngPass!23"},
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertNotIn("password", response.data)

        response = self.client.post(
            "/api/auth/login/", {"username": "alice", "password": "Str0ngPass!23"}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        token = response.data["token"]

        self.client.credentials(HTTP_AUTHORIZATION=f"Token {token}")
        response = self.client.post("/api/auth/logout/")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        # The token was deleted, so it no longer works
        response = self.client.post("/api/auth/logout/")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_login_with_wrong_password_fails(self):
        User.objects.create_user(username="bob", password="Str0ngPass!23")
        response = self.client.post("/api/auth/login/", {"username": "bob", "password": "wrong"})
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_duplicate_username_rejected(self):
        User.objects.create_user(username="alice", password="Str0ngPass!23")
        response = self.client.post(
            "/api/auth/register/", {"username": "alice", "password": "Str0ngPass!23"}
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class WorkflowItemTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="alice", password="Str0ngPass!23")
        self.other = User.objects.create_user(username="bob", password="Str0ngPass!23")
        self.client.force_authenticate(self.user)

    def test_crud(self):
        response = self.client.post(
            "/api/workflows/", {"title": "Write report", "description": "Task 1"}
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["status"], "pending")
        item_id = response.data["id"]

        response = self.client.patch(f"/api/workflows/{item_id}/", {"status": "in_progress"})
        self.assertEqual(response.data["status"], "in_progress")

        response = self.client.put(
            f"/api/workflows/{item_id}/",
            {"title": "Write final report", "description": "Edited", "status": "completed"},
        )
        self.assertEqual(response.data["title"], "Write final report")

        response = self.client.get("/api/workflows/")
        self.assertEqual(len(response.data), 1)

        response = self.client.delete(f"/api/workflows/{item_id}/")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(WorkflowItem.objects.exists())

    def test_invalid_status_rejected(self):
        response = self.client.post("/api/workflows/", {"title": "Valid title", "status": "done"})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("status", response.data)
    def test_users_cannot_see_each_others_items(self):
        item = WorkflowItem.objects.create(owner=self.other, title="Bob's item")
        self.assertEqual(self.client.get("/api/workflows/").data, [])
        response = self.client.delete(f"/api/workflows/{item.id}/")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_filter_by_status(self):
        WorkflowItem.objects.create(owner=self.user, title="A", status="pending")
        WorkflowItem.objects.create(owner=self.user, title="B", status="completed")
        response = self.client.get("/api/workflows/?status=completed")
        self.assertEqual([i["title"] for i in response.data], ["B"])

        
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

    def test_title_below_minimum_is_rejected(self):
        serializer = WorkflowItemSerializer(data=self.valid_data(title="ab"))
        self.assertFalse(serializer.is_valid())
        self.assertIn("title", serializer.errors)

    def test_title_at_minimum_is_accepted(self):
        serializer = WorkflowItemSerializer(data=self.valid_data(title="abc"))
        self.assertTrue(serializer.is_valid(), serializer.errors)

    def test_title_at_maximum_is_accepted(self):
        serializer = WorkflowItemSerializer(data=self.valid_data(title="a" * 200))
        self.assertTrue(serializer.is_valid(), serializer.errors)

    def test_title_above_maximum_is_rejected(self):
        serializer = WorkflowItemSerializer(data=self.valid_data(title="a" * 201))
        self.assertFalse(serializer.is_valid())
        self.assertIn("title", serializer.errors)

    def test_description_at_limit_is_accepted(self):
        serializer = WorkflowItemSerializer(data=self.valid_data(description="a" * 500))
        self.assertTrue(serializer.is_valid(), serializer.errors)

    def test_description_over_limit_is_rejected(self):
        serializer = WorkflowItemSerializer(data=self.valid_data(description="a" * 501))
        self.assertFalse(serializer.is_valid())
        self.assertIn("description", serializer.errors)

    def test_invalid_status_uses_custom_message(self):
        serializer = WorkflowItemSerializer(data=self.valid_data(status="Done"))
        self.assertFalse(serializer.is_valid())
        self.assertEqual(
            str(serializer.errors["status"][0]),
            "Status must be one of: pending, in_progress, completed.",
        )


class WorkflowItemApiValidationTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="carol", password="Str0ngPass!23")
        self.client.force_authenticate(self.user)

    def test_short_title_returns_400(self):
        response = self.client.post("/api/workflows/", {"title": "ab"})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("title", response.data)

    def test_long_description_returns_400(self):
        response = self.client.post(
            "/api/workflows/", {"title": "Valid title", "description": "a" * 501}
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("description", response.data)

    def test_invalid_status_returns_clear_message(self):
        response = self.client.post("/api/workflows/", {"title": "Valid title", "status": "done"})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("Status must be one of", str(response.data["status"][0]))