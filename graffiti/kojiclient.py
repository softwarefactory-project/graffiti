"""graffiti.koji handles koji interaction
"""
import collections
import koji


class KojiClient(object):
    """Centralize interaction with Koji
    """
    def __init__(self, koji_url,
                 client_cert, clientca_cert, serverca_cert):
        """Setup Koji client session
        Requires server urls and path to certificates
        """
        self.kojiclient = koji.ClientSession(koji_url)
        self.kojiclient.ssl_login(client_cert, clientca_cert, serverca_cert)

    def _get_tag_id(self, tag):
        """map tag name to tag ID in Koji
        """
        tags = [x['id'] for x in self.kojiclient.listTags()
                if x['name'] == tag]
        return tags[0] if len(tags) else None

    def _get_tag_ids(self, tags):
        """map a list tag name to a list of corresponding tag ID in Koji
        """
        tag_ids = [self._get_tag_id(tag) for tag in tags]
        return tag_ids if len(tag_ids) else []

    def retrieve_builds(self, tag):
        """retrieve latest builds in a tag
        """
        tag_id = self._get_tag_id(tag)
        builds = self.kojiclient.listTagged(tag_id, latest=True)
        builds = {b['package_name']: {'name': b['package_name'],
                                      'id': b['build_id'],
                                      'nvr': b['nvr']}
                  for b in builds}
        return builds

    def register_packages(self, tags, pkgs, username):
        """Register packages to a list of tags
        Username is Koji owner
        """
        if not isinstance(tags, collections.Iterable):
            tags = [tags]
        tag_ids = self._get_tag_ids(tags)
        self.kojiclient.multicall = True
        for tag_id in tag_ids:
            for pkg in pkgs:
                self.kojiclient.packageListAdd(tag_id, pkg, owner=username)
        self.kojiclient.multiCall(strict=True)

    def unregister_packages(self, tags, pkgs, force=False):
        """Unregister packages to a list of tags
        """
        # FIXME: remove tagged builds if force set to True
        if not isinstance(tags, collections.Iterable):
            tags = [tags]
        tag_ids = self._get_tag_ids(tags)
        self.kojiclient.multicall = True
        for tag_id in tag_ids:
            for pkg in pkgs:
                self.kojiclient.packageListRemove(tag_id, pkg, force)
        self.kojiclient.multiCall(strict=True)

    def tag_builds(self, target, tags, builds):
        """Tag builds in koji
        target is build expected status (none, candidate, testing, release)

        This function ensures that build is also tagged in previous tags
        e.g if status is testing, build is tagged in candidate and testing

        A specific target 'none' allows removing a build from all tags
        """
        if target not in ['none', 'candidate', 'testing', 'release']:
            raise Exception("""Target must be ['none, 'candidate', 'testing', 'release'].
                            Provided '{}'""".format(target))
        tag_ids = self._get_tag_ids(tags)
        self.kojiclient.multicall = True

        for build in builds:
            for tag_id in tag_ids:
                self.kojiclient.untagBuild(tag_id, build, strict=False)
            if target == 'none':
                continue

            self.kojiclient.tagBuild(tag_ids[0], build)
            if target == 'candidate':
                continue

            self.kojiclient.tagBuild(tag_ids[1], build)
            if target == 'testing':
                continue
            self.kojiclient.tagBuild(tag_ids[2], build)
        self.kojiclient.multiCall(strict=True)
