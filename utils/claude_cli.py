import subprocess
import logging
import threading
import os

log = logging.getLogger(__name__)


def _stream_output(stream, collector: list, label: str) -> None:
    for line in iter(stream.readline, ""):
        line = line.rstrip("\n")
        if line:
            log.info("[claude %s] %s", label, line)
            collector.append(line)
    stream.close()


def run_prompt(prompt: str, timeout: int = 120, cwd: str = None, extra_args: list = None) -> str:
    cmd = ["claude", "--print"] + (extra_args or []) + [prompt]
    log.info("Running: %s", " ".join(cmd[:3]) + " ...")

    env = os.environ.copy()
    env.pop("ANTHROPIC_API_KEY", None)

    proc = subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        cwd=cwd,
        env=env,
    )

    stdout_lines = []
    stderr_lines = []

    t_out = threading.Thread(target=_stream_output, args=(proc.stdout, stdout_lines, "out"))
    t_err = threading.Thread(target=_stream_output, args=(proc.stderr, stderr_lines, "err"))
    t_out.start()
    t_err.start()

    try:
        proc.wait(timeout=timeout)
    except subprocess.TimeoutExpired:
        proc.kill()
        raise RuntimeError(f"claude CLI timed out after {timeout}s")
    finally:
        t_out.join()
        t_err.join()

    if proc.returncode != 0:
        raise RuntimeError(f"claude CLI error (rc={proc.returncode}): {chr(10).join(stderr_lines)}")

    return "\n".join(stdout_lines).strip()
