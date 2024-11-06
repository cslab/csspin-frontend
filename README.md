# spin_frontend

This repository contains the spin plugin-package spin_frontend. It provides the
following spin-plugin:

-   spin_frontend.node (source:
    https://code.contact.de/qs/spin/cs.spin/-/commit/a6cd9906504e9761a5b888add26dfe0d62809bd7)
-   spin_frontend.cypress (source:
    https://code.contact.de/qs/tooling/spin-plugins/-/commit/87399f327a5979c3ef5619291cd12bc26fce04ac)

-   spin_frontend.jest
-   spin_frontend.jsconfig

[cs.spin](https://code.contact.de/qs/spin/cs.spin) is required for developing
`spin_frontend`, installation instructions can be found
[here](http://qs.pages.contact.de/spin/cs.spin/installation.html).

## Requirements

-   The cypress plugin requires Python 3.11+ to be used, since it depends on
    spin_ce.ce_services.

## Creating a New Release

The version scheme used is `major.minor.patch` while following the well-known
standards @CONTACT (https://wiki.contact.de/index.php/Versionsnummer).

**Steps to create a release:**

0. Preparations:
    - Verify that all relevant changes are merged into the branch of which the
      release is based.
    - Also make sure that the latest non-scheduled pipeline for that branch is
      green.
1. Enter the Repository within GitLab > Releases > New Release, select the
   desired branch and tag. Further down, enter the release notes including a
   list of changes (e.g. link issue + related MR) and further information that
   might be useful.
2. Hit "Create release" ✨
