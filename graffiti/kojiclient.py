"""graffiti.koji handles koji interaction
"""
import collections
import copy
import koji


# List of added tags for each tag for original model without separateed
# buildreqs.
# 0 is candidate, 1 is testing and 2 release.
TAGS_MAP = {'candidate': [0],
            'testing': [0, 1],
            'release': [0, 1, 2]}

# List of added tags for each tag for separated-buildreqs model
# 0 is el7-build, 1 is candidate, 2 is testing and 3 release.
TAGS_MAP_BRS = {'el7-build': [0],
                'candidate': [1],
                'testing': [2],
                'release': [2, 3]}


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
        self.kojiclient.multicall = False
        tags = [x['id'] for x in self.kojiclient.listTags()
                if x['name'] == tag]
        return tags[0] if len(tags) else None

    def _get_tag_ids(self, tags):
        """map a list tag name to a list of corresponding tag ID in Koji
        """
        tag_ids = [self._get_tag_id(tag) for tag in tags]
        return tag_ids if len(tag_ids) else []

    def retrieve_build_info(self, build):
        """retrieve info about a build
        """
        self.kojiclient.multicall = False
        build = self.kojiclient.getBuild(build)
        taglist = []
        if build:
            for tag in self.kojiclient.listTags(build):
                taglist.append(tag['name'])
            build['tags'] = taglist
        return build

    def retrieve_builds(self, tag):
        """retrieve latest builds in a tag
        """
        tag_id = self._get_tag_id(tag)
        builds = self.kojiclient.listTagged(tag_id, latest=False)
        # filter out older builds
        # Koji listTagged call returns latest modified build *not* latest build
        # so we retrieve all builds and compaire build id to keep only latest
        latest_builds = {}
        for b in builds:
            package_name = b['package_name']
            build_id = b['build_id']
            if package_name in latest_builds:
                b2 = latest_builds[package_name]
                if b2['id'] > build_id:
                    continue
            latest_builds[package_name] = {'name': package_name,
                                           'id': build_id,
                                           'nvr': b['nvr']}
        return latest_builds

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

    def _apply_tags(self, build, tags, added_tags):
        """ Apply tags in a koji instance for a build.
            params:
             - build: nvr for the build to be tagged.
             - tags: list of tags in a release
             - added_tags: tags required for a build in
               the given release
        """
        self.kojiclient.multicall = True

        tag_ids = self._get_tag_ids(tags)
        remove_tags = copy.copy(tag_ids)

        buildinfo = self.retrieve_build_info(build)
        if not buildinfo:
            raise Exception("Build %s does not exist" % build)
        build_tags = buildinfo['tags']
        for added in added_tags:
            remove_tags.remove(tag_ids[added])
            if tags[added] not in build_tags:
                self.kojiclient.tagBuild(tag_ids[added], build)
        for removed in remove_tags:
            self.kojiclient.untagBuild(removed, build, strict=False)

    def tag_builds(self, target, tags, builds, separated_brs=False):
        """Tag builds in koji
        target is build expected status (none, el7-build, testing, release)

        This function ensures that build is also tagged in previous tags as
        defined in the appropiate tags workflow:
        - Before Rocky:
          * Packages in -candidate are tagged only in -candidate.
          * Packages in -testing are tagged in -candidate and -testing.
          * Packages in -release are tagged in -candidate, -testing and
            -release.
       - Since rocky:
          * BuildRequires only will be untagged from -candidate and tagged into
            -el7-build.
          * Other packages, when tagged into -testing will be untagged from
            -candidate.
          * Packages tagged to -release will be also tagged into -testing.

        A specific target 'none' allows removing a build from all tags
        """

        available_targets = ['none', 'el7-build', 'candidate', 'testing',
                             'release']
        if target not in available_targets:
            raise Exception("""Target must be ['none', 'el7-build', 'candidate', 'testing', 'release'].
                            Provided '{}'""".format(target))

        self.kojiclient.multicall = True

        if separated_brs:
            tags_map = TAGS_MAP_BRS
        else:
            tags_map = TAGS_MAP

        for build in builds:
            if target == 'none':
                tag_ids = self._get_tag_ids(tags)
                for tag_id in tag_ids:
                    self.kojiclient.untagBuild(tag_id, build, strict=False)
            else:
                add_tags = tags_map[target]
                self._apply_tags(build, tags, add_tags)