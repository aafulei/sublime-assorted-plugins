# 24/10/12 = Sat

# ===== Recenter ==============================================================
# Adapted from RecenterTopBottom by Matt Burrows
# https://github.com/mburrows/RecenterTopBottom
# =============================================================================

import sublime_plugin


class ShowAtTopOrCenterCommand(sublime_plugin.TextCommand):
    def run(self, edit, top_margin=5):
        # top_margin should be > 0
        top_margin = max(0, top_margin)
        view = self.view
        # Note: it would be wrong if you wrote -
        # ------------------
        # if not view.sel():
        # ------------------
        # because view.sel() evaluates to True even if there are no
        # selections
        if len(view.sel()) == 0:
            return
        # note that the row number here starts at 0
        cursor_row = view.rowcol(view.sel()[0].begin())[0]
        visual_reg = view.visible_region()
        target_row = view.rowcol(visual_reg.begin())[0] + top_margin
        lines_to_scroll = target_row - cursor_row
        if lines_to_scroll == 0:
            view.run_command("show_at_center")
        else:
            # Usually, lines_to_scroll < 0, and the current line shall move up
            # in the visual area. In other words, the page usually will be
            # scrolled down in order to show the current line at the top.
            view.run_command("scroll_lines", {"amount": lines_to_scroll})
        return
