import random
from apps.discover import models as discover_models
from apps.photo.photo import Photo
from django.test import TestCase, override_settings
from rest_framework.test import APIClient

@override_settings(REMOTE_IMAGE_STORAGE=False)
class TestStateViewGET(TestCase):
    """
    Test class for the StateView
    """

    def setUp(self):
        with open("apps/common/test/data/photos/avatar.png", "rb") as icon:
            icon = Photo(icon).compress()
            for num in range(0, 5):
                state = discover_models.State.objects.get(id=random.randint(1, 49))
                state.display = True
                state.fun_fact_1 = "Blah"
                state.icon = icon
                state.video_url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
                state.save()

    def tearDown(self):
        for state in discover_models.State.objects.all().iterator():
            state.display = False
            state.fun_fact_1 = None
            state.icon = None
            state.video_url = None
            state.save()

    def test_state_view_get_successful(self):
        """
        Unit test to ensure that retrieval works as expected

        :return: None
        """

        client = APIClient()

        response = client.get("/api/aov-web/discover/states")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data["results"]), 5)
