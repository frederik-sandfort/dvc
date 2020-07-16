import posixpath
from urllib.parse import urlparse

from .azure import AzureRemoteTree
from .gdrive import GDriveRemoteTree
from .gs import GSRemoteTree
from .hdfs import HDFSRemoteTree
from .http import HTTPRemoteTree
from .https import HTTPSRemoteTree
from .local import LocalRemoteTree
from .oss import OSSRemoteTree
from .s3 import S3RemoteTree
from .ssh import SSHRemoteTree

TREES = [
    AzureRemoteTree,
    GDriveRemoteTree,
    GSRemoteTree,
    HDFSRemoteTree,
    HTTPRemoteTree,
    HTTPSRemoteTree,
    S3RemoteTree,
    SSHRemoteTree,
    OSSRemoteTree,
    # NOTE: LocalRemoteTree is the default
]


def _get_tree(remote_conf):
    for tree_cls in TREES:
        if tree_cls.supported(remote_conf):
            return tree_cls
    return LocalRemoteTree


def _get_conf(repo, **kwargs):
    name = kwargs.get("name")
    if name:
        remote_conf = repo.config["remote"][name.lower()]
    else:
        remote_conf = kwargs
    return _resolve_remote_refs(repo.config, remote_conf)


def _resolve_remote_refs(config, remote_conf):
    # Support for cross referenced remotes.
    # This will merge the settings, shadowing base ref with remote_conf.
    # For example, having:
    #
    #       dvc remote add server ssh://localhost
    #       dvc remote modify server user root
    #       dvc remote modify server ask_password true
    #
    #       dvc remote add images remote://server/tmp/pictures
    #       dvc remote modify images user alice
    #       dvc remote modify images ask_password false
    #       dvc remote modify images password asdf1234
    #
    # Results on a config dictionary like:
    #
    #       {
    #           "url": "ssh://localhost/tmp/pictures",
    #           "user": "alice",
    #           "password": "asdf1234",
    #           "ask_password": False,
    #       }
    parsed = urlparse(remote_conf["url"])
    if parsed.scheme != "remote":
        return remote_conf

    base = config["remote"][parsed.netloc]
    url = posixpath.join(base["url"], parsed.path.lstrip("/"))
    return {**base, **remote_conf, "url": url}


def get_cloud_tree(repo, **kwargs):
    remote_conf = _get_conf(repo, **kwargs)
    return _get_tree(remote_conf)(repo, remote_conf)