MAX_ITERATIONS = 5
MAX_REVIEW_LOOPS = 3


class CostGuard:
    def check_iterations(self, state: dict) -> None:
        test_iterations = state.get("test_iterations", 0)
        review_iterations = state.get("review_iterations", 0)

        if test_iterations >= MAX_ITERATIONS:
            raise RuntimeError(
                f"Exceeded max test iterations ({MAX_ITERATIONS}). Aborting to prevent runaway costs."
            )
        if review_iterations >= MAX_REVIEW_LOOPS:
            raise RuntimeError(
                f"Exceeded max review loops ({MAX_REVIEW_LOOPS}). Aborting to prevent runaway costs."
            )
