echo $(chromium --version | cut -d "." -f 1 | sed -e 's/.*[^0-9]\([0-9]\+\)[^0-9]*$/\1/') > c_Version.moriarty
