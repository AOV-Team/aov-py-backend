from apps.common.models import get_date_stamp_str
from apps.podcast.models import Episode
from apps.podcast.audio import Audio
from django.test import override_settings, TestCase


@override_settings(REMOTE_AUDIO_STORAGE=False)
class TestEpisodeModelSave(TestCase):
    """
    Test class to verify the overridden save method works correctly
    """

    def test_episode_model_save_published_date_set_with_published_flag(self):
        """
        Unit test to make sure setting published to True also adds a published_date

        :return: None
        """

        with open("apps/common/test/data/audio/musicbox.wav", "rb") as audio:
            audio_file = Audio(audio).save("PODCAST_{}_{}".format(get_date_stamp_str(), audio.name))
            ep = Episode.objects.create(
                audio=audio_file, episode_number=1, title="AoV Podcast 1",
                participant_social="@wonderboyprince", description="lorem ipsum", quote="lorem ipsum",
                player_title_display="Musicbox", player_subtitle_display="lorem ipsum")

            ep.published = True
            ep.save()

        # Retrieve the episode
        updated_episode = Episode.objects.get(episode_number=1)
        self.assertTrue(updated_episode.published)
        self.assertIsNotNone(updated_episode.published_date)

    def test_episode_model_save_published_date_persists_with_published_flag_toggle(self):
        """
        Unit test to verify the published date maintains even if published flag is toggled

        :return: None
        """

        with open("apps/common/test/data/audio/musicbox.wav", "rb") as audio:
            audio_file = Audio(audio).save("PODCAST_{}_{}".format(get_date_stamp_str(), audio.name))
            ep = Episode.objects.create(
                audio=audio_file, episode_number=1, title="AoV Podcast 1",
                participant_social="@wonderboyprince", description="lorem ipsum", quote="lorem ipsum",
                player_title_display="Musicbox", player_subtitle_display="lorem ipsum")

            # Set it true, setting the publish date
            ep.published = True
            ep.save()

        # Retrieve the episode
        updated_episode = Episode.objects.get(episode_number=1)
        publish_date = updated_episode.published_date

        # Toggle the flag, off then back on
        updated_episode.published = False
        updated_episode.save()
        updated_episode.published = True
        updated_episode.save()

        # Retrieve the toggled version
        toggled = Episode.objects.get(episode_number=1)
        self.assertTrue(updated_episode.published)
        self.assertIsNotNone(updated_episode.published_date)
        self.assertEqual(publish_date, toggled.published_date)
        
    def test_episode_model_save_archived_date_set_with_archived_flag(self):
        """
        Unit test to make sure setting published to True also adds a published_date

        :return: None
        """

        with open("apps/common/test/data/audio/musicbox.wav", "rb") as audio:
            audio_file = Audio(audio).save("PODCAST_{}_{}".format(get_date_stamp_str(), audio.name))
            ep = Episode.objects.create(
                audio=audio_file, episode_number=1, title="AoV Podcast 1",
                participant_social="@wonderboyprince", description="lorem ipsum", quote="lorem ipsum",
                player_title_display="Musicbox", player_subtitle_display="lorem ipsum")

            ep.archived = True
            ep.save()

        # Retrieve the episode
        updated_episode = Episode.objects.get(episode_number=1)
        self.assertTrue(updated_episode.archived)
        self.assertIsNotNone(updated_episode.archive_date)

    def test_episode_model_save_archived_date_persists_with_archived_flag_toggle(self):
        """
        Unit test to verify the published date maintains even if published flag is toggled

        :return: None
        """

        with open("apps/common/test/data/audio/musicbox.wav", "rb") as audio:
            audio_file = Audio(audio).save("PODCAST_{}_{}".format(get_date_stamp_str(), audio.name))
            ep = Episode.objects.create(
                audio=audio_file, episode_number=1, title="AoV Podcast 1",
                participant_social="@wonderboyprince", description="lorem ipsum", quote="lorem ipsum",
                player_title_display="Musicbox", player_subtitle_display="lorem ipsum")

            # Set it true, setting the publish date
            ep.archived = True
            ep.save()

        # Retrieve the episode
        updated_episode = Episode.objects.get(episode_number=1)
        archive_date = updated_episode.archive_date

        # Toggle the flag, off then back on
        updated_episode.archived = False
        updated_episode.save()
        updated_episode.archived = True
        updated_episode.save()

        # Retrieve the toggled version
        toggled = Episode.objects.get(episode_number=1)
        self.assertTrue(updated_episode.archived)
        self.assertIsNotNone(updated_episode.archive_date)
        self.assertEqual(archive_date, toggled.archive_date)
