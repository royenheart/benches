#!/usr/bin/env bash
for bin in clang-format-19 clang-format-18 clang-format; do
    if command -v "$bin" &>/dev/null; then
        exec "$bin" "$@"
    fi
done
echo "Error: no clang-format (19, 18, or unversioned) found in PATH" >&2
exit 1
