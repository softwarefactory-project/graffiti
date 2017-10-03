# Fake rdoinfo module for tests
#

import sys
import yaml

RDOINFO_SAMPLE = """releases:
- name: queens
  branch: rpm-master
  repos:
  - name: el7
    buildsys: cbs/cloud7-openstack-queens-el7
    buildsys-tags:
    - cloud7-openstack-queens-candidate
    - cloud7-openstack-queens-testing
    distrepos:
    - name: RDO Pike el7
      url: http://mirror.centos.org/centos/7/cloud/x86_64/openstack-queens/
    - name: CentOS 7 Base
      url: http://mirror.centos.org/centos/7/os/x86_64/
    - name: CentOS 7 Updates
      url: http://mirror.centos.org/centos/7/updates/x86_64/
    - name: CentOS 7 Extras
      url: http://mirror.centos.org/centos/7/extras/x86_64/
- name: pike
  branch: pike-rdo
  repos:
  - name: el7
    buildsys: cbs/cloud7-openstack-pike-el7
    buildsys-tags:
    - cloud7-openstack-pike-candidate
    - cloud7-openstack-pike-testing
    - cloud7-openstack-pike-release
    distrepos:
    - name: RDO Pike el7
      url: http://mirror.centos.org/centos/7/cloud/x86_64/openstack-pike/
    - name: CentOS 7 Base
      url: http://mirror.centos.org/centos/7/os/x86_64/
    - name: CentOS 7 Updates
      url: http://mirror.centos.org/centos/7/updates/x86_64/
    - name: CentOS 7 Extras
      url: http://mirror.centos.org/centos/7/extras/x86_64/
- name: ocata
  branch: ocata-rdo
  repos:
  - name: el7
    buildsys: cbs/cloud7-openstack-ocata-el7
    buildsys-tags:
    - cloud7-openstack-ocata-candidate
    - cloud7-openstack-ocata-testing
    - cloud7-openstack-ocata-release
    distrepos:
    - name: RDO Ocata el7
      url: http://mirror.centos.org/centos/7/cloud/x86_64/openstack-ocata/
    - name: CentOS 7 Base
      url: http://mirror.centos.org/centos/7/os/x86_64/
    - name: CentOS 7 Updates
      url: http://mirror.centos.org/centos/7/updates/x86_64/
    - name: CentOS 7 Extras
      url: http://mirror.centos.org/centos/7/extras/x86_64/
- name: newton
  branch: newton-rdo
  repos:
  - name: el7
    buildsys: cbs/cloud7-openstack-newton-el7
    buildsys-tags:
    - cloud7-openstack-newton-candidate
    - cloud7-openstack-newton-testing
    - cloud7-openstack-newton-release
    distrepos:
    - name: RDO Newton el7
      url: http://mirror.centos.org/centos/7/cloud/x86_64/openstack-newton/
    - name: CentOS 7 Base
      url: http://mirror.centos.org/centos/7/os/x86_64/
    - name: CentOS 7 Updates
      url: http://mirror.centos.org/centos/7/updates/x86_64/
    - name: CentOS 7 Extras
      url: http://mirror.centos.org/centos/7/extras/x86_64/
"""


def parse_info_file(rdoinfo_db, include_fns):
    return yaml.load(RDOINFO_SAMPLE)


def _ensure_rdoinfo(path):
    return sys.modules[__name__]
