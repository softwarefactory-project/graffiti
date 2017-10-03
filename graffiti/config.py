"""graffiti.config handles config and command files parsing
"""
import imp
import os.path
import sys
import yaml


def parse_config_file(filename, rdoinfo_path=None):
    """Parse graffiti config file
    """
    with open(filename, 'rb') as cfg_file:
        data = yaml.load(cfg_file)
        info = parse_config(data, rdoinfo_path)
        return info
    return None


def parse_config(data, rdoinfo_path=None):
    """Config file parser
    """
    info = {}
    if not rdoinfo_path:
        info['rdoinfo'] = parse_rdoinfo(data)
        rdoinfo_path = info['rdoinfo']['location']
    info['releases'] = parse_releases(rdoinfo_path)
    info['koji'] = parse_koji(data)
    return info


def parse_rdoinfo(data):
    """Retrieve rdoinfo location
    """
    location = os.path.expanduser(data['rdoinfo']['location'])
    return {'location': location}


# Shamelessly taken from rdopkg code
def _ensure_rdoinfo(path):
    # when running get_info with gitrev, we are modifying rdoinfo module
    # while runing rdopkg. This seems to be problematic if we are using
    # the compiled .pyc so i'm forcing to load rdoinfo module from .py
    sys.dont_write_bytecode = True
    file, path, desc = imp.find_module('rdoinfo', [path])
    rdoinfo = imp.load_module('rdoinfo', file, path, desc)
    sys.dont_write_bytecode = False
    return rdoinfo


def parse_releases(rdoinfo_path):
    """Parse config release section
    """
    rdoinfo_db = os.path.join(rdoinfo_path, 'rdo.yml')
    rdoinfo = _ensure_rdoinfo(rdoinfo_path)
    # FIXME: needs to unset include_fns as default in rdoinfo
    # is a relative path
    data = rdoinfo.parse_info_file(rdoinfo_db, include_fns=[])
    releases = data['releases']
    rel = {}
    for release in releases:
        release_name = release['name']
        tags = release['repos'][0]['buildsys-tags']
        rel[release_name] = tags
    return rel


def parse_koji(data):
    """Parse config koji section
    """
    srv = {}
    koji = data['koji']
    srv['username'] = koji['username']
    srv['url'] = koji['url']
    srv['client_cert'] = os.path.expanduser(koji['client_cert'])
    srv['clientca_cert'] = os.path.expanduser(koji['clientca_cert'])
    srv['serverca_cert'] = os.path.expanduser(koji['serverca_cert'])
    return srv


def parse_command_file(filename):
    """Parse command files
    """
    with open(filename, 'rb') as cmd_file:
        data = yaml.load(cmd_file)
        return data
    return {}
