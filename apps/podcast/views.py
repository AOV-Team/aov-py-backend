from apps.common import models as common_models
from apps.common import views as common_views
from apps.common.exceptions import MissingRequiredFieldException
from apps.common.views import get_default_response
from apps.photo.photo import Photo
from apps.podcast import models as podcast_models
from apps.podcast import serializers as podcast_serializers
from apps.podcast.audio import Audio
from django.conf import settings
from rest_framework import generics, permissions
from rest_framework.exceptions import ValidationError


class GetFeaturedRequestView(generics.GenericAPIView):
    """
    /api/podcast/get_featured

    View to handle creation of new Get Featured requests from AOV Podcast site

    """
    permission_classes = (permissions.AllowAny,)
    serializer_class = podcast_serializers.GetFeaturedRequestSerializer

    @staticmethod
    def _verify_required_data(request):
        """
        Method to verify a Get Featured POST request prior to allowing any processing to happen

        :param request: Request to be verified
        :return: None
        """

        # Is the requester there
        expected_requester_fields = ["email", "full_name", "location"]
        for expected_requester_field in expected_requester_fields:
            if expected_requester_field not in request.data:
                raise MissingRequiredFieldException("Missing required field {}".format(expected_requester_field))

        # Is there at least one Camera provided?
        if "camera" in request.data:
            # Check length, as there can be more than one
            if not len(request.data.getlist("camera")) > 0:
                raise MissingRequiredFieldException("Missing required Camera entry.")
        else:
            MissingRequiredFieldException("Missing required field Camera")

    def get_queryset(self):
        return podcast_models.GetFeaturedRequest.objects.none()

    def post(self, request):
        """
            Method to process a POST request and create a new Get Featured Request entry

        :param request: HTTP Request object
            sample:
        :return: HTTP Response object
            sample:
        """
        response = get_default_response("400")
        try:
            self._verify_required_data(request)

        except MissingRequiredFieldException as exc:
            response.data["message"] = exc.__str__()
            return response

        # Now process the request since we've verified it's accurate
        requester_email = request.data.get("email")
        requester_full_name = request.data.get("full_name")
        requester_location = request.data.get("location")
        requester_instagram_handle = request.data.get("instagram_handle", None)

        requester = podcast_models.Requester.objects.create_or_update(
            email=requester_email, full_name=requester_full_name, location=requester_location,
            instagram_handle=requester_instagram_handle)

        if 'image' in request.data:
            # Save original photo to media
            try:
                photo = Photo(request.data['image'])
                photo.save('GET_FEATURED_{}_{}'.format(common_models.get_date_stamp_str(), photo.name),
                           custom_bucket=settings.STORAGE['IMAGES_ORIGINAL_BUCKET_NAME'])

                # Process image to save
                request.data["image"] = photo.compress()
            except TypeError:
                raise ValidationError('Image is not of type image')

        audio_url = None
        if 'audio_sample' in request.data:
            try:
                audio = Audio(request.data.get("audio_sample"))
                audio_url = audio.save('GET_FEATURED_AUDIO_{}_{}_{}'
                                        .format(requester.id, common_models.get_date_stamp_str(), audio.name),
                                        custom_bucket=settings.STORAGE['AUDIO_BUCKET_NAME'])
            except TypeError as exc:
                print(exc.__repr__())

        get_featured_request = podcast_models.GetFeaturedRequest.objects.create(
            requester_fk=requester, image=request.data.get("image", None), story=request.data.get("story", None),
            audio=audio_url)

        # Handle any Cameras submitted
        cameras = request.data.getlist("camera", [])

        for camera in cameras:
            podcast_models.Camera.objects.create_or_update(model=camera, get_featured_request_fk=get_featured_request)

        response = get_default_response("200")
        return response


class EpisodeViewSet(generics.ListCreateAPIView):
    """
    View Set to support creation and retrieval of Podcast Episodes

    """
    serializer_class = podcast_serializers.EpisodeSerializer
    permission_classes = (permissions.AllowAny,)
    pagination_class = common_views.DefaultResultsSetPagination

    @staticmethod
    def _filterify_query_params(params):
        """
        Method to convert simplified URL query parameters to their appropriate values to be unpacked in a .filter()
        call

        :param params: Query parameters passed in the request
        :return: Dictionary of the parameters that can be unpacked in QuerySet's .filter() method
        """
        filter_lookup = {
            "published_before": "published_date__lte",
            "published_after": "published_date__gte",
            "title": "title__icontains",
            "number": "episode_number"
        }

        filter_parameters = {}

        for key, value in params.items():
            filter_parameters.update({filter_lookup[key]: value})

        return filter_parameters

    def get_queryset(self):
        """
        Method to return the QuerySet of current Episodes. Only those that are not archived and are published will be
        returned

        :return: QuerySet of Episode Objects
        """

        # Allows for manipulation of the queryset for searching
        query_params = self.request.query_params
        filters = self._filterify_query_params(query_params)

        # Returns the un-archived, published Episodes from most recently published to first published
        queryset = podcast_models.Episode.objects.filter(
            published=True, **filters).exclude(archived=True).order_by("-published_date")

        return queryset
