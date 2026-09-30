# -*- coding: utf-8 -*-
"""geodata —— 工程实训数据包读取工具

不想写 SQL 的话，用这几个函数就够了。

    import geodata
    df = geodata.load()                    # 全部 5 万条
    df = geodata.load(limit=100)           # 先看 100 条
    df = geodata.load(where="data_type='ocean_marine' AND spatial_bbox IS NOT NULL")
    hit = geodata.naive_search("snow cover glacier")   # 一个朴素基线

连接是只读的，写不进去，放心用。
"""
import json
import os
import sqlite3

_HERE = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(_HERE, "geodata-teaching.db")
JSON_COLS = ("providers", "keywords", "distributions", "related_publications")
TEXT_SEARCH_COLS = ("title", "description", "keywords", "providers", "doi", "search_topic")


def connect(path=None):
    """打开只读连接。"""
    p = path or DB_PATH
    if not os.path.exists(p):
        raise FileNotFoundError(
            "找不到数据文件：%s\n请确认 geodata-teaching.db 与 geodata.py 在同一目录下。" % p)
    con = sqlite3.connect(p)
    con.execute("PRAGMA query_only = ON")       # 强制只读
    con.row_factory = sqlite3.Row
    return con


def fields(path=None):
    """返回 datasets 表的所有字段名。"""
    con = connect(path)
    try:
        return [r[1] for r in con.execute("PRAGMA table_info(datasets)")]
    finally:
        con.close()


def load(limit=None, where=None, columns=None, parse_json=True,
         as_dataframe=True, path=None):
    """把数据集读成 DataFrame（没装 pandas 时返回 dict 列表）。

    limit       只要前 N 条
    where       SQL 过滤条件，例如 "data_type='ocean_marine'"
    columns     指定字段；默认全部
    parse_json  是否把 JSON 字段转成 Python 对象
    """
    cols = list(columns) if columns else fields(path)
    sql = "SELECT %s FROM datasets" % ",".join(cols)
    if where:
        sql += " WHERE %s" % where
    if limit:
        sql += " LIMIT %d" % int(limit)

    con = connect(path)
    try:
        rows = [dict(zip(cols, r)) for r in con.execute(sql)]
    finally:
        con.close()

    if parse_json:
        for row in rows:
            for c in JSON_COLS:
                if c in row:
                    try:
                        row[c] = json.loads(row[c]) if row[c] else []
                    except (TypeError, ValueError):
                        row[c] = []

    if not as_dataframe:
        return rows
    try:
        import pandas as pd
        return pd.DataFrame(rows)
    except ImportError:
        return rows


def naive_search(query, limit=20, path=None):
    """最朴素的关键词基线：逐词 LIKE 匹配，命中次数多的排前面。

    这是你的**起点，不是目标**。它的毛病很明显——不懂同义词、不懂语义、
    中英文对不上、排序只看命中次数。

    你要做的是用同一套评测集证明你的方案比它好。
    """
    terms = [t for t in query.replace(",", " ").split() if t]
    if not terms:
        return []

    hit_expr = " + ".join(
        "CASE WHEN COALESCE(%s,'') LIKE ? THEN 1 ELSE 0 END" % c
        for c in TEXT_SEARCH_COLS)
    score = " + ".join("(%s)" % hit_expr for _ in terms)

    params = []
    for t in terms:
        params.extend(["%%%s%%" % t] * len(TEXT_SEARCH_COLS))

    sql = ("SELECT * FROM (SELECT *, (%s) AS _hits FROM datasets) "
           "WHERE _hits > 0 ORDER BY _hits DESC, importance_score DESC LIMIT %d"
           % (score, int(limit)))

    con = connect(path)
    try:
        rows = [dict(r) for r in con.execute(sql, params)]
    finally:
        con.close()
    return rows


def stats(path=None):
    """快速看一眼总量和各字段覆盖率。"""
    checks = [
        ("有描述", "TRIM(COALESCE(description,''))<>''"),
        ("有关键词", "keywords IS NOT NULL AND TRIM(keywords) NOT IN ('','[]')"),
        ("有空间范围",
         "spatial_bbox IS NOT NULL AND TRIM(spatial_bbox) NOT IN ('','[]','null')"),
        ("有时间起点", "temporal_start IS NOT NULL"),
        ("有DOI", "TRIM(COALESCE(doi,''))<>''"),
        ("有许可", "TRIM(COALESCE(license,''))<>''"),
    ]
    con = connect(path)
    try:
        n = con.execute("SELECT COUNT(*) FROM datasets").fetchone()[0]
        out = {"总条数": n}
        for label, cond in checks:
            k = con.execute(
                "SELECT COUNT(*) FROM datasets WHERE %s" % cond).fetchone()[0]
            out[label] = "%d (%.1f%%)" % (k, 100.0 * k / n)
        return out
    finally:
        con.close()


if __name__ == "__main__":
    for k, v in stats().items():
        print("%-10s %s" % (k, v))
