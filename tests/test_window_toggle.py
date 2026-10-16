from app.ui.window_toggle import should_show_optishot


def test_should_show_optishot_ignores_window_focus_state_regression() -> None:
    # Regression: floating-button clicks can move focus away from RangeLens.
    assert should_show_optishot(rangelens_visible=True, rangelens_minimized=False) is True


def test_should_not_show_optishot_when_rangelens_is_minimized_or_hidden() -> None:
    assert should_show_optishot(rangelens_visible=True, rangelens_minimized=True) is False
    assert should_show_optishot(rangelens_visible=False, rangelens_minimized=False) is False
