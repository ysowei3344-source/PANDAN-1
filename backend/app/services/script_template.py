import math

from ..schemas import Product

SHOT_SECONDS = 7


def _product_highlight(product: Product | None) -> str:
    if product is None:
        return "这台房车"
    for text in (product.standard_config, product.optional_config, product.chassis_info):
        if text.strip():
            return f"{product.name}（{text.strip().splitlines()[0]}）"
    return product.name


def generate_script(product: Product | None, duration_seconds: int) -> tuple[str, list[dict]]:
    """Template-only placeholder — no real LLM call. Splits duration_seconds
    into SHOT_SECONDS-long shots (last one takes the remainder) and fills
    each with a generic narration/visual_desc mentioning the product. Swap
    this function's body for a real LLM call later; callers only depend on
    the (script_text, shots) return shape."""

    highlight = _product_highlight(product)
    shot_count = max(1, math.ceil(duration_seconds / SHOT_SECONDS))

    shots: list[dict] = []
    lines: list[str] = []
    for i in range(shot_count):
        start = i * SHOT_SECONDS
        end = min(start + SHOT_SECONDS, duration_seconds)
        if i == 0:
            narration = f"大家好，今天带大家看看{highlight}。"
            visual = f"数字人正对镜头打招呼，{highlight}停在身后作为背景。"
        elif i == shot_count - 1:
            narration = "喜欢的话欢迎私信咨询，我们下期再见。"
            visual = f"数字人走到{highlight}旁边挥手告别。"
        else:
            narration = f"这里可以看到{highlight}的实际使用场景。"
            visual = f"数字人在{highlight}边讲解边比划，镜头在人和车之间切换。"

        shots.append(
            {
                "index": i,
                "start_sec": start,
                "end_sec": end,
                "narration": narration,
                "visual_desc": visual,
                "status": "draft",
                "video_url": None,
                "jimeng_task_id": None,
                "error_message": None,
                "generated_at": None,
            }
        )
        lines.append(f"[{start}-{end}s] {narration}")

    return "\n".join(lines), shots
