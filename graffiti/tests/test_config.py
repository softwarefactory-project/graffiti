from __future__ import print_function
import os.path
try:
    import unittest.mock as mock
except:
    import mock
from graffiti.config import parse_config_file


SAMPLE_CONFIG = """releases:
- name: pike
  tags:
  - cloud7-openstack-pike-candidate
  - cloud7-openstack-pike-testing
  - cloud7-openstack-pike-release
- name: ocata
  tags:
  - cloud7-openstack-ocata-candidate
  - cloud7-openstack-ocata-testing
  - cloud7-openstack-ocata-release
- name: newton
  tags:
  - cloud7-openstack-newton-candidate
  - cloud7-openstack-newton-testing
  - cloud7-openstack-newton-release
- name: mitaka
  tags:
  - cloud7-openstack-mitaka-candidate
  - cloud7-openstack-mitaka-testing
  - cloud7-openstack-mitaka-release
- name: common
  tags:
  - cloud7-openstack-common-candidate
  - cloud7-openstack-common-testing
  - cloud7-openstack-common-release
koji:
  username: hguemar
  url: https://cbs.centos.org/kojihub
  client_cert: ~/.centos.cert
  clientca_cert: ~/.centos-server-ca.cert
  serverca_cert: /etc/pki/tls/certs/ca-bundle.trust.crt
"""


def test_parse_config_file():
    m = mock.mock_open(read_data=SAMPLE_CONFIG)
    with mock.patch('__builtin__.open', m):
        info = parse_config_file('test')
        assert info['koji']['username'] == 'hguemar'
        assert info['koji']['url'] == 'https://cbs.centos.org/kojihub'
        assert info['koji']['client_cert'] == \
            os.path.expanduser('~/.centos.cert')
        assert info['koji']['clientca_cert'] == \
            os.path.expanduser('~/.centos-server-ca.cert')
        assert info['koji']['serverca_cert'] == \
            os.path.expanduser('/etc/pki/tls/certs/ca-bundle.trust.crt')
