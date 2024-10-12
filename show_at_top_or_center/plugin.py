# 24/10/12 = Sat

import sublime_plugin

g_last_row = dict()
g_show_at_top = dict()


class ShowAtTopOrCenterListener(sublime_plugin.ViewEventListener):
    def on_selection_modified_async(self):
        global g_last_row
        global g_show_at_top
        view = self.view
        vid = view.id()
        selections = view.sel()
        if len(selections) == 0:
            return
        cursor_row = view.rowcol(selections[0].begin())[0]
        if vid not in g_last_row:
            g_last_row[vid] = cursor_row
            return
        if cursor_row != g_last_row[vid]:
            g_last_row[vid] = cursor_row
            # reset the next position to show at to the top
            g_show_at_top[vid] = True


class ShowAtTopOrCenterCommand(sublime_plugin.TextCommand):
    def run(self, edit, top_margin=5):
        global g_show_at_top
        # top_margin should be > 0
        view = self.view
        vid = view.id()
        if vid not in g_show_at_top:
            g_show_at_top[vid] = True
        if g_show_at_top[vid]:
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
            # Usually, lines_to_scroll < 0, and the current line shall move up
            # in the visual area. In other words, the page usually will be
            # scrolled down in order to show the current line at the top.
            view.run_command("scroll_lines", {"amount": lines_to_scroll})
        else:
            view.run_command("show_at_center")
        # toggle the next position to show at: top <==> center
        g_show_at_top[vid] = not g_show_at_top[vid]
