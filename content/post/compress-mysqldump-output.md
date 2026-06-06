+++
title = "Compress a mysqldump backup — gzip, zstd, xz (2026)"
date = 2009-01-31
updated = 2026-06-06
slug = "compress-mysqldump-output"
description = "Pipe mysqldump straight through gzip, zstd, or xz to make a compressed SQL backup without a giant intermediate file — and restore it the same way. With the modern zstd recommendation."

[taxonomies]
tags = ["mysql", "mariadb", "mysqldump", "gzip", "zstd", "backup", "linux"]

[extra]
summary = "Pipe mysqldump directly into a compressor so you never write the huge uncompressed .sql to disk. gzip is universal; zstd is the modern default (fast and small); xz squeezes hardest. Restore by piping the decompressor back into mysql."
+++

**TL;DR —** `mysqldump db | zstd > db.sql.zst` dumps and compresses in one pipe — no giant intermediate file. Restore with `zstd -dc db.sql.zst | mysql db`. Use `gzip` for maximum portability, `zstd` for the best speed/size balance, `xz` for the smallest file.

> A 2009 note — the pipe pattern is timeless, but the original reached for `lzma`. In 2026 **zstd** is the one to use; the commands for all the common compressors are below.

## Dump and compress in one pipe

Piping avoids ever writing the full uncompressed dump to disk:

```
# zstd — modern default: fast, great ratio
mysqldump mydb | zstd -o mydb.sql.zst

# gzip — universal, on every system
mysqldump mydb | gzip > mydb.sql.gz

# xz — smallest file, slowest
mysqldump mydb | xz > mydb.sql.xz
```

Add the options you'd normally pass to `mysqldump` (credentials, flags) before the database name.

## Restore: decompress back into mysql

```
zstd -dc mydb.sql.zst | mysql mydb
gunzip  < mydb.sql.gz  | mysql mydb
xz -dc   mydb.sql.xz   | mysql mydb
```

`-dc` / `gunzip <` stream straight to `mysql` — again, no temp file.

## A sane production dump line

For a consistent, restorable backup of an InnoDB database without locking it:

```
mysqldump --single-transaction --quick --routines --triggers --events \
  mydb | zstd > mydb-$(date +%F).sql.zst
```

- `--single-transaction` — consistent snapshot without locking (InnoDB).
- `--quick` — stream rows instead of buffering (low memory on huge tables).
- `--routines --triggers --events` — include stored programs, not just data.

## MariaDB

Use the `mariadb-dump` / `mariadb` client names (the `mysqldump`/`mysql` names still exist as compatibility symlinks):

```
mariadb-dump --single-transaction mydb | zstd > mydb.sql.zst
zstd -dc mydb.sql.zst | mariadb mydb
```

## Speed vs size, roughly

- **gzip** — fast, ~everywhere, moderate ratio. Safe default if you can't install anything.
- **zstd** — as fast as gzip (often faster), notably smaller; `zstd -19` or `--long` for archival. Best all-rounder.
- **xz** — smallest output, much slower CPU. Good for cold archives where size is king.

Tune threads on big dumps: `zstd -T0` (all cores), `xz -T0`.

## FAQ

### How do I check the dump without restoring it?

`zstd -dc mydb.sql.zst | head -50` — peek at the SQL header. `zstd -t` / `gzip -t` test archive integrity.

### Can I dump just one table?

`mysqldump mydb mytable | zstd > mytable.sql.zst`. Add more table names to include several.

### Restore is slow — anything to do?

Wrap large imports with `SET autocommit=0; … COMMIT;` and disable keys during load, or restore from a physical backup tool (Percona XtraBackup / mariabackup) for very large datasets.

## Summary

- Dump+compress: `mysqldump db | zstd > db.sql.zst` (or `gzip`/`xz`).
- Restore: `zstd -dc db.sql.zst | mysql db`.
- Production: add `--single-transaction --quick --routines --triggers`.
- zstd is the modern pick; gzip for portability; xz for smallest.
