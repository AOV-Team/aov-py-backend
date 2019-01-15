from backend.settings.settings import PROFILE_USER, PROFILE_PASSWORD
from django.core.management import BaseCommand
import datetime
import requests

from apps.account.models import User
from rest_framework.authtoken.models import Token
import sys

def run_all_profiles(url_base, parameters):
    """
        Method to run all the profiles in sequence

    :param url_base: Base url needed to make the request to the correct api
    :param parameters: String used to identify url parameter to specify whether to use full serialization, render only,
                        or details only.
    :return: No return
    """

    print("***CLASSIFICATION***")
    run_classification_profile(url_base, parameters)
    print('\n')
    print("***ALL_PHOTOS***")
    run_all_photos_profile(url_base, parameters)
    print('\n')
    print("***SINGLE_PHOTO***")
    run_single_photo_profile(url_base, parameters)
    print('\n')
    print("***USER_PHOTOS***")
    run_user_photos_profile(url_base, parameters)
    print('\n')
    print("***TOP_PHOTOS***")
    run_top_photos_profile(url_base, parameters)

def run_classification_profile(url_base, parameters):
    """
        Method to profile the /api/photo_classifications/<id>/photos endpoint

    :param url_base: Base url needed to make the request to the correct api
    :param parameters: String used to identify url parameter to specify whether to use full serialization, render only,
                        or details only.
    :return: No return value
    """
    start_time = datetime.datetime.now()

    # Set up the query parameter to specify the serialization required
    if parameters == "renders":
        q = "?data=renders"
    elif parameters == "details":
        q = "?data=details"
    else:
        q = ""

    # Gotta login
    print("Logging in...")
    login_response = requests.post(url_base + "/auth", data={"email": PROFILE_USER, "password": PROFILE_PASSWORD})
    if login_response.status_code == 201:
        auth_token = login_response.json()["token"]
        headers = {"authorization": "Token {}".format(auth_token)}
        print("Login complete!")

        print("Retrieving Photo Classifications...")
        classifications = requests.get(url_base + "/photo_classifications", headers=headers)
        if classifications.status_code == 200:
            print("Classifications data received!")

            print("Retrieving {} classification photos...".format(classifications.json()["results"][0]["name"]))
            photos = requests.get(
                url_base + "/logging/classification/{}{}".format(classifications.json()["results"][0]["id"], q),
                headers=headers)
            if photos.status_code == 200:
                print("{} Classification photos received!".format(classifications.json()["results"][0]["name"]))

                params = {
                    "user": PROFILE_USER,
                    "paths": ["/api/logging/classification/{}{}".format(classifications.json()["results"][0]["id"], q)],
                    "start_time": start_time.strftime("%Y-%m-%d")
                }
                # Retrieve the necessary data from the Profiling table
                profile_result = requests.get(url_base + "/utils/profiles",
                                              headers=headers, params=params)
                profile_result_data = profile_result.json()["results"]
                if len(profile_result_data) > 0:
                    profile_result_data = profile_result_data[0]

                    print("\n-----------RESULTS-----------")
                    print("View Class: ", profile_result_data["view"])
                    print("API Path: ", profile_result_data["path"])
                    print("Response Time (ms): ", profile_result_data["response_ms"])
                    print("-----------------------------\n")
                    print("Profiling Complete!")
                else:
                    print("\n-----------RESULTS-----------")
                    print(profile_result.json())
                    print("-----------------------------\n")
                    print("Profiling Complete!")

            else:
                print("Failed to retrieve {} Classification photos.".format(
                    classifications.json()["results"][0]["name"]))
                print("Profiling Failed.")
        else:
            print("Failed to retrieve Classifications. Bailing out!")
    else:
        print("Login Failed")

def run_user_photos_profile(url_base, parameters):
    """
        Method to profile the /api/users/<id>/photos endpoint

    :param url_base: Base url needed to make the request to the correct api
    :param parameters: String used to identify url parameter to specify whether to use full serialization, render only,
                        or details only.
    :return: No return value
    """
    start_time = datetime.datetime.now()

    # Set up the query parameter to specify the serialization required
    if parameters == "renders":
        q = "?data=renders"
    elif parameters == "details":
        q = "?data=details"
    else:
        q = ""

    # Gotta login
    print("Logging in...")
    login_response = requests.post(url_base + "/auth", data={"email": PROFILE_USER, "password": PROFILE_PASSWORD})
    if login_response.status_code == 201:
        auth_token = login_response.json()["token"]
        headers = {"authorization": "Token {}".format(auth_token)}
        print("Login complete!")

        print("Retrieving profile data...")
        me = requests.get(url_base + "/me", headers=headers)
        profile = requests.get(url_base + "/me/profile", headers=headers)
        if profile.status_code == 200 and me.status_code == 200:
            print("Profile data received!")

            print("Retrieving user Photos")
            user_photos = requests.get(url_base + "/logging/user_photos/{}{}".format(me.json()["id"], q), headers=headers)
            if user_photos.status_code == 200:
                print("User photos received!")
                params = {
                    "user": PROFILE_USER,
                    "paths": ["/api/logging/user_photos/{}".format(me.json()["id"])],
                    "start_time": start_time.strftime("%Y-%m-%d")
                }
                # Retrieve the necessary data from the Profiling table
                profile_result = requests.get(url_base + "/utils/profiles",
                                              headers=headers, params=params)
                profile_result_data = profile_result.json()["results"]
                if len(profile_result_data) > 0:
                    profile_result_data = profile_result_data[0]

                    print("\n-----------RESULTS-----------")
                    print("View Class: ", profile_result_data["view"])
                    print("API Path: ", profile_result_data["path"])
                    print("Response Time (ms): ", profile_result_data["response_ms"])
                    print("-----------------------------\n")
                    print("Profiling Complete!")
                else:
                    print("\n-----------RESULTS-----------")
                    print(profile_result.json())
                    print("-----------------------------\n")
                    print("Profiling Complete!")
            else:
                print("Failed to retrieve user photos.")
                print("Profiling Failed")
        else:
            print("Could not retrieve Profile.")
            print("Profiling Failed")

    else:
        print("Login Failed")

def run_all_photos_profile(url_base, parameters):
    """
        Method to profile the /api/photos endpoint

    :param url_base: Base url needed to make the request to the correct api
    :param parameters: String used to identify url parameter to specify whether to use full serialization, render only,
                        or details only.
    :return: No return value
    """
    start_time = datetime.datetime.now()

    # Set up the query parameter to specify the serialization required
    if parameters == "renders":
        q = "?data=renders"
    elif parameters == "details":
        q = "?data=details"
    else:
        q = ""

    # Gotta login
    print("Logging in...")
    login_response = requests.post(url_base + "/auth", data={"email": PROFILE_USER, "password": PROFILE_PASSWORD})
    if login_response.status_code == 201:
        auth_token = login_response.json()["token"]
        headers = {"authorization": "Token {}".format(auth_token)}
        print("Login complete!")

        print("Retrieving all photos")
        all_photos = requests.get(url_base + "/logging/all_photos{}".format(q), headers=headers)
        if all_photos.status_code == 200:
            print("All photos received!")

            params = {
                "user": PROFILE_USER,
                "paths": ["/api/logging/all_photos"],
                "start_time": start_time.strftime("%Y-%m-%d")
            }
            # Retrieve the necessary data from the Profiling table
            profile_result = requests.get(url_base + "/utils/profiles",
                                          headers=headers, params=params)
            profile_result_data = profile_result.json()["results"]
            if len(profile_result_data) > 0:
                profile_result_data = profile_result_data[0]

                print("\n-----------RESULTS-----------")
                print("View Class: ", profile_result_data["view"])
                print("API Path: ", profile_result_data["path"])
                print("Response Time (ms): ", profile_result_data["response_ms"])
                print("-----------------------------\n")
                print("Profiling Complete!")
            else:
                print("\n-----------RESULTS-----------")
                print(profile_result.json())
                print("-----------------------------\n")
                print("Profiling Complete!")
        else:
            print("Failed to retrieve photos.")
            print("Profiling Failed")

    else:
        print("Login Failed")

def run_single_photo_profile(url_base, parameters):
    """
        Method to profile the /api/photos/<id> endpoint

    :param url_base: Base url needed to make the request to the correct api
    :param parameters: String used to identify url parameter to specify whether to use full serialization, render only,
                        or details only.
    :return: No return value
    """
    start_time = datetime.datetime.now()

    # Set up the query parameter to specify the serialization required
    if parameters == "renders":
        q = "?data=renders"
    elif parameters == "details":
        q = "?data=details"
    else:
        q = ""

    # Gotta login
    print("Logging in...")
    login_response = requests.post(url_base + "/auth", data={"email": PROFILE_USER, "password": PROFILE_PASSWORD})
    if login_response.status_code == 201:
        auth_token = login_response.json()["token"]
        headers = {"authorization": "Token {}".format(auth_token)}
        print("Login complete!")

        print("Retrieving all photos")
        all_photos = requests.get(url_base + "/photos", headers=headers)
        if all_photos.status_code == 200:
            print("All photos received!")

            print("Retrieving photo #{}...".format(all_photos.json()["results"][0]["id"]))
            single_photo = requests.get(url_base + "/logging/single_photo/{}{}".format(
                all_photos.json()["results"][0]["id"], q), headers=headers)
            if single_photo.status_code == 200:
                print("Photo #{} data received!".format(all_photos.json()["results"][0]["id"]))

                params = {
                    "user": PROFILE_USER,
                    "paths": ["/api/logging/single_photo/{}{}".format(all_photos.json()["results"][0]["id"], q)],
                    "start_time": start_time.strftime("%Y-%m-%d")
                }
                # Retrieve the necessary data from the Profiling table
                profile_result = requests.get(url_base + "/utils/profiles",
                                              headers=headers, params=params)
                profile_result_data = profile_result.json()["results"]
                if len(profile_result_data) > 0:
                    profile_result_data = profile_result_data[0]
                    print("\n-----------RESULTS-----------")
                    print("View Class: ", profile_result_data["view"])
                    print("API Path: ", profile_result_data["path"])
                    print("Response Time (ms): ", profile_result_data["response_ms"])
                    print("-----------------------------\n")
                    print("Profiling Complete!")
                else:
                    print("\n-----------RESULTS-----------")
                    print(profile_result.json())
                    print("-----------------------------\n")
                    print("Profiling Complete!")
            else:
                print("Failed to retrieve photo #{}".format(all_photos.json()["results"][0]["id"]))
                print("Profiling Failed")
        else:
            print("Failed to retrieve photos.")
            print("Profiling Failed")

    else:
        print("Login Failed")

def run_top_photos_profile(url_base, parameters):
    """
        Method to profile the /api/photos/top endpoint

    :param url_base: Base url needed to make the request to the correct api
    :param parameters: String used to identify url parameter to specify whether to use full serialization, render only,
                        or details only.
    :return: No return value
    """
    start_time = datetime.datetime.now()

    # Set up the query parameter to specify the serialization required
    if parameters == "renders":
        q = "&data=renders"
    elif parameters == "details":
        q = "&data=details"
    else:
        q = ""

    # Gotta login
    print("Logging in...")
    login_response = requests.post(url_base + "/auth", data={"email": PROFILE_USER, "password": PROFILE_PASSWORD})
    if login_response.status_code == 201:
        auth_token = login_response.json()["token"]
        headers = {"authorization": "Token {}".format(auth_token)}
        print("Login complete!")

        print("Retrieving top photos")
        top_photos = requests.get(url_base + "/logging/top_photos?display_page=popular{}".format(q), headers=headers)
        if top_photos.status_code == 200:
            print("Top photos received!")

            params = {
                "user": PROFILE_USER,
                "paths": ["/api/logging/top_photos?display_page=popular{}".format(q)],
                "start_time": start_time.strftime("%Y-%m-%d")
            }
            # Retrieve the necessary data from the Profiling table
            profile_result = requests.get(url_base + "/utils/profiles",
                                          headers=headers, params=params)
            profile_result_data = profile_result.json()["results"]
            if len(profile_result_data) > 0:
                profile_result_data = profile_result_data[0]

                print("\n-----------RESULTS-----------")
                print("View Class: ", profile_result_data["view"])
                print("API Path: ", profile_result_data["path"])
                print("Response Time (ms): ", profile_result_data["response_ms"])
                print("-----------------------------\n")
                print("Profiling Complete!")
            else:
                print("\n-----------RESULTS-----------")
                print(profile_result.json())
                print("-----------------------------\n")
                print("Profiling Complete!")
        else:
            print("Failed to retrieve top photos.")
            print("Profiling Failed")

    else:
        print("Login Failed")


def run_sample_login(url_base, parameters):
    users = User.objects.exclude(email__contains="Anonymous")
    tokens = Token.objects.filter(user__in=users)
    count = 0
    for user_id, token in tokens.values_list("user", "key"):
        headers = {"authorization": "Token {}".format(token)}
        response = requests.post(url_base + "/api/{}/sample_login".format(user_id), headers=headers)
        if response.status_code == 200:
            count += 1
        sys.stdout.write("Sessions created: {}  \r".format(count))
        sys.stdout.flush()

## TODO Remove after conversation with Gumbo about supposed 500?
def run_update_profile(url_base, parameters):
    login_response = requests.post(url_base + "/auth", data={"email": PROFILE_USER, "password": PROFILE_PASSWORD})
    if login_response.status_code == 201:
        token = login_response.json()["token"]
        headers = {"authorization": "Token {}".format(token)}

        with open('apps/common/test/data/photos/avatar-min.png', 'rb') as image:
            payload = {
                'avatar': image
            }

            response = requests.patch(url_base + "/api/me", headers=headers, files=payload)
        print(response.status_code, response.__dict__)


class Command(BaseCommand):
    help = 'Make API requests to test profiling packages'

    def add_arguments(self, parser):
        parser.add_argument('-p',
                            action='store',
                            dest='profile',
                            default='all_photos',
                            help='Run a profile of the /api/photo_classifications/<id>/photos endpoint.')
        parser.add_argument('-s',
                            action='store',
                            dest='server',
                            default='local',
                            help='Specify server to profile "(local | staging | production)"')
        parser.add_argument('-a',
                            action='store_true',
                            dest='all',
                            help='Run all profiles')
        parser.add_argument('-P',
                            action='store',
                            dest='parameters',
                            default='both',
                            help='Optional argument for specifying renders|details|both arguments for retrieval of images.'
                                 'Default is both.')

    def handle(self, *args, **options):
        """
            Command to test profiling packages. Makes a series of API requests to simulate app functionality.

        :param args:
        :param options:
        :return:
        """

        base_url_lut = {
            "local": "http://localhost:8000/api",
            "staging": "https://staging.artofvisuals.com/api",
            "production": "https://data.artofvisuals.com/api"
        }

        profile_method_lut = {
            "classification": run_classification_profile,
            "user_photos": run_user_photos_profile,
            "all_photos": run_all_photos_profile,
            "single_photo": run_single_photo_profile,
            "top_photos": run_top_photos_profile,
            "login": run_sample_login,
            "me": run_update_profile
        }

        if options["all"]:
            run_all_profiles(base_url_lut[options["server"]], options["parameters"])

        elif options["profile"] in profile_method_lut:
            profile_method_lut[options["profile"]](base_url_lut[options["server"]], options["parameters"])
        else:
            print("{} profile not currently implemented.".format(options["profile"]))

