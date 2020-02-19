#!/usr/bin/env python
"""graffiti.cli handles user interaction
"""
from __future__ import print_function
import argparse
import json
import pprint
import sys
import six
import yaml
from graffiti import __version__
from graffiti.kojiclient import KojiClient
from graffiti.config import parse_config_file, parse_command_file


def configure_koji(config):
    """Configure a Koji object to be usable by commands
    """
    koji_url = config['koji']['url']
    client_cert = config['koji']['client_cert']
    clientca_cert = config['koji']['clientca_cert']
    serverca_cert = config['koji']['serverca_cert']
    return KojiClient(koji_url, client_cert, clientca_cert, serverca_cert)


def version_cmd():
    """Display graffiti version
    """
    print("graffiti version: {}".format(__version__))


# Different output formats functions
def format_pretty(missing):
    pp = pprint.PrettyPrinter(indent=4)
    pp.pprint(missing)


def format_json(missing):
    print(json.dumps(missing))


def format_yaml(missing):
    print(yaml.dump(missing, default_flow_style=False))


formatters = {'pretty': format_pretty,
              'yaml': format_yaml,
              'json': format_json}


def list_candidates_cmd(config, args):
    """Display candidates builds that are not tagged in testing
    """
    koji = configure_koji(config)
    for release in args.releases:
        release_info = config['releases_info'][release]
        tags = config['releases'][release]
        if 'tags_map' in release_info.keys():
            map_name = release_info['tags_map']
        else:
            map_name = 'unified_buildreqs'
        if map_name == 'unified_buildreqs':
            tag_from = tags[0]
            tag_to = tags[1]
        else:
            tag_from = tags[1]
            tag_to = tags[2]
        if args.old:
            list_old_candidates(koji, tag_from, tag_to, formatter=args.format)
        else:
            list_candidates(koji, tag_from, tag_to, formatter=args.format)


def list_testing_cmd(config, args):
    """Display testing builds that are not tagged in release
    """
    koji = configure_koji(config)
    for release in args.releases:
        release_info = config['releases_info'][release]
        tags = config['releases'][release]
        if 'tags_map' in release_info.keys():
            map_name = release_info['tags_map']
        else:
            map_name = 'unified_buildreqs'
        if map_name == 'unified_buildreqs':
            tag_from = tags[1]
            tag_to = tags[2]
        else:
            tag_from = tags[2]
            tag_to = tags[3]
        list_candidates(koji, tag_from, tag_to, formatter=args.format)


def list_candidates(koji, tag_from, tag_to, formatter='pretty'):
    """Computes builds that in 'tag_from' but not in 'tag_to'
    """
    candidates = koji.retrieve_builds(tag_from)
    testing = koji.retrieve_builds(tag_to)
    missing = {}
    for k in six.iterkeys(candidates):
        if k in testing:
            if candidates[k]['id'] > testing[k]['id']:
                missing[k] = candidates[k]
        else:
            missing[k] = candidates[k]
    formatters[formatter](missing)


def list_old_candidates(koji, tag_from, tag_to, formatter='pretty'):
    """Computes builds that in 'tag_from' but not in 'tag_to'
       which are older that latest on in 'tag_to'
    """
    candidates = koji.retrieve_all_builds(tag_from)
    testing = koji.retrieve_all_builds(tag_to)
    testing_latest = koji.retrieve_builds(tag_to)
    missing = {}
    for k in six.iterkeys(candidates):
        name = candidates[k]['name']
        # we may have packages in -candidate, for which there is no
        # builds in -testing.
        try:
            if k not in testing and k < testing_latest[name]['id']:
                missing[k] = candidates[k]
        except KeyError:
            pass
    formatters[formatter](missing)


def tag_cmd(config, args):
    """Tag builds from command file
    """
    koji = configure_koji(config)
    cmd_file = args.file
    cmds = parse_command_file(cmd_file)
    for release, dat in six.iteritems(cmds):
        release_info = config['releases_info'][release]
        tags = config['releases'][release]
        if 'tags_map' in release_info.keys():
            map_name = release_info['tags_map']
            tags_map = config['tags_maps'][map_name]
        else:
            tags_map = config['tags_maps']['unified_buildreqs']
        for target, builds in six.iteritems(dat):
            koji.tag_builds(target, tags, builds, tags_map)


def register_cmd(config, args):
    """Register packages in tags from command file
    """
    koji = configure_koji(config)
    cmd_file = args.file
    username = config['koji']['username']
    cmds = parse_command_file(cmd_file)
    for release, dat in six.iteritems(cmds):
        tags = config['releases'][release]
        if 'add' in dat:
            pkgs = dat['add']
            koji.register_packages(tags, pkgs, username)
        if 'remove' in dat:
            pkgs = dat['remove']
            koji.unregister_packages(tags, pkgs, True)


def main():
    """graffiti CLI entry point
    """
    parser = argparse.ArgumentParser('graffiti is RDO builds tagging utility')
    parser.add_argument('--config-file', default='config.yaml',
                        help='config file. Default: config.yaml')
    parser.add_argument('--info-repo', help='Path to rdoinfo database. '
                        'Overrides value in config file.')
    parser.add_argument('--centos-release', default='7',
                        choices=['7', '8'],
                        help='CentOS Release to check.')
    subparsers = parser.add_subparsers(dest='cmd')

    subparsers.add_parser('version', help='show version')  # NOQA

    parser_list_candidates = subparsers.add_parser('list-candidates',
                                                   help='list candidates \
                                                   builds')
    parser_list_candidates.add_argument('releases', nargs='+', help='releases')
    parser_list_candidates.add_argument('--old', help='Show old builds in\
                                        candidate but not in testing tags',
                                        action='store_true')
    parser_list_candidates.add_argument('--format', help='Output format',
                                        choices=['pretty', 'json', 'yaml'],
                                        default='pretty')

    parser_list_testing = subparsers.add_parser('list-testing',
                                                help='list testing builds')
    parser_list_testing.add_argument('releases', nargs='+', help='releases')
    parser_list_testing.add_argument('--format', help='Output format',
                                     choices=['pretty', 'json', 'yaml'],
                                     default='pretty')

    parser_tag = subparsers.add_parser('tag', help='tag builds')
    parser_tag.add_argument('-f', required=True, dest='file',
                            help='command file')
    parser_register = subparsers.add_parser('register',
                                            help='register packages')
    parser_register.add_argument('-f', required=True, dest='file',
                                 help='command file')

    if len(sys.argv) == 1:
        sys.argv.append('--help')
    args = parser.parse_args(sys.argv[1:])
    config = parse_config_file(args.config_file, args.info_repo,
                               args.centos_release)

    if args.cmd == 'version':
        version_cmd()
    elif args.cmd == 'list-candidates':
        list_candidates_cmd(config, args)
    elif args.cmd == 'list-testing':
        list_testing_cmd(config, args)
    elif args.cmd == 'tag':
        tag_cmd(config, args)
    elif args.cmd == 'register':
        register_cmd(config, args)
    else:
        print("Unknown command")
    sys.exit(0)


if __name__ == '__main__':
    main()
