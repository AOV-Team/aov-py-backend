from backend.settings.settings import PROFILE_USER, PROFILE_PASSWORD
from django.core.management import BaseCommand
import datetime
import requests

def run_all_profiles(url_base):
    """
        Method to run all the profiles in sequence

    :param url_base: Base url needed to make the request to the correct api
    :return: No return
    """

    print("***CLASSIFICATION***")
    run_classification_profile(url_base)
    print('\n')
    print("***ALL_PHOTOS***")
    run_all_photos_profile(url_base)
    print('\n')
    print("***SINGLE_PHOTO***")
    run_single_photo_profile(url_base)
    print('\n')
    print("***USER_PHOTOS***")
    run_user_photos_profile(url_base)
    print('\n')
    print("***TOP_PHOTOS***")
    run_top_photos_profile(url_base)

def run_classification_profile(url_base):
    """
        Method to profile the /api/photo_classifications/<id>/photos endpoint

    :param url_base: Base url needed to make the request to the correct api
    :return: No return value
    """
    start_time = datetime.datetime.now()

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
                url_base + "/photo_classifications/{}/photos".format(classifications.json()["results"][0]["id"]),
                headers=headers)
            if photos.status_code == 200:
                print("{} Classification photos received!".format(classifications.json()["results"][0]["name"]))

                params = {
                    "user": PROFILE_USER,
                    "paths": ["/api/photo_classifications/{}/photos".format(
                        classifications.json()["results"][0]["id"])],
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

def run_user_photos_profile(url_base):
    """
        Method to profile the /api/users/<id>/photos endpoint

    :param url_base: Base url needed to make the request to the correct api
    :return: No return value
    """
    start_time = datetime.datetime.now()

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
            user_photos = requests.get(url_base + "/users/{}/photos".format(me.json()["id"]), headers=headers)
            if user_photos.status_code == 200:
                print("User photos received!")
                params = {
                    "user": PROFILE_USER,
                    "paths": ["/api/users/{}/photos".format(me.json()["id"])],
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

def run_all_photos_profile(url_base):
    """
        Method to profile the /api/photos endpoint

    :param url_base: Base url needed to make the request to the correct api
    :return: No return value
    """
    start_time = datetime.datetime.now()

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

            params = {
                "user": PROFILE_USER,
                "paths": ["/api/photos"],
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

def run_single_photo_profile(url_base):
    """
        Method to profile the /api/photos/<id> endpoint

    :param url_base: Base url needed to make the request to the correct api
    :return: No return value
    """
    start_time = datetime.datetime.now()

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
            single_photo = requests.get(url_base + "/photos/{}".format(all_photos.json()["results"][0]["id"]),
                                        headers=headers)
            if single_photo.status_code == 200:
                print("Photo #{} data received!".format(all_photos.json()["results"][0]["id"]))

                params = {
                    "user": PROFILE_USER,
                    "paths": ["/api/photos/{}".format(all_photos.json()["results"][0]["id"])],
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

def run_top_photos_profile(url_base):
    """
        Method to profile the /api/photos/top endpoint

    :param url_base: Base url needed to make the request to the correct api
    :return: No return value
    """
    start_time = datetime.datetime.now()

    # Gotta login
    print("Logging in...")
    login_response = requests.post(url_base + "/auth", data={"email": PROFILE_USER, "password": PROFILE_PASSWORD})
    if login_response.status_code == 201:
        auth_token = login_response.json()["token"]
        headers = {"authorization": "Token {}".format(auth_token)}
        print("Login complete!")

        print("Retrieving top photos")
        top_photos = requests.get(url_base + "/photos/top?display_page=popular", headers=headers)
        if top_photos.status_code == 200:
            print("Top photos received!")

            params = {
                "user": PROFILE_USER,
                "paths": ["/api/photos/top"],
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
            "top_photos": run_top_photos_profile

        }

        if options["all"]:
            run_all_profiles(base_url_lut[options["server"]])

        elif options["profile"] in profile_method_lut:
            profile_method_lut[options["profile"]](base_url_lut[options["server"]])
        else:
            print("{} profile not currently implemented.".format(options["profile"]))

