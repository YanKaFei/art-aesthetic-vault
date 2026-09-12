#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
clip_embed.py —— 用 CLIP 的图像编码器算 512 维嵌入。

## 为什么加它

前两条路都做完了，各有短板：

    T3 Vision featureprint（768 维）  图像↔流派 Top-1 30.6%
    T1 客观维度（31 维）              图像↔流派 Top-1 13.2%

Vision 是苹果为**物体/场景识别**训练的；T1 只测亮度色彩笔触。
CLIP 是**图文对比学习**出来的，训练目标就是「让描述和图像对上」——
理论上更接近「这张图属于哪个流派」这件事。

## 为什么用 ONNX 不用 PyTorch

CLIP 的标准用法是 `transformers` + `torch`，但 torch 装完约 2.5GB。
onnxruntime 只用了约 15MB，模型是量化版（视觉 85MB + 文本 61MB），
推理速度在 CPU 上够用（622 张约半分钟）。

## 模型

`Xenova/clip-vit-base-patch32` 的量化 ONNX，放在 `_scripts/vendor/clip/`
（vendor/ 已 gitignore，不会进仓库）。首次运行前需要下载：

    python3 clip_embed.py download

用法
    python3 clip_embed.py download          # 下载模型（约 150MB）
    python3 clip_embed.py build             # 算全库嵌入并缓存
    python3 clip_embed.py features <图>      # 单张嵌入
"""

import argparse
import json
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
VAULT = os.path.dirname(HERE)
IMAGES = os.path.join(VAULT, "99-附件", "images")
MODEL_DIR = os.path.join(HERE, "vendor", "clip")
VISION_ONNX = os.path.join(MODEL_DIR, "vision.onnx")
TEXT_ONNX = os.path.join(MODEL_DIR, "text.onnx")
PREPROC = os.path.join(MODEL_DIR, "preprocessor_config.json")
TOKENIZER = os.path.join(MODEL_DIR, "tokenizer.json")
CACHE = os.path.join(HERE, "_data", "clip_cache.json")
HF = "https://huggingface.co/Xenova/clip-vit-base-patch32/resolve/main"

EXTS = (".jpg", ".jpeg", ".png", ".webp", ".tif", ".tiff", ".bmp")
BATCH = 16

for _c in (os.path.join(HERE, "vendor", "libs"), os.path.expanduser("~/.artvault/deps"),
           os.environ.get("ARTVAULT_DEPS", "")):
    if _c and os.path.isdir(_c) and _c not in sys.path:
        sys.path.insert(0, _c)

_SESS = None
_NP = None
_PIL = None


def available():
    """返回 None 表示可用，否则返回原因字符串。"""
    if not os.path.exists(VISION_ONNX):
        return "缺少模型 %s（跑 python3 clip_embed.py download）" % VISION_ONNX
    try:
        import numpy  # noqa: F401
        from PIL import Image  # noqa: F401
    except Exception as e:
        return "缺少 numpy / Pillow：%s" % e
    try:
        import onnxruntime  # noqa: F401
    except Exception:
        return "缺少 onnxruntime（pip3 install --target ./vendor/libs onnxruntime）"
    return None


def _load():
    global _SESS, _NP, _PIL
    if _SESS is None:
        import numpy as np
        import onnxruntime as ort
        from PIL import Image
        _NP, _PIL = np, Image
        _SESS = ort.InferenceSession(VISION_ONNX, providers=["CPUExecutionProvider"])
    return _SESS, _NP, _PIL


def download(verbose=True):
    """下载量化 ONNX 模型、预处理配置与分词器。"""
    import urllib.request
    os.makedirs(MODEL_DIR, exist_ok=True)
    files = [(HF + "/onnx/vision_model_quantized.onnx", VISION_ONNX),
             (HF + "/onnx/text_model_quantized.onnx", TEXT_ONNX),
             (HF + "/preprocessor_config.json", PREPROC),
             (HF + "/tokenizer.json", TOKENIZER)]
    for url, dst in files:
        if os.path.exists(dst) and os.path.getsize(dst) > 1024:
            if verbose:
                print("  已存在，跳过 %s" % os.path.basename(dst))
            continue
        if verbose:
            print("  下载 %s …" % os.path.basename(dst))
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "artvault"})
            with urllib.request.urlopen(req, timeout=900) as a, open(dst, "wb") as b:
                while True:
                    chunk = a.read(1 << 20)
                    if not chunk:
                        break
                    b.write(chunk)
            if verbose:
                print("    ✓ %.1f MB" % (os.path.getsize(dst) / 1048576.0))
        except Exception as e:
            print("    ✗ 失败：%s" % str(e)[:80])
            return False
    return True


def text_available():
    """文本编码是否可用（零样本命名要用）。"""
    if not os.path.exists(TEXT_ONNX):
        return "缺少 %s（跑 python3 clip_embed.py download）" % TEXT_ONNX
    if not os.path.exists(TOKENIZER):
        return "缺少 %s（跑 python3 clip_embed.py download）" % TOKENIZER
    try:
        import tokenizers  # noqa: F401
        import numpy  # noqa: F401
    except Exception as e:
        return "缺少 tokenizers / numpy：%s" % e
    try:
        import onnxruntime  # noqa: F401
    except Exception:
        return "缺少 onnxruntime"
    return None


_TOK = None
_TSESS = None


def _load_text():
    global _TOK, _TSESS
    if _TSESS is None:
        import onnxruntime as ort
        from tokenizers import Tokenizer
        _TOK = Tokenizer.from_file(TOKENIZER)
        # CLIP 的文本塔固定 77 个 token，必须开 padding 与截断
        _TOK.enable_padding(length=77)
        _TOK.enable_truncation(max_length=77)
        _TSESS = ort.InferenceSession(TEXT_ONNX, providers=["CPUExecutionProvider"])
    return _TOK, _TSESS


def text_embed(texts, verbose=False):
    """把文本编码成 512 维（已 L2 归一化），与图像嵌入同一空间。

    同一空间意味着可以直接点积比较 —— 这正是 CLIP 的用处：
    用一句**文字**去检索图像，不需要为流派训练任何分类器。
    """
    reason = text_available()
    if reason:
        if verbose:
            print("CLIP 文本塔不可用：%s" % reason)
        return None
    import numpy as np
    tok, sess = _load_text()
    encs = tok.encode_batch(list(texts))
    ids = np.array([e.ids for e in encs], dtype="i8")
    mask = np.array([e.attention_mask for e in encs], dtype="i8")
    names = [i.name for i in sess.get_inputs()]
    feed = {}
    for n in names:
        if "input_ids" in n:
            feed[n] = ids
        elif "attention_mask" in n:
            feed[n] = mask
    out_name = sess.get_outputs()[0].name
    y = np.asarray(sess.run([out_name], feed)[0], dtype="f4")
    n = np.linalg.norm(y, axis=1, keepdims=True)
    n[n == 0] = 1.0
    return y / n



def _preprocess(paths):
    """CLIP 预处理：短边缩到 224 → 中心裁剪 224 → 归一化 → NCHW float32。

    与 transformers 的 CLIPImageProcessor 对齐；顺序不能反
    （先裁剪再缩放会改变构图，和训练时不一致）。
    """
    import numpy as np
    from PIL import Image
    cfg = json.load(open(PREPROC, encoding="utf-8")) if os.path.exists(PREPROC) else {}
    size = 224
    mean = np.array(cfg.get("image_mean", [0.48145466, 0.4578275, 0.40821073]), dtype="f4")
    std = np.array(cfg.get("image_std", [0.26862954, 0.26130258, 0.27577711]), dtype="f4")

    out = np.zeros((len(paths), 3, size, size), dtype="f4")
    for i, p in enumerate(paths):
        try:
            im = Image.open(p).convert("RGB")
        except Exception:
            continue
        w, h = im.size
        s = size / float(min(w, h))
        im = im.resize((max(size, int(round(w * s))), max(size, int(round(h * s)))),
                       Image.BICUBIC)
        w, h = im.size
        left, top = (w - size) // 2, (h - size) // 2
        im = im.crop((left, top, left + size, top + size))
        a = np.asarray(im, dtype="f4") / 255.0
        a = (a - mean) / std
        out[i] = a.transpose(2, 0, 1)
    return out


def embed_batch(paths, verbose=False):
    """返回 {路径: 512 维向量}。任何一张失败只跳过它。"""
    reason = available()
    if reason:
        if verbose:
            print("CLIP 不可用：%s" % reason)
        return {}
    sess, np, _Image = _load()
    name = sess.get_inputs()[0].name
    out_name = sess.get_outputs()[0].name
    res = {}
    for i in range(0, len(paths), BATCH):
        chunk = paths[i:i + BATCH]
        x = _preprocess(chunk)
        try:
            y = sess.run([out_name], {name: x})[0]
        except Exception as e:
            if verbose:
                print("  推理失败（批次 %d）：%s" % (i, str(e)[:60]))
            continue
        y = np.asarray(y, dtype="f4")
        # L2 归一化，让余弦相似度等价于点积
        n = np.linalg.norm(y, axis=1, keepdims=True)
        n[n == 0] = 1.0
        y = y / n
        for j, p in enumerate(chunk):
            res[p] = [float(v) for v in y[j]]
        if verbose and (i // BATCH) % 10 == 0:
            print("    %d/%d" % (min(i + BATCH, len(paths)), len(paths)))
    return res


def iter_images():
    for root, _d, files in os.walk(IMAGES):
        for fn in sorted(files):
            if fn.lower().endswith(EXTS):
                yield os.path.relpath(os.path.join(root, fn), VAULT).replace(os.sep, "/")


def load_cache():
    if os.path.exists(CACHE):
        try:
            return json.load(open(CACHE, encoding="utf-8"))
        except Exception:
            return {}
    return {}


def build(force=False, verbose=True):
    reason = available()
    if reason:
        if verbose:
            print("CLIP 不可用：%s" % reason)
        return None
    files = list(iter_images())
    cache = {} if force else load_cache()
    todo = [f for f in files if f not in cache]
    if verbose:
        print("库中图片 %d 张；已缓存 %d 张，需计算 %d 张"
              % (len(files), len(cache), len(todo)))
    t0 = time.time()
    if todo:
        got = embed_batch([os.path.join(VAULT, f) for f in todo], verbose=verbose)
        for ap, v in got.items():
            cache[os.path.relpath(ap, VAULT).replace(os.sep, "/")] = v
    live = set(files)
    dropped = [k for k in cache if k not in live]
    for k in dropped:
        del cache[k]
    os.makedirs(os.path.dirname(CACHE), exist_ok=True)
    json.dump(cache, open(CACHE, "w", encoding="utf-8"), ensure_ascii=False)
    if verbose:
        print("✓ 缓存 %d 张，用时 %.0fs%s"
              % (len(cache), time.time() - t0,
                 ("，清理 %d 张" % len(dropped)) if dropped else ""))
    return cache


def main():
    ap = argparse.ArgumentParser(description="CLIP 图像嵌入（ONNX，无需 PyTorch）")
    sub = ap.add_subparsers(dest="cmd")
    sub.add_parser("download", help="下载量化模型（约 150MB）")
    p = sub.add_parser("build", help="算全库嵌入并缓存")
    p.add_argument("--force", action="store_true")
    p = sub.add_parser("features", help="单张图的 512 维嵌入")
    p.add_argument("target")
    a = ap.parse_args()

    if a.cmd == "download":
        return 0 if download() else 1
    if a.cmd == "build":
        return 0 if build(force=a.force) else 1
    if a.cmd == "features":
        v = embed_batch([a.target], verbose=True).get(a.target)
        if not v:
            print("失败：%s" % (available() or "读取失败"))
            return 1
        print("维度 %d" % len(v))
        print("前 8 维：%s" % " ".join("%.4f" % x for x in v[:8]))
        return 0
    ap.print_help()
    return 0


if __name__ == "__main__":
    sys.exit(main())
