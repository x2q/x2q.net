+++
title = "MySQL: find and remove duplicate rows (2026)"
date = 2007-06-09
updated = 2026-06-06
slug = "mysql-remove-duplicate-rows"
description = "Find and delete duplicate rows in MySQL or MariaDB — the self-join DELETE that works everywhere, the modern window-function approach, and how to add a UNIQUE index to keep them out."

[taxonomies]
tags = ["mysql", "mariadb", "sql", "database", "linux"]

[extra]
summary = "The old ALTER IGNORE TABLE … ADD UNIQUE trick was removed in MySQL 5.7. The portable way to dedupe now is a self-join DELETE keeping the lowest id; MySQL 8 / MariaDB 10.2+ add a cleaner window-function version. Then add a UNIQUE index so duplicates can't come back."
+++

**TL;DR —** find duplicates with `GROUP BY … HAVING COUNT(*) > 1`; delete them with a self-join `DELETE` that keeps the lowest `id`; then add a `UNIQUE` index so they can't return. The old `ALTER IGNORE TABLE … ADD UNIQUE` shortcut was **removed in MySQL 5.7** — don't use it.

> The 2007 version of this post used `ALTER IGNORE TABLE … ADD UNIQUE INDEX` to let MySQL drop the dupes for you. That `IGNORE` clause is gone in modern MySQL, so here are the approaches that actually work in 2026.

## 1. Find the duplicates first

Decide what "duplicate" means — which columns must match. Say rows are duplicates when `(a, b)` are equal:

```sql
SELECT a, b, COUNT(*) AS n
FROM mydata
GROUP BY a, b
HAVING n > 1;
```

Always look before you delete.

## 2. Delete them, keeping one row

### Self-join (works on every version)

Keep the row with the **lowest `id`** in each duplicate group:

```sql
DELETE t1
FROM mydata t1
JOIN mydata t2
  ON t1.a = t2.a
 AND t1.b = t2.b
 AND t1.id > t2.id;
```

`t1.id > t2.id` deletes every copy except the smallest id. Flip to `<` to keep the newest instead.

### Window function (MySQL 8.0+ / MariaDB 10.2+)

Cleaner and easy to extend to "keep the newest per group":

```sql
DELETE FROM mydata
WHERE id IN (
  SELECT id FROM (
    SELECT id,
           ROW_NUMBER() OVER (PARTITION BY a, b ORDER BY id) AS rn
    FROM mydata
  ) x
  WHERE rn > 1
);
```

The extra subquery layer is required — MySQL won't let you delete from a table you're selecting from directly.

## 3. Stop them coming back

Once the table is clean, add a `UNIQUE` index so future inserts can't duplicate:

```sql
ALTER TABLE mydata ADD UNIQUE INDEX uq_a_b (a, b);
```

Then write inserts as `INSERT … ON DUPLICATE KEY UPDATE …` or `INSERT IGNORE` so the dedup is enforced at write time.

## Big tables: the rebuild approach

For very large tables, rewriting via a fresh table is often faster than a giant `DELETE`:

```sql
CREATE TABLE mydata_clean LIKE mydata;
ALTER TABLE mydata_clean ADD UNIQUE INDEX uq_a_b (a, b);
INSERT IGNORE INTO mydata_clean SELECT * FROM mydata;   -- IGNORE drops dup-key rows
RENAME TABLE mydata TO mydata_old, mydata_clean TO mydata;
```

## FAQ

### Why doesn't ALTER IGNORE TABLE work anymore?

The `IGNORE` keyword on `ALTER TABLE` was deprecated in MySQL 5.6 and **removed in 5.7**. The self-join or rebuild approach replaces it.

### How do I keep the newest row instead of the oldest?

Self-join: change `t1.id > t2.id` to `t1.id < t2.id`. Window function: `ORDER BY id DESC` in the `PARTITION BY`.

### Back up first?

Yes. `DELETE` is irreversible — take a [compressed dump](/post/compress-mysqldump-output/) before running it on production.

## Summary

- Find: `GROUP BY cols HAVING COUNT(*) > 1`.
- Delete (portable): self-join `DELETE … WHERE t1.id > t2.id`.
- Delete (modern): `ROW_NUMBER() OVER (PARTITION BY …)`.
- Prevent: add a `UNIQUE` index + `INSERT … ON DUPLICATE KEY`.
