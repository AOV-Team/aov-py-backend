from apps.account import models as account_models
from apps.photo import models as photo_models
from django.contrib.gis.geos import Point
import factory


class GearFactory(factory.DjangoModelFactory):
    class Meta:
        model = account_models.Gear


class PhotoClassificationFactory(factory.DjangoModelFactory):
    class Meta:
        model = photo_models.PhotoClassification

    name = 'Night'
    classification_type = 'category'


class UserFactory(factory.DjangoModelFactory):
    class Meta:
        model = account_models.User
        django_get_or_create = ("username",)

    email = 'mrtest@mypapaya.io'
    password = 'WhoAmI'
    username = 'aov1'
    location = "Boise"
    social_name = "@theaov"


class PhotoFactory(factory.DjangoModelFactory):
    class Meta:
        model = photo_models.Photo

    # image = Photo(open('apps/common/test/data/photos/photo1-min.jpg', 'rb'))
    # image__height = 100
    # image__width = 100
    coordinates = Point(-116, 43)
    user = UserFactory(username="aov1")

    @factory.post_generation
    def gear(self, create, extracted, **kwargs):
        if not create:
            # Simple build, do nothing.
            return

        if extracted:
            # A list of groups were passed in, use them
            for gear in extracted:
                self.gear.add(gear)

    @factory.post_generation
    def photo_feed(self, create, extracted, **kwargs):
        self.photo_feed.add(1)

    @factory.post_generation
    def category(self, create, extracted, **kwargs):
        self.category.add(PhotoClassificationFactory())
