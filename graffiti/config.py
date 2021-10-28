"""graffiti.config handles config and command files parsing
"""
import os.path
import yaml

from distroinfo import info as dinfo


def parse_config_file(filename, rdoinfo_path=None, centos_release='7',
                      info_file='rdo.yml'):
    """Parse graffiti config file
    """
    with open(filename, 'rb') as cfg_file:
        data = yaml.safe_load(cfg_file)
        info = parse_config(data, rdoinfo_path, centos_release, info_file)
        return info
    return None


def parse_config(data, rdoinfo_path=None, centos_release='7',
                 info_file='rdo.yml'):
    """Config file parser
    """
    info = {}
    if not rdoinfo_path:
        info['rdoinfo'] = parse_rdoinfo(data)
        rdoinfo_path = info['rdoinfo']['location']
    info['releases'] = parse_releases(rdoinfo_path, centos_release, info_file)
    info['releases_info'] = parse_releases_info(rdoinfo_path, info_file)
    info['koji'] = parse_koji(data)
    info['tags_maps'] = data['tags_maps']
    return info


def parse_rdoinfo(data):
    """Retrieve rdoinfo location
    """
    location = os.path.expanduser(data['rdoinfo']['location'])
    return {'location': location}


def parse_releases(rdoinfo_path, centos_release='7', info_file='rdo.yml'):
    """Parse config release section to extract buildsys-tags
    """
    data = dinfo.DistroInfo(info_files=info_file,
                            local_info=rdoinfo_path).get_info()
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


def parse_releases_info(rdoinfo_path, info_file='rdo.yml'):
    """Parse config release section
    """
    data = dinfo.DistroInfo(info_files=info_file,
                            local_info=rdoinfo_path).get_info()
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
        data = yaml.safe_load(cmd_file)
        return data
    return {}
