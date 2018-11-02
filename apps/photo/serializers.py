from apps.account import models as account_models
from apps.account.serializers import UserBasicSerializer, UserPublicSerializer
from apps.common.serializers import DateTimeFieldWithTZ, determine_render
from apps.photo import models
from django.contrib.contenttypes.models import ContentType
from django.db.models import Max
from rest_framework import serializers
from rest_framework.authentication import TokenAuthentication
import re


class GallerySerializer(serializers.ModelSerializer):
    """
        Serializer for GalleryModel instances

    :author: gallen
    """

    photo_count = serializers.SerializerMethodField()

    def get_photo_count(self, obj):
        return obj.photos.all().count()

    class Meta:
        model = models.Gallery
        fields = ["id", "name", "photo_count", "public"]
        read_only_fields = ["user"]


class PhotoClassificationSerializer(serializers.ModelSerializer):
    feed_id = serializers.SerializerMethodField()

    def get_feed_id(self, obj):
        if obj.photo_feed:
            return obj.photo_feed.id
        return None

    class Meta:
        model = models.PhotoClassification
        fields = ('id', 'name', 'classification_type', 'icon', 'category_image', 'feed_id')


class PhotoClassificationSearchSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.PhotoClassification
        fields = ('id', 'name', 'classification_type')


class PhotoCommentReplySerializer(serializers.ModelSerializer):
    """
        Serializer for Comment Replies

    """
    created_at = DateTimeFieldWithTZ()
    user = serializers.SerializerMethodField()

    def get_user(self, obj):
        """
        Get basic user details

        :param obj: Photo object
        :return: user info
        """
        user = obj.user

        if user:
            return UserPublicSerializer(obj.user).data

        return None

    class Meta:
        model = models.PhotoComment
        fields = ('id', 'comment', 'user', 'created_at',)
        read_only_fields = ('user',)


class PhotoCommentSerializer(serializers.ModelSerializer):
    """
        Serializer class for the PhotoSerializer class
    :author: gallen
    """
    created_at = DateTimeFieldWithTZ()
    replies = PhotoCommentReplySerializer(many=True)
    photo = serializers.CharField(source='photo.id', read_only=True)
    user = serializers.SerializerMethodField()
    mentions = serializers.SerializerMethodField()

    def get_mentions(self, obj):
        if obj.mentions:
            mentioned_users = account_models.User.objects.filter(username__in=obj.mentions)
            return UserPublicSerializer(mentioned_users, many=True).data
        return []

    def get_user(self, obj):
        """
        Get basic user details

        :param obj: Photo object
        :return: user info
        """
        user = obj.user

        if user:
            return UserPublicSerializer(obj.user).data

        return None

    class Meta:
        model = models.PhotoComment
        fields = ('id', 'comment', 'user', 'photo', 'created_at', 'replies', 'mentions')
        read_only_fields = ('user',)


class PhotoFeedSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.PhotoFeed
        fields = ('id', 'name')


class PhotoRenderSerializer(serializers.ModelSerializer):
    """
        Serializer used when only Renders are needed

    :author: gallen
    """
    image_blurred = serializers.ImageField(required=False)
    image_medium = serializers.ImageField(required=False)
    image_small = serializers.ImageField(required=False)
    image_small_2 = serializers.ImageField(required=False)
    image_tiny_246 = serializers.ImageField(required=False)
    image_tiny_272 = serializers.ImageField(required=False)

    @staticmethod
    def setup_eager_loading(queryset):
        return queryset

    class Meta:
        model = models.Photo
        fields = ('id', 'image', 'image_blurred', 'image_medium', 'image_small', 'image_small_2', 'image_tiny_246',
                  'image_tiny_272',)
        ordering_fields = ('id')
        ordering = ('-id',)
        read_only_fields = ('image_blurred', 'image_medium', 'image_small', 'image_small_2', 'image_tiny_246',
                            'image_tiny_272')


class PhotoDetailsSerializer(serializers.ModelSerializer):
    """
        Serializer to serialize all the metadata for a Photo

    :author: gallen
    """
    comments = serializers.SerializerMethodField()
    dimensions = serializers.SerializerMethodField()
    gear = serializers.PrimaryKeyRelatedField(many=True, queryset=account_models.Gear.objects.all(), required=False)
    geo_location = serializers.CharField(max_length=32, write_only=True, required=False)
    tag = serializers.SerializerMethodField()
    user_details = serializers.SerializerMethodField()
    user_starred = serializers.SerializerMethodField()
    user_voted = serializers.SerializerMethodField()
    votes_behind = serializers.SerializerMethodField()

    def get_comments(self, obj):
        """
            Get the number of comments currently on the photo

        :param obj: Photo object
        :return: Number of comments related to the photo
        """
        photo_comments = models.PhotoComment.objects.filter(photo=obj)
        return photo_comments.count()

    def get_dimensions(self, obj):
        """
        Get image dimensions

        :param obj: Photo object
        :return: dict containing image dimensions
        """
        return {'width': obj.image.width, 'height': obj.image.height}

    def get_tag(self, obj):
        """
            Returns a list of tag names

        :param obj: Photo object
        :return: List of Tag names
        """
        return list(obj.tag.values_list("name", flat=True))

    def get_user_details(self, obj):
        """
        Get basic user details

        :param obj: Photo object
        :return: user info
        """
        user = obj.user

        if user:
            return UserBasicSerializer(obj.user).data

        return None

    def get_user_starred(self, obj):
        """
            Check if there is a UserInterest with type of 'star' for the accessing user on this photo

        :param obj: Photo object
        :return: Dict denoting whether a star has occurred
        """

        authenticate = TokenAuthentication().authenticate(self.context["request"])
        if authenticate:
            user = authenticate[0]
        else:
            user = self.context["request"].user
        photo_type = ContentType.objects.get_for_model(obj)
        star_interest = account_models.UserInterest.objects.filter(interest_type='star', user=user,
                                                                   object_id=obj.id, content_type__pk=photo_type.id)
        return {
            "starred": star_interest.exists(),
        }

    def get_user_voted(self, obj):
        """
            Check if there is a PhotoVote object for the accessing user and set the necessary data

        :param obj: Photo obj
        :return: dict of data denoting type of vote a user gave
        """
        authenticate = TokenAuthentication().authenticate(self.context["request"])
        if authenticate:
            user = authenticate[0]
        else:
            user = self.context["request"].user
        photo_vote = models.PhotoVote.objects.filter(photo=obj, user=user)
        if photo_vote.exists():
            return {
                "voted": True,
                "type": "upvote" if photo_vote.first().upvote else "downvote"
            }

        return {
            "voted": photo_vote.exists(),
        }

    def get_votes_behind(self, obj):
        """
            Returns the difference between

        :param obj: Photo object
        :return: dict of the form - { "classification_name": number of votes behind top photo in category }
        """

        classifications = obj.category.all()
        votes_behind_dict = {}

        for classification_id, classification_name in classifications.values_list('id', 'name'):
            category_photos = models.Photo.objects.filter(category=classification_id)
            max_votes = category_photos.aggregate(Max('votes'))
            votes_behind_dict.update({
                classification_name: max_votes["votes__max"] - obj.votes
            })

        return votes_behind_dict

    @staticmethod
    def setup_eager_loading(queryset):
        queryset = queryset\
            .select_related("user")\
            .prefetch_related("category")\
            .prefetch_related("gear")\
            .prefetch_related("tag")

        return queryset

    class Meta:
        model = models.Photo
        fields = ("id", "category", "gear", "geo_location", "tag", "user", "attribution_name", "dimensions",
                  "latitude", "location", "longitude", "photo_data", "photo_feed",
                  "user_details", "magazine_authorized", "caption", "votes_behind", "comments", "votes", "user_voted",
                  "user_starred")
        ordering_fields = ("id", "location")
        ordering = ("-id",)
        read_only_fields = ("photo_data", "user_details", "comments", "user_voted", "user_starred")


class PhotoSerializer(serializers.ModelSerializer):
    """
        Full Serializer, mostly used for single object serializations and creations.

    """
    comments = serializers.SerializerMethodField()
    dimensions = serializers.SerializerMethodField()
    geo_location = serializers.CharField(max_length=32, write_only=True, required=False)
    image_blurred = serializers.ImageField(required=False)

    #TODO Remove the following block when optimizations are done on Frontend
    image_medium = serializers.ImageField(required=False)
    image_small = serializers.ImageField(required=False)
    image_small_2 = serializers.ImageField(required=False)
    image_tiny_246 = serializers.ImageField(required=False)
    image_tiny_272 = serializers.ImageField(required=False)

    rank = serializers.SerializerMethodField()
    scaled_render = serializers.SerializerMethodField()
    tag = serializers.SerializerMethodField()
    user_details = serializers.SerializerMethodField()
    user_starred = serializers.SerializerMethodField()
    user_voted = serializers.SerializerMethodField()
    votes_behind = serializers.SerializerMethodField()

    def get_comments(self, obj):
        """
            Get the number of comments currently on the photo

        :param obj: Photo object
        :return: Number of comments related to the photo
        """
        photo_comments = models.PhotoComment.objects.filter(photo=obj)
        return photo_comments.count()

    def get_dimensions(self, obj):
        """
        Get image dimensions

        :param obj: Photo object
        :return: dict containing image dimensions
        """
        return {'width': obj.image.width, 'height': obj.image.height}

    def get_scaled_render(self, obj):
        if "width" in self.context["request"].query_params and "height" in self.context["request"].query_params:
            render_string = determine_render(self.context)
            render_field = getattr(obj, render_string)
            return self.context["request"].build_absolute_uri(render_field.url)

        return ""

    def get_tag(self, obj):
        """
            Returns a list of tag names

        :param obj: Photo object
        :return: List of Tag names
        """
        return list(obj.tag.values("name", "id", "classification_type"))

    def get_user_details(self, obj):
        """
        Get basic user details

        :param obj: Photo object
        :return: user info
        """
        user = obj.user

        if user:
            return UserBasicSerializer(obj.user).data

        return None

    def get_user_starred(self, obj):
        """
            Check if there is a UserInterest with type of 'star' for the accessing user on this photo

        :param obj: Photo object
        :return: Dict denoting whether a star has occurred
        """

        authenticate = TokenAuthentication().authenticate(self.context["request"])
        if authenticate:
            user = authenticate[0]
        else:
            user = self.context["request"].user
        photo_type = ContentType.objects.get_for_model(obj)
        star_interest = account_models.UserInterest.objects.filter(interest_type='star', user=user,
                                                                   object_id=obj.id, content_type__pk=photo_type.id)
        return {
            "starred": star_interest.exists(),
        }

    def get_user_voted(self, obj):
        """
            Check if there is a PhotoVote object for the accessing user and set the necessary data

        :param obj: Photo obj
        :return: dict of data denoting type of vote a user gave
        """
        authenticate = TokenAuthentication().authenticate(self.context["request"])
        if authenticate:
            user = authenticate[0]
        else:
            user = self.context["request"].user

        # Put in a check to prevent the attempts of retrieving PhotoVote objects for the AnonymousUser object.
        if user.__string__() != "AnonymousUser":
            photo_vote = models.PhotoVote.objects.filter(photo=obj, user=user)
        else:
            photo_vote = models.PhotoVote.objects.none()
        if photo_vote.exists():
            return {
                "voted": True,
                "type": "upvote" if photo_vote.first().upvote else "downvote"
            }

        return {
            "voted": photo_vote.exists(),
        }

    def get_votes_behind(self, obj):
        """
            Returns the difference between

        :param obj: Photo object
        :return: dict of the form - { "classification_name": number of votes behind top photo in category }
        """

        classifications = obj.category.all()
        votes_behind_dict = {}

        for classification_id, classification_name in classifications.values_list('id', 'name'):
            category_photos = models.Photo.objects.filter(category=classification_id)
            max_votes = category_photos.aggregate(Max('votes'))
            votes_behind_dict.update({
                classification_name: max_votes["votes__max"] - obj.votes
            })

        return votes_behind_dict
    
    def get_rank(self, obj):
        classifications = obj.category.all()
        rank_dict = dict()
        photos = models.Photo.objects.all()
        count = 1
        for category_photo_id in photos.annotate(
                max_votes=Max('votes')).order_by("-max_votes").values_list("id", flat=True):
            if category_photo_id == obj.id:
                rank_dict.update({
                    "overall": count
                })
            else:
                count += 1

        for classification_id, classification_name in classifications.values_list('id', 'name'):
            category_photos = photos.filter(category=classification_id)
            count = 1
            for category_photo_id in category_photos.annotate(
                    max_votes=Max('votes')).order_by("-max_votes").values_list("id", flat=True):
                if category_photo_id == obj.id:
                    rank_dict.update({
                        classification_name: count
                    })
                else:
                    count += 1

        return rank_dict

    @staticmethod
    def setup_eager_loading(queryset):
        queryset = queryset\
            .select_related('user')\
            .prefetch_related('category')\
            .prefetch_related('gear')\
            .prefetch_related('tag')

        return queryset

    def validate_geo_location(self, value):
        """
        Check that coordinates are valid
        """
        if not re.match('^POINT\s\([\-\.\d]+\s[\-\.\d]+\)$', value):
            raise serializers.ValidationError('Geo location coordinates are invalid - expecting "POINT (long lat)"')
        return value

    class Meta:
        model = models.Photo
        fields = ("id", "category", "gear", "geo_location", "tag", "user", "attribution_name", "dimensions", "image",
                  "image_blurred", "image_medium", "image_small", "image_small_2", "image_tiny_246",
                  "image_tiny_272", "latitude", "location", "longitude", "photo_data", "original_image_url", "public",
                  "photo_feed", "user_details", "magazine_authorized", "caption", "votes_behind", "comments", "votes",
                  "user_voted", "user_starred", "bts_lens", "bts_shutter", "bts_iso", "bts_aperture",
                  "bts_camera_settings", "bts_time_of_day", "bts_camera_make", "bts_camera_model",
                  "bts_photo_editor", "scaled_render", "rank")
        extra_kwargs = {"original_image_url":  {"write_only": True},
                        "public": {"default": True, "write_only": True}}
        ordering_fields = ("id", "location")
        ordering = ("-id",)
        read_only_fields = ("image_blurred", "image_medium", "image_small", "image_small_2", "image_tiny_246",
                            "image_tiny_272", "scaled_render", "rank")