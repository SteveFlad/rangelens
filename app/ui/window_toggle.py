"""Helpers for deciding which app window should be shown next."""


def should_show_optishot(*, rangelens_visible: bool, rangelens_minimized: bool) -> bool:
    """Return True when the next toggle action should reveal OptiShot."""
    return rangelens_visible and not rangelens_minimized
