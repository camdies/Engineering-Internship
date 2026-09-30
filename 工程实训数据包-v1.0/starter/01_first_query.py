# -*- coding: utf-8 -*-
"""第一个查询 —— 跑通这个脚本，你的环境就没问题了。

运行：  python starter/01_first_query.py
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import geodata  # noqa: E402


def main():
    print("=" * 60)
    print("1. 数据里有什么")
    print("=" * 60)
    for k, v in geodata.stats().items():
        print("  %-10s %s" % (k, v))

    print()
    print("=" * 60)
    print("2. 一条记录长什么样")
    print("=" * 60)
    row = geodata.load(limit=1, as_dataframe=False)[0]
    for k in ["id", "title", "data_type", "source_adapter",
              "spatial_bbox", "temporal_start", "license"]:
        print("  %-16s %s" % (k, str(row.get(k))[:70]))
    print("  %-16s %s" % ("keywords", row.get("keywords")))

    print()
    print("=" * 60)
    print("3. 按学科看分布")
    print("=" * 60)
    con = geodata.connect()
    for dt, n in con.execute(
            "SELECT data_type, COUNT(*) FROM datasets GROUP BY 1 ORDER BY 2 DESC"):
        print("  %-28s %6d" % (dt, n))
    con.close()

    print()
    print("=" * 60)
    print("4. 试着找几条有空间范围和时间的海洋数据")
    print("=" * 60)
    rows = geodata.load(
        where="data_type='ocean_marine' AND spatial_bbox IS NOT NULL "
              "AND temporal_start IS NOT NULL",
        limit=5, as_dataframe=False)
    for r in rows:
        print("  -", str(r["title"])[:66])

    print()
    print("全部跑通。现在去看 data_dictionary.md，然后想你的选题。")


if __name__ == "__main__":
    main()
