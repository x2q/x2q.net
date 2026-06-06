+++
title = "MySQL: set or reset the AUTO_INCREMENT value (2026)"
date = 2006-08-31
updated = 2026-06-06
slug = "mysql-set-auto-increment"
description = "Set, reset, or bump a table's AUTO_INCREMENT counter in MySQL or MariaDB — why you can't set it below the current maximum, how to reset after deleting rows, and the auto_increment_increment gotchas."

[taxonomies]
tags = ["mysql", "mariadb", "sql", "database", "linux"]

[extra]
summary = "ALTER TABLE … AUTO_INCREMENT = N sets the next id a table will hand out. It won't go below the current max id, behaves differently across storage engines on restart, and interacts with auto_increment_increment on replicated/Galera setups. Here's the full picture."
+++

**TL;DR —** `ALTER TABLE t AUTO_INCREMENT = 100000;` sets the next auto-increment value. You can raise it freely, but you **can't set it below the current maximum id** — MySQL silently clamps it to max+1.

> One of the shortest notes from the old blog (2006) — one line. Still correct, but the caveats below are what actually trip people up.

## Set it

```sql
ALTER TABLE mytable AUTO_INCREMENT = 100000;
```

The next inserted row gets id `100000` (assuming that's above the current max). Handy for leaving room between data sets, or starting ids at a friendlier number.

## Reset after deleting rows

Deleted the tail of a table and want ids to continue from the real maximum instead of the old high-water mark?

```sql
-- continue from the highest existing id
ALTER TABLE mytable AUTO_INCREMENT = 1;   -- clamps up to max(id)+1 automatically
```

Setting it to `1` doesn't reset to 1 if rows exist — MySQL clamps to `MAX(id) + 1`. That's usually exactly what you want after a cleanup.

## Empty a table and truly start at 1

If you want ids to restart from 1, the table must be empty. `TRUNCATE` does both — wipes rows *and* resets the counter:

```sql
TRUNCATE TABLE mytable;     -- removes all rows AND resets AUTO_INCREMENT to 1
```

(`DELETE FROM mytable` removes rows but leaves the counter where it was — use `ALTER TABLE … AUTO_INCREMENT = 1` after it, or `TRUNCATE`.)

## Gotchas

- **Can't go below the max.** `ALTER TABLE … AUTO_INCREMENT = 5` on a table whose largest id is 900 leaves it at 901. There's no way to reuse ids below existing data without rewriting the table.
- **Engine differences on restart.** Modern InnoDB (MySQL 8.0+) persists the counter across restarts. Older InnoDB (≤5.7) recomputed it as `MAX(id)+1` at startup, so a gap at the top could "shrink" after a reboot. MyISAM always persisted it.
- **Replication / Galera.** With `auto_increment_increment` > 1 (multi-primary, Galera, group replication), ids jump in steps (e.g. 1, 3, 5…) by design — don't "fix" the gaps, they prevent id collisions between nodes.
- **Gaps are normal.** Rolled-back transactions and failed inserts consume ids. Auto-increment guarantees uniqueness and monotonicity, **not** contiguity. Don't rely on "no holes".

## FAQ

### How do I see the current value?

```sql
SHOW TABLE STATUS LIKE 'mytable';   -- the Auto_increment column
```

or query `information_schema.TABLES`.

### It won't let me lower it — why?

By design: lowering below existing ids would risk duplicate keys. Rewrite the table (dump, recreate, reload) if you genuinely must renumber.

### Does this work the same in MariaDB?

Yes — `ALTER TABLE … AUTO_INCREMENT = N` and `TRUNCATE` behave the same. Restart-persistence depends on the engine/version as above.

## Summary

- Set/raise: `ALTER TABLE t AUTO_INCREMENT = N`.
- After deletes: `ALTER TABLE t AUTO_INCREMENT = 1` clamps to `MAX(id)+1`.
- Restart at 1: `TRUNCATE TABLE t` (must be empty).
- Can't set below the current max; gaps are expected.
