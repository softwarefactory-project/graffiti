"""graffiti.config handles config and command files parsing
"""
import imp
import os.path
import yaml


def parse_config_file(filename, rdoinfo_path=None, centos_release='7'):
    """Parse graffiti config file
    """
    with open(filename, 'rb') as cfg_file:
        data = yaml.load(cfg_file)
        info = parse_config(data, rdoinfo_path, centos_release)
        return info
    return None


def parse_config(data, rdoinfo_path=None, centos_release='7'):
    """Config file parser
    """
    info = {}
    if not rdoinfo_path:
        info['rdoinfo'] = parse_rdoinfo(data)
        rdoinfo_path = info['rdoinfo']['location']
    info['releases'] = parse_releases(rdoinfo_path, centos_release)
    info['releases_info'] = parse_releases_info(rdoinfo_path)
    info['koji'] = parse_koji(data)
    info['tags_maps'] = data['tags_maps']
    return info


def parse_rdoinfo(data):
    """Retrieve rdoinfo location
    """
    location = os.path.expanduser(data['rdoinfo']['location'])
    return {'location': location}


# Shamelessly taken from rdopkg code
def _ensure_rdoinfo(path):
    file, path, desc = imp.find_module('rdoinfo', [path])
    rdoinfo = imp.load_module('rdoinfo', file, path, desc)
    return rdoinfo


def parse_releases(rdoinfo_path, centos_release='7'):
    """Parse config release section to extract buildsys-tags
    """
    rdoinfo_db = os.path.join(rdoinfo_path, 'rdo.yml')
    rdoinfo = _ensure_rdoinfo(rdoinfo_path)
    # FIXME: needs to unset include_fns as default in rdoinfo
    # is a relative path
    data = rdoinfo.parse_info_file(rdoinfo_db, include_fns=[])
    releases = data['releases']
    rel = {}
    dist_tag = "el{0}".format(centos_release)
    for release in releases:
        release_name = release['name']
        filter_repos = [dist for dist in release['repos'] if
                        dist['name'] == dist_tag]
        if filter_repos:
            tags = filter_repos[0]['buildsys-tags']
        else:
            tags = release['repos'][0]['buildsys-tags']
        rel[release_name] = tags
    return rel


def parse_releases_info(rdoinfo_path):
    """Parse config release section
    """
    rdoinfo_db = os.path.join(rdoinfo_path, 'rdo.yml')
    rdoinfo = _ensure_rdoinfo(rdoinfo_path)
    data = rdoinfo.parse_info_file(rdoinfo_db, include_fns=[])
    releases = data['releases']
    releases_info = {}
    for release in releases:
        release_name = release['name']
        info = release
        releases_info[release_name] = info
    return releases_info


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
