+++
title = "Find the most recently changed files on Linux (2026)"
date = 2007-10-30
updated = 2026-06-06
slug = "find-recently-changed-files-linux"
description = "List the most recently modified files recursively on Linux with find and sort, filter by age with -mmin/-mtime, and the macOS-compatible variants when find lacks -printf."

[taxonomies]
tags = ["linux", "find", "command-line", "macos", "shell"]

[extra]
summary = "find -printf with sort gives you a newest-last list of every file in a tree; -mmin/-mtime filter by age. macOS's BSD find lacks -printf, so this covers the portable variants too. Handy for 'what just changed on this server?'"
+++

**TL;DR —** `find . -type f -printf '%T+ %p\n' | sort | tail` lists files newest-last across a whole tree. To filter by age, `find . -type f -mmin -60` (last hour) or `-mtime -1` (last day). On macOS, use the `stat`/`-newermt` variants below.

> A one-line note from 2007 that's still in my muscle memory. "What changed on this box recently?" comes up constantly — here's the full toolkit.

## Newest files in a directory tree (GNU/Linux)

```
find . -type f -printf '%T+ %p\n' | sort | tail -20
```

- `-printf '%T+ %p\n'` prints a sortable `YYYY-MM-DD+HH:MM:SS` timestamp then the path.
- `sort` orders oldest→newest; `tail -20` shows the 20 most recent (`| sort -r | head` flips it).

## Filter by age directly

`find` can select by modification time without sorting:

```
find . -type f -mmin -60      # modified in the last 60 minutes
find . -type f -mmin -5       # last 5 minutes
find . -type f -mtime -1      # last 24 hours (-mtime is in days)
find . -type f -mtime -7      # last week
```

The leading `-` means "less than N ago"; `+N` means "more than N ago".

## Files newer than a reference

```
find . -type f -newer /etc/some.reference     # changed after that file
find . -type f -newermt "2026-06-01"          # changed after a date (GNU)
find . -type f -newermt "2 hours ago"         # changed in the last 2 hours
```

## Add details (size, time) to the listing

```
find . -type f -mmin -60 -printf '%TY-%Tm-%Td %TT  %10s  %p\n' | sort
# or hand off to ls for human sizes:
find . -type f -mmin -60 -exec ls -lh --time-style=long-iso {} +
```

## macOS / BSD find (no -printf)

BSD `find` on macOS doesn't support `-printf`. Use `-newermt` (it does have that) or fall back to `stat`:

```
find . -type f -mtime -1                       # works on macOS too
find . -type f -newermt "2026-06-01"           # date filter
# newest-last with stat (macOS stat syntax):
find . -type f -exec stat -f '%m %N' {} + | sort -n | tail -20
```

(`%m` = epoch mtime, `%N` = name; `sort -n` orders numerically.)

## FAQ

### What's the difference between modified, changed, and accessed?

`-mtime`/`%T` = **content** last modified. `-ctime`/`%C` = inode **changed** (permissions, rename, content). `-atime`/`%A` = last **accessed** (often disabled via `noatime` mounts). For "what file changed" you almost always want `-mtime`/`-mmin`.

### How do I find the single newest file?

`find . -type f -printf '%T@ %p\n' | sort -n | tail -1 | cut -d' ' -f2-` (`%T@` is epoch seconds).

### Exclude a directory (e.g. .git)?

`find . -path ./.git -prune -o -type f -mmin -60 -print`.

## Summary

- Newest-last list: `find . -type f -printf '%T+ %p\n' | sort | tail`.
- By age: `-mmin -60` (minutes), `-mtime -1` (days), `-newermt "…"`.
- macOS: use `-mtime`/`-newermt`, or `stat -f '%m %N'` since BSD find has no `-printf`.
