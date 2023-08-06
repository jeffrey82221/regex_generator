import requests
import pkg_resources


PKG_NAME = 'random-regex'
IMPORT_NAME = 'random_regex'


def get_all_versions() -> str:
    """
    Gets the latest pip version number from the pypi server.
    Returns: (str) the version of the latest pip module
    """
    try:
        req = requests.get(f"https://pypi.org/pypi/{PKG_NAME}/json")
        return list(req.json()["releases"].keys())
    except BaseException:
        return []


if __name__ == '__main__':
    online_versions = get_all_versions()
    print('online versions:', online_versions)
    my_version = pkg_resources.get_distribution(IMPORT_NAME).version
    print('this version:', my_version)
    assert my_version not in online_versions, "This version already uploaded!"
