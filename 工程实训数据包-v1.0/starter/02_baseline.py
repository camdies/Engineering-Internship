# -*- coding: utf-8 -*-
"""一个朴素基线 —— 这就是你要超过的对象。

运行：  python starter/02_baseline.py

它做的事情很简单：把查询拆成词，逐词在若干字段里做 LIKE 匹配，
命中次数多的排前面。没有语义、没有同义词、没有中英文对齐。

这不是「参考答案」，是「最弱的下限」。你的任务是：
  1. 先给自己造一套评测集（哪些查询、每个查询对应哪些相关数据集）
  2. 测出这个基线在评测集上的指标（Recall@k / nDCG / MRR）
  3. 做出你的方案，用同一套评测集证明它更好
  4. 分析它在哪类查询上失效、为什么

没有基线对比的方案，做得再好也拿不到高分。
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import geodata  # noqa: E402


QUERIES = [
    "snow cover",
    "glacier mass balance",
    "sea surface temperature",
    "soil moisture",
    "vegetation index",
]


def main():
    for q in QUERIES:
        hits = geodata.naive_search(q, limit=5)
        print("=" * 66)
        print("查询：%s   （命中 %d 条）" % (q, len(hits)))
        print("=" * 66)
        for i, h in enumerate(hits, 1):
            print("  %d. [%s] %s" % (i, h["data_type"], str(h["title"])[:58]))
        print()

    print("观察一下：上面这些结果里，有多少是真的相关的？")
    print("如果你觉得「好像还行」，试着换几个中文查询，或者换成")
    print("「2015 年以后北极的海冰数据」这种带时空约束的句子，再看结果。")
    print()
    print("把这些判断记下来 —— 那就是你的评测集的起点。")


if __name__ == "__main__":
    main()
