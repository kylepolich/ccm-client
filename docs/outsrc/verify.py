import json


def get_results(client):
    client_version = client.get_version()
    server_version = client.get_server_version()
    preference_profile = client.get_current_profile()
    return {
        'client_version': client_version,
        'server_version': server_version,
        'preference_profile': preference_profile
    }
