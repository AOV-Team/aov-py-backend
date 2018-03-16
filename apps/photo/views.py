from apps.account import models as account_models
from apps.account import serializers as account_serializers
from apps.common import models as common_models
from apps.common.serializers import setup_eager_loading
from apps.common.views import DefaultResultsSetPagination, get_default_response, handle_jquery_empty_array, \
    LargeResultsSetPagination, MediumResultsSetPagination, remove_pks_from_payload
from apps.communication.models import PushNotificationRecord
from apps.communication import tasks as communication_tasks
from apps.photo import models as photo_models
from apps.photo import serializers as photo_serializers
from apps.photo.photo import Photo
from apps.utils.models import UserAction
from apps.utils.serializers import UserActionSerializer
from datetime import datetime, timedelta
from django.conf import settings
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.contenttypes.models import ContentType
from django.contrib.gis.geos import Polygon
from django.core.exceptions import ObjectDoesNotExist
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Count, Q
from django.shortcuts import render
from django.utils import timezone
from push_notifications.apns import APNSServerError
from push_notifications.models import APNSDevice
from rest_framework import generics, permissions
from rest_framework.authentication import SessionAuthentication, TokenAuthentication
from rest_framework.exceptions import NotFound, PermissionDenied, ValidationError


@staff_member_required
def photo_admin(request):
    """
    View for /admin/photos/

    :param request: Request object
    :return: render()
    """
    category = request.GET.get('category')
    date = request.GET.get('date')
    feed = request.GET.get('feed')
    g = request.GET.get('g')
    i = request.GET.get('i')
    magazine = request.GET.get('magazine')
    q = request.GET.get('q')
    u = request.GET.get('u')

    # Default is none
    photos = photo_models.Photo.objects.none()

    if category:
        cat = photo_models.PhotoClassification.objects\
            .filter(classification_type='category', name__icontains=category).first()

        if cat:
            photos = photos | photo_models.Photo.objects.filter(category=cat)

    if date:
        dates = date.split(' - ')

        if len(dates) == 2:
            start = datetime.strptime(dates[0], '%Y-%m-%d')
            end = datetime.strptime(dates[1], '%Y-%m-%d') + timedelta(days=1)

            photos = photos | photo_models.Photo.objects.filter(created_at__gte=start, created_at__lte=end)

    if feed:
        if feed == "AOV Picks":
            feed = photo_models.PhotoFeed.objects.filter(name__icontains=feed)

            if feed:
                photos = photos | photo_models.Photo.objects.filter(
                    photo_feed=feed).distinct().order_by("-aov_feed_add_date")
        else:
            feed = photo_models.PhotoFeed.objects.filter(name__icontains=feed)

            if feed:
                photos = photos | photo_models.Photo.objects.filter(photo_feed=feed)

    if g:
        # Search gear
        gear = account_models.Gear.objects.filter(Q(item_make__icontains=g) | Q(item_model__icontains=g))

        for g in gear:
            photos = photos | photo_models.Photo.objects.filter(gear=g)

    if i:
        # ID
        photos = photo_models.Photo.objects.filter(pk=i)

    if magazine:
        photos = photo_models.Photo.objects.filter(magazine_authorized=magazine)

    if q or u:
        # Search for a tag
        if q:
            tag = photo_models.PhotoClassification.objects.filter(classification_type='tag', name__icontains=q).first()

            if tag:
                photos = photos | photo_models.Photo.objects.filter(Q(tag=tag) | Q(location__icontains=q))
            else:
                photos = photos | photo_models.Photo.objects.filter(location__icontains=q)

        # User search
        # Only active users
        if u:
            try:
                age = int(u)
            except ValueError:
                age = -1

            users = account_models.User.objects\
                .filter(Q(age=age) | Q(email__icontains=u) | Q(first_name__icontains=u) |
                        Q(last_name__icontains=u) | Q(location__icontains=u) | Q(username__icontains=u), is_active=True)

            for user in users:
                photos = photos | photo_models.Photo.objects.filter(user=user)

    # Default query
    if not category and not date and not feed and not g and not i and not q and not u and not magazine:
        # Build search attributes for photo
        search = {
            'public': True
        }

        photos = photo_models.Photo.objects.filter(**search)

    # Pagination
    photos = photos.filter(public=True).order_by('-id').distinct()
    paginator = Paginator(photos, 30)
    page = request.GET.get('page')

    try:
        photos = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        photos = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        photos = paginator.page(paginator.num_pages)

    # Add lists of names of feeds and tags that image is in
    # Also check if photo has been starred by user
    # Makes it easier to work with in the HTML template
    for photo in photos:
        if not getattr(photo, 'photo_feed_names', None):
            photo.photo_feed_names = list()

        if not getattr(photo, 'photo_tag_names', None):
            photo.photo_tag_names = list()

        for feed in photo.photo_feed.all():
            if feed.public:
                photo.photo_feed_names.append(feed.name)

        for tag in photo.tag.all():
            if tag.public:
                photo.photo_tag_names.append(tag.name)

        # Has user starred photo?
        photo_type = ContentType.objects.get_for_model(photo)
        interest = account_models.UserInterest.objects.filter(
            user=request.user, interest_type='star', content_type__pk=photo_type.id, object_id=photo.id).first()

        if interest:
            photo.starred = True
        else:
            photo.starred = False

    # Categories
    categories = photo_models.PhotoClassification.objects\
        .filter(classification_type='category', public=True).order_by('name')

    # Ensure we retain query string even when paginating
    get_copy = request.GET.copy()
    parameters = get_copy.pop('page', True) and get_copy.urlencode()

    context = {
        'categories': categories,
        'media_url': settings.MEDIA_URL,
        'parameters': parameters,
        'photo_feeds': photo_models.PhotoFeed.objects.filter(public=True),
        'photos': photos
    }

    return render(request, 'photos.html', context)


@staff_member_required
def photo_map_admin(request):
    """
    Map photos

    :param request:
    :return: render()
    """
    context = {}

    return render(request, 'photo_map.html', context)


class GalleryRetrieveViewSet(generics.ListAPIView):
    """
        View set to handle creation and  updating of a Gallery

    :author: gallen
    """
    authentication_classes = (SessionAuthentication, TokenAuthentication,)
    pagination_class = DefaultResultsSetPagination
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = photo_serializers.GallerySerializer
    queryset = photo_models.Gallery.objects.all()

    def get_queryset(self):
        """
            Return Galleries

        :return: QuerySet
        """
        authenticated_user = TokenAuthentication().authenticate(self.request)[0]
        user_id = self.kwargs.get("user_id")
        query_params = {
            "public": True
        }

        if user_id:
            gallery_user = account_models.User.objects.filter(id=user_id)
        else:
            gallery_user = authenticated_user
            query_params["public"] = False

        name = self.request.query_params.get("name")

        if name:
            query_params.update({
                "name__icontains": name
            })

        galleries = self.queryset.filter(user=gallery_user, **query_params)

        return galleries

    def post(self, request, **kwargs):
        """
            Method to create new Galleries

        :param request: HTTP Request object containing data to create a new Gallery
        :param kwargs: Additional Keyword arguments passed to the view from the url conf
        :return: HTTP Response confirming/denying creation of a new Gallery
        """
        authenticated_user = TokenAuthentication().authenticate(request)[0]
        request_data = request.data

        response = get_default_response('400')

        if "name" in request_data:
            new_gallery = photo_models.Gallery.objects.create_or_update(user=authenticated_user, **request_data)

            response = get_default_response('201')
            response.data = {
                "results": photo_serializers.GallerySerializer(new_gallery).data
            }

        return response

    def put(self, request, **kwargs):
        """
            Method to update Gallery entries

        :param request: HTTP Request containing the new data to be entered
        :param kwargs: Additional Keyword arguments passed to the view from the url conf
        :return: HTTP Response confirming/denying update
        """

        authenticated_user = TokenAuthentication().authenticate(request)[0]
        request_data = request.data
        gallery_id = kwargs.get("gallery_id")
        gallery = photo_models.Gallery.objects.filter(id=gallery_id)
        response = get_default_response('404')

        if gallery.exists():
            gallery = gallery.first()
            object_changed = False
            response = get_default_response('200')

            if "name" in request_data:
                gallery.name = request_data.get("name")
                object_changed = True

            if "photos" in request_data:
                gallery.photos.add(*request_data.get("photos"))
                object_changed = True

            if "public" in request_data:
                if any([gallery.user.email == authenticated_user.email,
                        authenticated_user.is_superuser, authenticated_user.is_staff]):
                    gallery.public = request_data.get("public")
                    object_changed = True

            if object_changed:
                gallery.save()
                response.data = {
                    "results": self.serializer_class(gallery).data
                }

        return response


class GalleryPhotoViewSet(generics.ListAPIView):
    """
        API view to return the photos for a specific Gallery

    """
    authentication_classes = (SessionAuthentication, TokenAuthentication,)
    pagination_class = DefaultResultsSetPagination
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = photo_serializers.PhotoSerializer
    queryset = photo_models.Photo.objects.all()

    def get_queryset(self):
        """
            Method to return a queryset of photos for a given Gallery

        :return: QuerySet of Photo
        """
        user_id = self.kwargs.get("user_id")
        gallery_id = self.kwargs.get("gallery_id")

        gallery = photo_models.Gallery.objects.filter(user_id=user_id, id=gallery_id)

        if gallery.exists():
            gallery = gallery.first()
            return gallery.photos.all()

        return photo_models.Photo.objects.none()


class PhotoViewSet(generics.ListCreateAPIView):
    authentication_classes = (SessionAuthentication, TokenAuthentication,)
    pagination_class = DefaultResultsSetPagination
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = photo_serializers.PhotoSerializer

    def get_queryset(self):
        """
        Return images

        :return: Queryset
        """
        classification_param = self.request.query_params.get('classification')
        geo_location = self.request.query_params.get('geo_location')
        location = self.request.query_params.get('location')
        query_params = {
            'public': True
        }

        if location:
            query_params['location__iexact'] = location

        # If searching by a box of coordinates
        # Format ?geo_location=SW LONG,SW LAT,NE LONG, NE LAT
        if geo_location:
            coordinates = tuple(geo_location.split(','))

            # Check that we have 4 coordinates
            # And each coordinate needs to be a number
            if len(coordinates) != 4:
                raise ValidationError('Expecting geo_location to have 4 coordinates: "SW LONG,SW LAT,NE LONG, NE LAT"')
            else:
                try:
                    for c in coordinates:
                        float(c)
                except ValueError:
                    raise ValidationError('Expecting number format for coordinates')

            rectangle = Polygon.from_bbox(coordinates)
            query_params['coordinates__contained'] = rectangle

        if classification_param:
            try:
                # If we get classification id, use it
                # Otherwise set to 0 (will not match anything)
                try:
                    classification_id_param = int(classification_param)
                except ValueError:
                    classification_id_param = 0

                # Match either by ID or name
                classification = photo_models.PhotoClassification.objects\
                    .get(Q(id=classification_id_param) | Q(name__iexact=classification_param))

                return photo_models.Photo.objects\
                    .filter(Q(category=classification) | Q(tag=classification), **query_params).order_by('-votes')
            except ObjectDoesNotExist:
                # Empty queryset
                return photo_models.Photo.objects.none()
        else:
            return photo_models.Photo.objects.filter(**query_params).order_by('-created_at')

    def post(self, request, *args, **kwargs):
        """
        Save photo

        :param request: Request object
        :param args:
        :param kwargs:
        :return: Response object
        """
        authenticated_user = TokenAuthentication().authenticate(request)[0]
        payload = request.data
        payload['user'] = authenticated_user.id

        # Image compression
        # Save original first
        if 'image' in payload:
            # Save original photo to media
            try:
                photo = Photo(payload['image'])
                remote_key = photo.save('u{}_{}_{}'
                                        .format(authenticated_user.id, common_models.get_date_stamp_str(), photo.name),
                                        custom_bucket=settings.STORAGE['IMAGES_ORIGINAL_BUCKET_NAME'])

                # Original image url
                payload['original_image_url'] = '{}{}'.format(settings.ORIGINAL_MEDIA_URL, remote_key)

                # Process image to save
                payload['image'] = photo.compress()
            except TypeError:
                raise ValidationError('Image is not of type image')

        serializer = photo_serializers.PhotoSerializer(data=payload, context={"request": request})

        if serializer.is_valid():
            serializer.save()

            response = get_default_response('200')
            response.data = serializer.data
        else:
            raise ValidationError(serializer.errors)

        return response


class PhotoAppTopPhotosViewSet(generics.ListAPIView):
    pagination_class = DefaultResultsSetPagination
    permission_classes = (permissions.AllowAny,)
    photo_feed = None
    serializer_class = photo_serializers.PhotoSerializer

    @setup_eager_loading
    def get_queryset(self):
        """
        Return list of photos for requested photo feed

        :return: Queryset
        """
        page = self.request.query_params.get("display_page", None)
        cutoff = timezone.now() - timedelta(days=30)

        if page == "picks":
            picks_feed = photo_models.PhotoFeed.objects.filter(name="AOV Picks")
            aov_picks = photo_models.Photo.objects.filter(
                photo_feed=picks_feed, public=True,
                aov_feed_add_date__isnull=False).distinct().order_by("-aov_feed_add_date")
            return aov_picks

        if page == "popular":
            cutoff = timezone.now() - timedelta(days=7)
            popular_photos = photo_models.Photo.objects.filter(
                created_at__gte=cutoff, public=True, category__isnull=False).distinct().annotate(
                actions=Count("user_action")).order_by("-actions")
            return popular_photos

        top_photos = photo_models.Photo.objects.filter(
            public=True, category__isnull=False, created_at__gte=cutoff).distinct().order_by("-votes")[:100]
        return top_photos


class PhotoClassificationViewSet(generics.ListCreateAPIView):
    permission_classes = (permissions.AllowAny,)
    pagination_class = MediumResultsSetPagination
    serializer_class = photo_serializers.PhotoClassificationSerializer

    def get_queryset(self):
        """
        Return classifications

        :return: Queryset
        """
        query_params = {
            'public': True
        }

        classification_type = self.request.query_params.get('classification', None)

        # Add classification if provided
        if classification_type:
            if classification_type == 'category' or classification_type == 'tag':
                query_params['classification_type'] = classification_type
            else:
                # HTTP 400
                raise ValidationError('Classification type "{}" not valid'.format(classification_type))

        return photo_models.PhotoClassification.objects.filter(
            **query_params).annotate(photo_count=Count("category", distinct=True)).order_by("-photo_count")

    def post(self, request, *args, **kwargs):
        """
        Create new classification

        :param request: Request object
        :param args:
        :param kwargs:
        :return: Response object
        """
        payload = request.data
        payload = remove_pks_from_payload('photo_classification', payload)

        # Have to be authenticated to POST
        if not TokenAuthentication().authenticate(request):
            return get_default_response('401')

        # Only tags are allowed
        if 'classification_type' in payload:
            if payload['classification_type'] == 'category':
                raise ValidationError('Cannot create a category')
        else:
            payload['classification_type'] = 'tag'

        # If trying to create private entry, deny
        if 'public' in payload:
            if not payload['public']:
                raise ValidationError('Cannot create private classification')

        serializer = photo_serializers.PhotoClassificationSerializer(data=payload)

        if serializer.is_valid():
            # If classification already exists, update.
            # Else save new
            try:
                classification = photo_models.PhotoClassification.objects.get(name__iexact=payload['name'],
                                                                              classification_type='tag')

                serializer.update(classification, serializer.validated_data)
            except ObjectDoesNotExist:
                serializer.save()

            response = get_default_response('200')
            response.data = serializer.data
            return response
        else:
            raise ValidationError(serializer.errors)


class PhotoClassificationPhotosViewSet(generics.ListAPIView):
    pagination_class = DefaultResultsSetPagination
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)
    serializer_class = photo_serializers.PhotoSerializer

    def get_queryset(self):
        """
        Return photos for a classification

        :return: Queryset
        """
        # Determine if the request is for the Featured tab or the Recent Tab
        display_tab = self.request.query_params.get("display_tab", None)
        order_by = "-votes"
        length = self.request.query_params.get("length", 100)
        if display_tab == "recent":
            order_by = "-created_at"
            length = None
        try:
            photo_classification_id = self.kwargs.get('photo_classification_id')
            classification = photo_models.PhotoClassification.objects.get(id=photo_classification_id)

            return photo_models.Photo.objects.filter(
                Q(category=classification) | Q(tag=classification), public=True).distinct().order_by(order_by)[:length]

        except ObjectDoesNotExist:
            raise NotFound


class PhotoFeedViewSet(generics.ListAPIView):
    permission_classes = (permissions.AllowAny,)
    queryset = photo_models.PhotoFeed.objects.filter(public=True)
    serializer_class = photo_serializers.PhotoFeedSerializer


class PhotoFeedPhotosViewSet(generics.ListAPIView):
    pagination_class = DefaultResultsSetPagination
    permission_classes = (permissions.AllowAny,)
    photo_feed = None
    serializer_class = photo_serializers.PhotoSerializer

    @setup_eager_loading
    def get_queryset(self):
        """
        Return list of photos for requested photo feed

        :return: Queryset
        """
        try:
            photo_feed_id = self.kwargs['photo_feed_id']
            self.photo_feed = photo_models.PhotoFeed.objects.get(id=photo_feed_id)
            queryset = photo_models.Photo.objects.filter(public=True, photo_feed=self.photo_feed).order_by('-votes')

            return queryset
        except ObjectDoesNotExist:
            raise NotFound


class PhotoSingleViewSet(generics.RetrieveDestroyAPIView, generics.UpdateAPIView):
    permission_classes = (permissions.AllowAny,)
    serializer_class = photo_serializers.PhotoSerializer

    @setup_eager_loading
    def get_queryset(self):
        return photo_models.Photo.objects.all()

    def delete(self, request, *args, **kwargs):
        """
        Delete a photo

        :param request: Request object
        :param args:
        :param kwargs:
        :return: Response object
        """
        photo_id = kwargs.get('pk')
        authenticate = TokenAuthentication().authenticate(request)

        # User needs to be authenticated
        if authenticate:
            authenticated_user = authenticate[0]
        else:
            return get_default_response('401')

        try:
            photo = photo_models.Photo.objects.get(id=photo_id, public=True)

            # Photo must belong to authenticated user
            if photo.user == authenticated_user:
                photo.public = False
                photo.save()

                response = get_default_response('200')
            else:
                raise PermissionDenied
        except ObjectDoesNotExist:
            raise NotFound

        return response

    def get(self, request, *args, **kwargs):
        """
        Get a photo

        :param request: Request object
        :return: Response object
        """
        photo_id = kwargs.get('pk')

        try:
            photo = photo_models.Photo.objects.get(id=photo_id, public=True)

            response = get_default_response('200')
            response.data = photo_serializers.PhotoSerializer(photo, context={"request": request}).data
        except ObjectDoesNotExist:
            raise NotFound

        return response

    def patch(self, request, *args, **kwargs):
        """
        Edit photo

        :param request: Request object
        :return: Response object
        """
        authenticate = TokenAuthentication().authenticate(request)

        # Check that user is authenticated
        if authenticate:
            user = authenticate[0]
        elif request.user.is_superuser:
            user = request.user
        else:
            return get_default_response('401')

        # Needs to be superuser
        if user.is_superuser:
            photo_id = kwargs.get('pk')
            payload = request.data
            payload = remove_pks_from_payload('photo', payload)
            payload = handle_jquery_empty_array('photo_feed', payload)
            payload = remove_pks_from_payload('user', payload)

            # Cannot change image
            if 'image' in payload:
                del payload['image']

            if 'magazine_authorized' in payload:
                payload['magazine_authorized'] = payload['magazine_authorized'][0] == 'true'

            try:
                photo = photo_models.Photo.objects.get(id=photo_id)
                serializer = photo_serializers.PhotoSerializer(
                    photo, data=payload, partial=True, context={"request": request})

                if serializer.is_valid():
                    serializer.save()

                    response = get_default_response('200')
                    response.data = serializer.data
                    return response
                else:
                    raise ValidationError(serializer.errors)
            except ObjectDoesNotExist:
                raise NotFound
        else:
            raise PermissionDenied


class PhotoSingleCaptionViewSet(generics.UpdateAPIView):
    authentication_classes = (SessionAuthentication, TokenAuthentication)
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = photo_serializers.PhotoSerializer

    def patch(self, request, **kwargs):
        """
            Allow user to submit their own caption

        :param request: Request object
        :param kwargs: Additional keyword arguments
        :return: Response object
        """
        photo_id = kwargs.get('pk')

        try:
            photo = photo_models.Photo.objects.get(id=photo_id)
            existing_caption = photo.caption
            new_caption = request.data.get('caption', existing_caption)
            payload = {
                'caption': new_caption
            }

            serializer = photo_serializers.PhotoSerializer(
                photo, data=payload, partial=True, context={"request": request})

            if serializer.is_valid():
                serializer.save()

                response = get_default_response('200')
                response.data = serializer.data
                return response
            else:
                raise ValidationError(serializer.errors)

        except ObjectDoesNotExist:
            raise NotFound


class PhotoSingleCommentViewSet(generics.ListCreateAPIView):
    """
        API view to retrieve and create comments for photos

    :author: gallen
    """

    authentication_classes = (SessionAuthentication, TokenAuthentication,)
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = photo_serializers.PhotoCommentSerializer

    def get_queryset(self):
        """
            Overriding get_queryset to return a specific QuerySet of comments for a given photo

        :return: Filtered QuerySet
        """
        try:
            photo_id = self.kwargs.get('pk', None)
            photo = photo_models.Photo.objects.get(id=photo_id)

            return photo_models.PhotoComment.objects.filter(photo=photo).order_by("-created_at")
        except ObjectDoesNotExist:
            raise NotFound

    def post(self, request, **kwargs):
        """
            POST method to create a new comment

        :param request: HTTP Request object
        :param kwargs: Additional keyword arguments passed via url
        :return: HTTP response object
        """

        auth_user = TokenAuthentication().authenticate(request)[0]

        photo_id = kwargs.get('pk', None)
        data = request.data
        comment = data.get('comment', None)

        photo = photo_models.Photo.objects.filter(id=photo_id)

        if photo.exists() and comment:
            serializer_payload = {
                "user_id": auth_user.id,
                "comment": comment,
                "photo_id": photo_id
            }

            new_comment = photo_models.PhotoComment.objects.create_or_update(**serializer_payload)

            # After creating the comment, send a push notification to the photo owner
            owning_user = account_models.User.objects.filter(id__in=photo.values_list("user", flat=True))
            owning_apns = APNSDevice.objects.filter(user=owning_user)

            message = "{} has commented on your artwork, {}.".format(auth_user.username, owning_user.first().username)

            # This check is here to make sure the record is only created for devices that we have. No APNS means no
            # permission for notifications on the device.
            if owning_apns.exists():
                if auth_user.username != owning_user.first().username:
                    # To ensure we have the most recent APNSDevice entry, get a QuerySet of only the first item
                    owning_apns = APNSDevice.objects.filter(id=owning_apns.first().id)

                    try:
                        communication_tasks.send_push_notification(message, owning_apns.values_list("id", flat=True))
                        # Create the record of the notification being sent
                        PushNotificationRecord.objects.create(message=message, receiver=owning_apns.first(), action="C",
                                                              content_object=photo.first(), sender=auth_user)
                    except APNSServerError:
                        pass

            serializer = photo_serializers.PhotoCommentSerializer(new_comment)
            response = get_default_response('201')
            response.data = serializer.data

        else:
            response = get_default_response('400')
            response.data["userMessage"] = "A comment string cannot be empty."
            response.data["message"] = "Missing required field 'comment' in request data."

        return response


class PhotoSingleFlagsViewSet(generics.CreateAPIView):
    authentication_classes = (SessionAuthentication, TokenAuthentication)
    permission_classes = (permissions.IsAuthenticated,)
    queryset = account_models.UserInterest.objects.all()
    serializer_class = UserActionSerializer

    def post(self, request, **kwargs):
        """
        Create a flag entry

        :param request: Request object
        :param kwargs:
        :return: Response object
        """
        authentication = TokenAuthentication().authenticate(request)
        authenticated_user = authentication[0] if authentication else request.user

        try:
            photo = photo_models.Photo.objects.get(id=kwargs.get('pk'))
            photo_content_type = ContentType.objects.get_for_model(photo)
            user_action = UserAction.objects.filter(user=authenticated_user, action='photo_flag',
                                                    content_type__pk=photo_content_type.id, object_id=photo.id).first()

            if user_action:
                return get_default_response('200')
            else:
                UserAction.objects.create(user=authenticated_user, action='photo_flag', content_object=photo)

                return get_default_response('201')
        except ObjectDoesNotExist:
            raise NotFound('Photo does not exist')


class PhotoSingleInterestsViewSet(generics.DestroyAPIView, generics.CreateAPIView):
    """
    /api/photos/{}/likes
    /api/photos/{}/stars
    """
    authentication_classes = (SessionAuthentication, TokenAuthentication)
    permission_classes = (permissions.IsAuthenticated,)
    queryset = account_models.UserInterest.objects.all()
    serializer_class = account_serializers.UserInterestSerializer

    def delete(self, request, **kwargs):
        """
        Delete photo star

        :param request: Request object
        :param kwargs:
        :return: Response object
        """
        authentication = TokenAuthentication().authenticate(request)
        authenticated_user = authentication[0] if authentication else request.user
        response = get_default_response('200')
        starred_photo_id = kwargs.get('pk')
        user_interest = kwargs.get('user_interest')

        if user_interest == 'stars' or user_interest == 'likes':
            user_interest = user_interest[:-1]
        else:
            raise NotFound('Invalid user interest')

        try:
            try:
                photo = photo_models.Photo.objects.get(id=starred_photo_id)
            except ObjectDoesNotExist:
                response = get_default_response('404')
                response.data['message'] = 'Photo does not exist'
                return response

            photo_type = ContentType.objects.get_for_model(photo)
            interest = account_models.UserInterest.objects.filter(user=authenticated_user, interest_type=user_interest,
                                                                  content_type__pk=photo_type.id,
                                                                  object_id=photo.id)

            interest.delete()
        except ObjectDoesNotExist:
            # Return 200 even if photo wasn't acted upon
            pass

        return response

    def post(self, request, **kwargs):
        """
        Star a photo

        :param request: Request object
        :param kwargs:
        :return: Response object
        """
        authentication = TokenAuthentication().authenticate(request)
        authenticated_user = authentication[0] if authentication else request.user
        photo_id = kwargs.get('pk')
        user_interest = kwargs.get('user_interest')

        if user_interest == 'stars' or user_interest == 'likes':
            user_interest = user_interest[:-1]
        else:
            raise NotFound('Invalid user interest')

        try:
            photo = photo_models.Photo.objects.get(id=photo_id)

            # Make sure there is no existing entry
            photo_type = ContentType.objects.get_for_model(photo)
            interest = account_models.UserInterest.objects \
                .filter(user=authenticated_user, interest_type=user_interest, content_type__pk=photo_type.id,
                        object_id=photo.id) \
                .first()

            if not interest:
                account_models.UserInterest.objects.create(content_object=photo,
                                                           user=authenticated_user, interest_type=user_interest)
                response = get_default_response('201')
            else:
                response = get_default_response('409')
        except ObjectDoesNotExist:
            response = get_default_response('404')
            response.data['message'] = 'User you attempted to star does not exist'

        return response


class PhotoSingleVotesViewSet(generics.UpdateAPIView):
    authentication_classes = (SessionAuthentication, TokenAuthentication)
    permission_classes = (permissions.IsAuthenticated,)
    queryset = photo_models.Photo.objects.all()
    serializer_class = photo_serializers.PhotoSerializer

    def patch(self, request, **kwargs):
        """
        Create a vote entry

        :param request: Request object
        :param kwargs: pk for the object being patched
        :return: Response object
        """

        try:
            data = request.data
            photo = photo_models.Photo.objects.get(id=kwargs.get('pk'))
            send_notification = False

            if "operation" not in data:
                response = get_default_response('400')
                return response

            payload = dict()
            new_photo_vote_data = {
                "user": TokenAuthentication().authenticate(request)[0],
                "photo": photo
            }

            if data["operation"] == "increment":
                payload = {
                    "votes": photo.votes + 1
                }
                new_photo_vote_data.update({
                    "upvote": True
                })
                send_notification = True

            if data["operation"] == "decrement":
                payload = {
                    "votes": photo.votes - 1
                }
                new_photo_vote_data.update({
                    "upvote": False
                })

            serializer = photo_serializers.PhotoSerializer(
                photo, data=payload, partial=True, context={"request": request})
            photo_models.PhotoVote.objects.create_or_update(**new_photo_vote_data)

            if serializer.is_valid():
                serializer.save()

                # Send a push notification ONLY for upvote, and keep a record of it
                if send_notification:
                    auth_user = TokenAuthentication().authenticate(request)[0]
                    owning_user = account_models.User.objects.filter(id=photo.user.id)
                    owning_apns = APNSDevice.objects.filter(user=owning_user)

                    message = "{} has upvoted your artwork, {}.".format(
                        auth_user.username, owning_user.first().username)

                    # This check is here to make sure the record is only created for devices that we have. No APNS means no
                    # permission for notifications on the device.
                    if owning_apns.exists():
                        # To ensure we have the most recent APNSDevice entry, get a QuerySet of only the first item
                        owning_apns = APNSDevice.objects.filter(id=owning_apns.first().id)

                        try:
                            communication_tasks.send_push_notification(message, owning_apns.values_list("id", flat=True))
                            # Create the record of the notification being sent
                            PushNotificationRecord.objects.create(message=message, receiver=owning_apns.first(), action="U",
                                                                  content_object=photo, sender=auth_user)
                        except APNSServerError:
                            pass

                response = get_default_response('200')
                response.data = serializer.data
                return response

        except ObjectDoesNotExist:
            raise NotFound('Photo does not exist')


class UserFollowingPhotoViewSet(generics.ListAPIView):
    """
        View to retrieve all photos for the users being followed by the requesting user

    :author: gallen
    """
    pagination_class = DefaultResultsSetPagination
    authentication_classes = (SessionAuthentication, TokenAuthentication)
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = photo_serializers.PhotoSerializer

    def get_queryset(self):
        """
           Get the photos for users that a user is following

        :return: Queryset
        """
        authentication = TokenAuthentication().authenticate(self.request)
        accessing_user = authentication[0] if authentication else self.request.user

        if accessing_user:
            # Gather the users he is following
            following = account_models.User.objects.filter(follower=accessing_user)
            following_photos = photo_models.Photo.objects.filter(user__in=following).order_by('-created_at')
            return following_photos

        else:
            raise NotFound('User does not exist')
