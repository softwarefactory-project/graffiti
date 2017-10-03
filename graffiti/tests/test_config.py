from __future__ import print_function
import os.path
try:
    import unittest.mock as mock
except:
    import mock
from graffiti.config import parse_config_file


SAMPLE_CONFIG = """releases:
rdoinfo:
  location: ~/.rdopkg/rdoinfo/
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
        assert info['rdoinfo']['location'] == \
            os.path.expanduser('~/.rdopkg/rdoinfo')
