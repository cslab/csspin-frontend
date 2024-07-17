# spin_frontend

This repository contains the spin plugin-package spin_frontend. It provides the
following spin-plugin:

-   spin_python.node (source:
    https://code.contact.de/qs/spin/cs.spin/-/commit/a6cd9906504e9761a5b888add26dfe0d62809bd7)

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
