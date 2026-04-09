import re


def task_slug(task: dict) -> str:
    short_id = task.get("idShort", task.get("id", "0"))
    name = task.get("name", "task")
    slug = name.lower()
    slug = re.sub(r"[^\w\s-]", "", slug)
    slug = re.sub(r"[\s_]+", "-", slug).strip("-")
    return f"{short_id}-{slug}"
