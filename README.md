## Graffiti

Graffiti is a low-level utility handling interactions with Koji. It's still alpha software.


## Design

Graffiti uses a YAML configuration file containing:
- list releases and corresponding tags
- koji credentials (no secrets, only koji url, username, path to certificates)

It currently can
- list latest builds in candidate that are not tagged into testing
- list latest builds in testing that are not tagged into candidate
- add/remove packages to tags using a command file (see samples)
- tag/untag builds using a command file (see samples) and ensure that there are appropriately
tagged (candidate -> testing -> candidate)
- use koji multicall feature to speed up operations


## Develop

```bash
% sudo yum install koji PyYAML
% python setup.py develop --user # can't use virtualenv because of koji module
% graffiti --config-file <config-file> <command> <options>
```

## Todo

A lot :)