from apps.common.exceptions import MissingRequiredFieldException
from apps.common.views import get_default_response, DefaultResultsSetPagination
from apps.discover import models as discover_models
from apps.discover import serializers as discover_serializers
from apps.photo.serializers import PhotoRenderSerializer, PhotoCustomRenderSerializer
from datetime import timedelta
from django.utils import timezone
from rest_framework import generics, permissions
from rest_framework.exceptions import ValidationError


class MobileAppTopPhotosView(generics.ListAPIView):
    """
    Endpoint to retrieve the top images from the Mobile app for display on the web
    """
    permission_classes = (permissions.AllowAny,)

    def get_serializer_class(self):
        """
        Determine which serializer class to use based on a combination of URL path and query parameters provided

        :return: Appropriate Photo serializer class
        """
        # Check if it's a custom render request
        if "width" in self.request.query_params and "height" in self.request.query_params:
            return PhotoCustomRenderSerializer
        else:
            return PhotoRenderSerializer

    def get_queryset(self):
        """
        Override of DRF method to specify custom QuerySet of Photo objects to be returned by the View

        :return: QuerySet of Photo objects
        """
        data = self.request.query_params.get("data", None)
        page = self.request.query_params.get("display_page", None)
        cutoff = timezone.now() - timedelta(days=30)

        if page == "aov-web-all":
            aov_web_images = photo_models.Photo.objects.filter(public=True, category__isnull=False).distinct().annotate(
                images_order=(Count("user_action") + (Count("photo_comment", distinct=True) * 5))
            ).order_by("-images_order")
            return aov_web_images

        if page == "aov-web-weekly":
            cutoff = timezone.now() - timedelta(days=7)
            aov_web_images = photo_models.Photo.objects.filter(public=True, category__isnull=False,
                                                               created_at__gte=cutoff).distinct().annotate(
                images_order=(Count("user_action") + (Count("photo_comment", distinct=True) * 5))
            ).order_by("-images_order")
            return aov_web_images


class DownloaderView(generics.CreateAPIView):
    """
    View to handle saving information for the users that request information download on a state

    /api/aov-web/discover/downloader
    """

    permission_classes = (permissions.AllowAny,)
    serializer_class = discover_serializers.DownloaderSerializer

    @staticmethod
    def _validate_request(request):
        expected_fields = ["name", "email", "location", "state_sponsor"]
        for expected in expected_fields:
            if expected not in request.data:
                raise MissingRequiredFieldException("Missing required field: {}".format(expected))

    def get_queryset(self):
        return discover_models.Downloader.objects.none()

    def post(self, request, *args, **kwargs):
        """
        Method to handle POST request

        :param request: Request object containing the data to be saved
        :param args: Arguments passed to the method from View decomposition
        :param kwargs: Keyword arguments passed to the method from the View decomposition
        :return: HTTP Response
        """

        response = get_default_response("400")
        # Validate the required data is present
        try:
            self._validate_request(request)
        except MissingRequiredFieldException as exc:
            response.data["message"] = exc.__str__()
            return response

        serialized = self.serializer_class(data=request.data)

        if serialized.is_valid():
            serialized.save()

            # Retrieve the downloadable file from the related sponsor, and return it in the response
            state_sponsor = discover_models.StateSponsor.objects.get(id=serialized.initial_data["state_sponsor"])
            serialized_file = discover_serializers.DownloadableFileOnlySerializer(state_sponsor.sponsor).data

            response = get_default_response("201")
            response.data = serialized_file

        else:
            raise ValidationError(serialized.errors)

        return response


class StateView(generics.ListAPIView):
    """
    Endpoint to retrieve all the States

    /api/aov-web/discover/states
    """

    permission_classes = (permissions.AllowAny,)
    serializer_class = discover_serializers.StateSerializer

    def get_queryset(self):
        return discover_models.State.objects.filter(display=True)


class StatePhotographerView(generics.ListAPIView):
    """
    Endpoint to retrieve StatePhotographers

    /api/aov-web/discover/states/<id>/photographers
    """
    permission_classes = (permissions.AllowAny,)
    serializer_class = discover_serializers.StatePhotographerSerializer

    def get_queryset(self):
        today = timezone.now()
        state = int(self.kwargs.get("pk"))
        if 1 <= state <= 50:
            return discover_models.StatePhotographer.objects.filter(state=state, feature_start__lte=today,
                                                                    feature_end__gte=today)
        else:
            return discover_models.StatePhotographer.objects.none()


class StateSponsorView(generics.ListAPIView):
    """
    Endpoint to retrieve StateSponsors

    /api/aov-web/discover/states/<id>/sponsors
    """
    permission_classes = (permissions.AllowAny,)
    serializer_class = discover_serializers.StateSponsorSerializer

    def get_queryset(self):
        today = timezone.now()
        state = int(self.kwargs.get("pk"))
        if 1 <= state <= 50:
            return discover_models.StateSponsor.objects.filter(state=state, sponsorship_start__lte=today,
                                                               sponsorship_end__gte=today)
        else:
            return discover_models.StateSponsor.objects.none()


class StatePhotoView(generics.ListAPIView):
    """
    Endpoint to retrieve StateSponsors

    /api/aov-web/discover/states/<id>/photos
    """
    permission_classes = (permissions.AllowAny,)
    serializer_class = discover_serializers.StatePhotoSerializer
    pagination_class = DefaultResultsSetPagination

    def get_queryset(self):
        state = int(self.kwargs.get("pk"))
        if 1 <= state <= 50:
            return discover_models.StatePhoto.objects.filter(state=state).order_by("-created_at")
        else:
            return discover_models.StatePhoto.objects.none()
