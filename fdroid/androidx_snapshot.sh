#!/bin/bash
# Put the androidx.dev snapshot (the version Chromium pins) back for some
# androidx libraries in a tree where androidx=release replaced them, to find
# which release causes a regression. For build.yml's fixup with resume_from:
#
#   curl -fsSL https://raw.githubusercontent.com/AcideFluorhydrique/chromium-fdroid/main/fdroid/androidx_snapshot.sh \
#     | bash -s androidx.preference:preference androidx.recyclerview:recyclerview
#
# Run from the workspace that holds src/. args.gn must have
# update_android_aar_prebuilts = true (androidx=release sets it) so gn gen
# rewrites the .info files.
set -euo pipefail
repo=$(grep -oP "https://androidx\.dev/snapshots/builds/\d+/artifacts/repository" src/third_party/androidx/build.gradle | head -1)
echo "snapshot repository: $repo"
for coord in "$@"; do
  g=${coord%%:*} a=${coord##*:}
  v=$(python3 -c "import json,sys; print(next(e['version'] for e in json.load(open('src/third_party/androidx/bill_of_materials.json')) if e['group']==sys.argv[1] and e['name']==sys.argv[2]))" "$g" "$a")
  d=src/third_party/androidx/cipd/libs/$(echo "${g}_${a}" | tr '.-' '__')
  base="$repo/${g//.//}/$a/$v"
  for f in "$d"/*.aar "$d"/*.jar; do
    [ -e "$f" ] || continue
    ext=${f##*.}
    val=$(curl -fsSL "$base/maven-metadata.xml" | python3 -c "import re,sys; t=sys.stdin.read(); print(re.findall(r'<extension>$ext</extension>\s*<value>([^<]+)</value>', t)[-1])")
    chmod u+w "$d" "$f" 2>/dev/null || true
    rm -f "$f"
    curl -fsSL "$base/$a-$val.$ext" -o "$f"
    echo "$coord: $(basename "$f") <- $a-$val.$ext ($(sha256sum "$f" | cut -c1-16))"
  done
done
# Make ninja rerun gn gen, which regenerates the .info files.
touch src/third_party/androidx/BUILD.gn
grep -q 'update_android_aar_prebuilts = true' src/out/Default/args.gn || echo 'update_android_aar_prebuilts = true' >> src/out/Default/args.gn
