from __future__ import print_function
import os.path
try:
    import unittest.mock as mock
except Exception:
    import mock
from graffiti.config import parse_config_file

from fake_rdoinfo import _ensure_rdoinfo


SAMPLE_CONFIG = """releases:
rdoinfo:
  location: ~/.rdopkg/rdoinfo
koji:
  username: hguemar
  url: https://cbs.centos.org/kojihub
  client_cert: ~/.centos.cert
  clientca_cert: ~/.centos-server-ca.cert
  serverca_cert: /etc/pki/tls/certs/ca-bundle.trust.crt
tags_maps:
  unified_buildreqs:
    candidate: [0]
    testing: [0, 1]
    release: [0, 1, 2]
  separated_buildreqs:
    el7-build: [0]
    candidate: [1]
    testing: [2]
    release: [2, 3]
"""


def test_parse_config_file():
    m = mock.mock_open(read_data=SAMPLE_CONFIG)
    # FIXME: the multiple context managers syntax does
    # not work encapsulated by parenthesis hence disable PEP8 checks
    with mock.patch('__builtin__.open', m), \
         mock.patch('graffiti.config._ensure_rdoinfo',
                    side_effect=_ensure_rdoinfo):  # noqa
        info = parse_config_file('test')
        assert info['koji']['username'] == 'hguemar'
        assert info['koji']['url'] == 'https://cbs.centos.org/kojihub'
        assert info['koji']['client_cert'] == \
            os.path.expanduser('~/.centos.cert')
        assert info['koji']['clientca_cert'] == \
            os.path.expanduser('~/.centos-server-ca.cert')
        assert info['koji']['serverca_cert'] == \
            os.path.expanduser('/etc/pki/tls/certs/ca-bundle.trust.crt')
        assert info['rdoinfo']['location'] == \
            os.path.expanduser('~/.rdopkg/rdoinfo')
        assert info['releases'] == \
            {'newton': ['cloud7-openstack-newton-candidate',
                        'cloud7-openstack-newton-testing',
                        'cloud7-openstack-newton-release'],
             'pike': ['cloud7-openstack-pike-candidate',
                      'cloud7-openstack-pike-testing',
                      'cloud7-openstack-pike-release'],
             'ocata': ['cloud7-openstack-ocata-candidate',
                       'cloud7-openstack-ocata-testing',
                       'cloud7-openstack-ocata-release'],
             'queens': ['cloud7-openstack-queens-candidate',
                        'cloud7-openstack-queens-testing']}
        assert info['releases_info']['queens'] == \
            {'name': 'queens',
             'branch': 'rpm-master',
             'repos': [{'name': 'el7',
                        'buildsys': 'cbs/cloud7-openstack-queens-el7',
                        'buildsys-tags': ['cloud7-openstack-queens-candidate',
                                          'cloud7-openstack-queens-testing'],
                        'distrepos': [{'name': 'RDO Queens el7',
                                       'url': 'url1'},
                                      {'name': 'CentOS 7 Base',
                                       'url': 'url2'},
                                      {'name': 'CentOS 7 Updates',
                                       'url': 'url3'},
                                      {'name': 'CentOS 7 Extras',
                                       'url': 'url4'}]}]}
        assert info['tags_maps'] == \
            {'unified_buildreqs': {'candidate': [0],
                                   'testing': [0, 1],
                                   'release': [0, 1, 2]},
             'separated_buildreqs': {'el7-build': [0],
                                     'candidate': [1],
                                     'testing': [2],
                                     'release': [2, 3]}}

