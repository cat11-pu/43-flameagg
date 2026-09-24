"""flameagg.py：调用栈聚合（基线：只数顶层帧）。"""
from __future__ import annotations


class FlameAgg:
    def __init__(self, max_depth: int = 8):
        self.max_depth = max_depth
        self.tops = {}
        self.samples = 0
        self.truncated = 0

    def add(self, stack, weight: int = 1) -> dict:
        """基线：只把栈顶函数加起来。"""
        self.samples += 1
        if stack:
            self.tops[stack[0]] = self.tops.get(stack[0], 0) + weight
        return {"samples": self.samples}

    def merge(self, other) -> "FlameAgg":
        raise NotImplementedError("两棵树合并还没实现")

    def fold(self) -> dict:
        return dict(self.tops)

    def tree(self) -> dict:
        raise NotImplementedError("层级聚合还没实现")

    def persist(self) -> bytes:
        raise NotImplementedError("快照还没实现")

    def restore(self, blob: bytes = None) -> dict:
        raise NotImplementedError("重启恢复还没实现")

    def stats(self) -> dict:
        return {"samples": self.samples, "truncated": self.truncated, "max_depth": self.max_depth,
                "tops": dict(self.tops)}
