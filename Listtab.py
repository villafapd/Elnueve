import json

from geckordp.actors.root import RootActor
from geckordp.firefox import Firefox
from geckordp.profile import ProfileManager
from geckordp.rdp_client import RDPClient

""" Uncomment to enable debug output
"""
from geckordp.settings import GECKORDP
GECKORDP.DEBUG = 1
GECKORDP.DEBUG_REQUEST = 1
GECKORDP.DEBUG_RESPONSE = 1
GECKORDP.LOG_FILE = "xyz.log" #: enabled

def main():
    # clone default profile to 'geckordp'
    pm = ProfileManager()
    profile_name = "geckordp"
    port = 15200
    pm.clone("default", profile_name)
    profile = pm.get_profile_by_name(profile_name)
    profile.set_required_configs()

    # start firefox with specified profile
    Firefox.start("https://www.elnueve.com.ar/en-vivo", port, profile_name, ["-headless"])

    # create client and connect to firefox
    client = RDPClient()
    client.connect("localhost", port)

    # initialize root
    root = RootActor(client)

    # get a list of tabs
    tabs = root.list_tabs()
    print(json.dumps(tabs, indent=2))

    input()


if __name__ == "__main__":
    main()