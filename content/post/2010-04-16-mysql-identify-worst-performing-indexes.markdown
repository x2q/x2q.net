---
categories:
- Hacking
- MySQL
comments: true
date: "2010-04-16T07:56:45Z"
slug: mysql-identify-worst-performing-indexes
tags:
- MySQL
- Performance
title: 'MySQL: Identify The Worst Performing Indexes'
wordpress_id: 157
---

This script shows the Top 10 worst performing indexes (in terms of selectivity %) on the whole [MySQL](https://en.wikipedia.org/wiki/MySQL) server instance. Selectivity is the percentage of distinct values in an indexed field compared to the number of records in the table. When constructing indexes, you want to create indexes on columns that have a good chance of "high selectivity". This requires some understanding of the data in the column, which you may or may not have depending on your knowledge of the domain and the availability of sample data. Keep in mind that selectivity is {" Index Selectivity = Number of Distinct Values / Total Number of Rows "}

Lets consider a table "People" with three columns;  name, surname, gender, and age.

For example, creating an index on a column such as gender (where gender is constrained to (NULL), M or F) would not provide much benefit during a query (especially if the query already results in a table scan for other reasons). In any scenario, the selectivity of this index would be extremely low. Depending on the database, using this index may actually be worse that a full table scan.

However, creating a composite index on (name , surname) would provide benefits when executing queries against those columns. The selectivity of this index (for most populations) would be pretty good.

An index with selectivity of 1 is the ideal, however, the only way to achieve a selectivity of 1 is to have a unique index on a non-nullable column.

In general we say, that indexes help us to search the rows faster, however

1. If the index column is **_not used for searches_** there is no point in defining it.
2. If the values in that column **_keep changing_** very frequently it will be extra work for database server (for re-indexing)
3. If there are **_too many inserts and deletes_** from table it will be extra work for server

**Query to Identify The Worst Performing Indexes**

Note that this query can take some time to complete on servers with lots of databases or lots of tables.

{% gist 635219 %}

Example output on a MySQL server with a few wordpress databases.

```
x2q@x2q:~$ mysql --table -u x2q -p < mysql-worst-indexes.sql
+-----+------------------+---------------------------+------------------+--------------+--------+------+----------+-------+
| db  | table            | index name                | field name       | seq in index | # cols | card | est rows | sel % |
+-----+------------------+---------------------------+------------------+--------------+--------+------+----------+-------+
| aa  | wp_commentmeta   | meta_key                  | meta_key         |            1 |      1 |    0 |     1360 |  0.00 |
| aa1 | wp_commentmeta   | meta_key                  | meta_key         |            1 |      1 |    6 |    14023 |  0.04 |
| aa  | wp_comments      | comment_approved_date_gmt | comment_approved |            1 |      2 |    1 |     2213 |  0.05 |
| aa  | wp_comments      | comment_parent            | comment_parent   |            1 |      1 |    1 |     2213 |  0.05 |
| aa  | wp_postmeta      | meta_value                | meta_value       |            1 |      1 |    1 |     1693 |  0.06 |
| aa  | wp_term_taxonomy | taxonomy                  | taxonomy         |            1 |      1 |    2 |     3548 |  0.06 |
| aa  | wp_posts         | post_related              | post_name        |            1 |      2 |    1 |      808 |  0.12 |
| aa  | wp_posts         | yarpp_title               | post_title       |            1 |      1 |    1 |      808 |  0.12 |
| aa  | wp_posts         | post_author               | post_author      |            1 |      1 |    1 |      808 |  0.12 |
| aa  | wp_posts         | yarpp_content             | post_content     |            1 |      1 |    1 |      808 |  0.12 |
+-----+------------------+---------------------------+------------------+--------------+--------+------+----------+-------+
```
