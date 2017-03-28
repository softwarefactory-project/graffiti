"""graffiti.config handles config and command files parsing
"""
import os.path
import yaml


def parse_config_file(filename):
    """Parse graffiti config file
    """
    with open(filename, 'rb') as cfg_file:
        data = yaml.load(cfg_file)
        info = parse_config(data)
        return info
    return None


def parse_config(data):
    """Config file parser
    """
    info = {}
    info['releases'] = parse_releases(data)
    info['koji'] = parse_koji(data)
    return info


def parse_releases(data):
    """Parse config release section
    """
    releases = data['releases']
    rel = {}
    for release in releases:
        release_name = release['name']
        tags = release['tags']
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
