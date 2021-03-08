#!/bin/bash

VERSION=$1
TAG="v$VERSION"

if [[ -z $VERSION ]]; then
  echo "ERROR: No version to release specified"
  exit 1
fi

rx='^([0-9]+\.){0,2}(\*|[0-9]+)$'

if [[ $VERSION =~ $rx ]]; then
 echo "INFO: Version $VERSION"
else
 echo "ERROR: Version specified not valid: $VERSION"
 exit 1
fi

if git rev-parse $TAG > /dev/null 2>&1; then
  echo "ERROR: Version $VERSION already released"
  exit 1
fi

if [[ `git branch --show-current` != "main" ]]; then
  echo "ERROR: Not currently on main branch"
  exit 1
fi

if [[ `git status --porcelain` ]]; then
  echo "ERROR: There are local changes:"
  git status --short
  exit 1
fi

sed -i "s/VERSION = \"dev\"/\VERSION = \"$VERSION\"/" custom_components/switchbot_cloud/const.py
sed -i "s/  \"version\": \"dev\",/  \"version\": \"$VERSION\",/" custom_components/switchbot_cloud/manifest.json
git add custom_components/switchbot_cloud/const.py
git add custom_components/switchbot_cloud/manifest.json
git commit --message "Release $VERSION"
git tag $TAG
git push origin $TAG
sed -i -E "s/VERSION = \".+\"/\VERSION = \"dev\"/" custom_components/switchbot_cloud/const.py
sed -i -E "s/  \"version\": \".+\",/  \"version\": \"dev\",/" custom_components/switchbot_cloud/manifest.json
git add custom_components/switchbot_cloud/const.py
git add custom_components/switchbot_cloud/manifest.json
git commit --message "Prepare for next version"
git push origin
