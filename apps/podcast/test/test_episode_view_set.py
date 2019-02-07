from apps.common.models import get_date_stamp_str
from apps.photo.photo import Photo
from apps.podcast import models as podcast_models
from apps.podcast.audio import Audio
from django.test import override_settings, TestCase
from rest_framework.test import APIClient
# from unittest import skip

import datetime


@override_settings(REMOTE_AUDIO_STORAGE=False, REMOTE_IMAGE_STORAGE=False)
class TestEpisodeViewSetGET(TestCase):
    """
    Test class for GET requests to EpisodeViewSet

    """

    def setUp(self):
        """
        Method to set up the Episodes for retrieval. All audio is stored locally for this test, to not rack up AWS bills

        :return: None
        """

        with open("apps/common/test/data/audio/musicbox.wav", "rb") as audio:
            audio_file = Audio(audio).save("PODCAST_{}_{}".format(get_date_stamp_str(), audio.name))
            for num in range(1, 11):
                archived = True if num == 10 else False
                podcast_models.Episode.objects.create(
                    audio=audio_file, episode_number=num, title="AoV Podcast {}".format(num),
                    participant_social="@wonderboyprince", description="lorem ipsum", quote="lorem ipsum",
                    player_title_display="Musicbox", player_subtitle_display="lorem ipsum", published=True,
                    archived=archived)

        with open("apps/common/test/data/photos/avatar.png", "rb") as image:
            for ep in podcast_models.Episode.objects.all().iterator():
                display_type = {
                    1: "EI",
                    2: "BI",
                    3: "RI",
                    4: "RI",
                    5: "RI",
                    6: "PI"
                }
                for val in range(1, 7):
                    image_file = Photo(image).compress()
                    podcast_models.PodcastImage.objects.create(
                        image=image_file, episode=ep, display_type=display_type[val])

    def tearDown(self):
        """
        Method to clean up test data to make a clean slate for each unit test

        :return: None
        """

        podcast_models.Episode.objects.all().delete()
        podcast_models.PodcastImage.objects.all().delete()

    def test_episode_view_set_no_archives(self):
        """
        Unit test to verify that only unarchived episodes return

        :return:
        """

        client = APIClient()

        response = client.get("/api/podcast/episodes")
        episodes = response.data["results"]

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(episodes), 9)

    def test_episode_view_set_only_published(self):
        """
        Unit test to verify that an episode without published=True and with archived=False will not return in the
        queryset

        :return: None
        """

        for altered_episode in podcast_models.Episode.objects.all().iterator():
            altered_episode.archived = False
            altered_episode.published = False
            altered_episode.save()

        client = APIClient()

        response = client.get("/api/podcast/episodes")
        episodes = response.data["results"]

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(episodes), 0)

    def test_episode_query_parameters(self):
        """
        Test that search parameters works properly

        :return: None
        """

        client = APIClient()

        # Filter by episode number
        response = client.get("/api/podcast/episodes?number=3")
        episodes = response.data["results"]

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(episodes), 1)

        # Filter by title
        response = client.get("/api/podcast/episodes?title=podcast")
        episodes = response.data["results"]

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(episodes), 9)

        # Filter by publish date, less than
        episode = podcast_models.Episode.objects.first()
        episode.published_date = datetime.datetime(2018, 2, 12)
        episode.save()
        response = client.get("/api/podcast/episodes?published_before=2019-02-07")
        episodes = response.data["results"]

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(episodes), 1)

        # Filter by publish date, greater than
        episode = podcast_models.Episode.objects.first()
        episode.published_date = datetime.datetime(2019, 3, 12)
        episode.save()
        response = client.get("/api/podcast/episodes?published_after=2019-03-01")
        episodes = response.data["results"]

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(episodes), 1)
