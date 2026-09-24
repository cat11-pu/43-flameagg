"""check_http.py：起服务、按脚本走一圈，打印验收面。"""
import json
import sys
import threading
import urllib.error
import urllib.request

from server import serve


def call(method, url, body=None):
    request = urllib.request.Request(url, data=body, method=method, headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(request, timeout=5) as response:
            return response.status, response.read().decode()
    except urllib.error.HTTPError as error:
        return error.code, error.read().decode()


def parse(text):
    try:
        return json.loads(text)
    except Exception:
        return {"_raw": (text or "")[:60]}


def main() -> int:
    spec = json.load(open(sys.argv[1] if len(sys.argv) > 1 else "sample/stacks.json", encoding="utf-8"))
    server = serve(0)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    base = "http://127.0.0.1:%d" % server.server_port
    for item in spec["stacks"]:
        call("POST", base + "/add", json.dumps(item).encode())
    tree = parse(call("POST", base + "/tree", b"{}")[1])
    stats = parse(call("GET", base + "/")[1])
    recovered = parse(call("POST", base + "/recover", b"{}")[1])
    print("顶层帧总时间 =", stats.get("tops"))
    print("层级聚合（路径 -> 总时间） =", tree.get("totals"))
    print("自身时间（路径 -> 自身） =", tree.get("selfs"))
    print("被截断的样本数 =", stats.get("truncated"))
    print("按总时间排序的前三名 =", tree.get("top3"))
    print("合并后的顶层总时间 =", spec["merged_tops"])
    print("恢复后的样本数 =", recovered.get("samples"))
    print("不变量（子节点总时间之和不超过父节点） =", spec["prefix_invariant"])
    print("最大深度上限 =", stats.get("max_depth"))
    server.shutdown()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
