# 24/10/14 = Mon

# --- imports -----------------------------------------------------------------
# standard library
import re

# sublime
import sublime
import sublime_plugin

# --- globals -----------------------------------------------------------------
g_plugin_name = "Highlight All Occurences"
g_settings_filename = "HighlightAllOccurences.sublime-settings"
g_settings = sublime.load_settings(g_settings_filename)

g_default_color_scope = "string"
g_default_enabled = True
g_default_instant = False

g_color_scope_key = "color_scope"
g_enabled_key = "enabled"
g_instant_key = "instant"
g_region_key = "highlight_all_occurences"


# --- internal functions ------------------------------------------------------
def is_valid_identifier(string):
    pattern = r"^[A-za-z][A-Za-z0-9_]*$"
    return bool(re.match(pattern, string))


# --- commands ----------------------------------------------------------------
class HighlightAllOccurencesListener(sublime_plugin.ViewEventListener):
    def on_selection_modified_async(self):
        view = self.view
        view.erase_regions(key=g_region_key)
        if not g_settings.get(key=g_enabled_key, default=g_default_enabled):
            return
        selections = view.sel()
        regions_to_highlight = []
        for region in selections:
            # if region is a range, i.e. selection has something in it
            if len(region) > 0:
                string = view.substr(region)
                regex = re.escape(string)
                word_region = view.word(region)
                # The region here might be a leftward selection with a > b:
                #   region=Region(3199, 3192) vs word_region=Region(3192, 3199)
                # We could normalize it, similar to taking the absolute value
                # of a negative number. However, a simpler approach is to
                # compare the lengths.
                if len(region) == len(word_region):
                    print(f"{region=} vs {word_region=}")
                    regex = "\\b{}\\b".format(regex)
                regions_to_highlight.extend(view.find_all(regex))
            # if region is a point, i.e. selection is empty
            elif g_settings.get(key=g_instant_key, default=g_default_instant):
                word_region = view.word(region)
                word = view.substr(word_region)
                if not is_valid_identifier(word):
                    continue
                regex = "\\b{}\\b".format(re.escape(word))
                regions_to_highlight.extend(view.find_all(regex))
        color_scope = g_settings.get(key=g_color_scope_key,
                                     default=g_default_color_scope)
        view.add_regions(key=g_region_key, regions=regions_to_highlight,
                         scope=color_scope)


class HighlightAllOccurencesToggleSettingCommand(
        sublime_plugin.ApplicationCommand):
    def run(self, **args):
        global g_settings
        if "setting" not in args:
            return
        if args["setting"] not in ("enabled", "instant"):
            return
        msg = "{} ".format(g_plugin_name)
        if args["setting"] == "enabled":
            enabled = not g_settings.get(g_enabled_key, g_default_enabled)
            g_settings.set(g_enabled_key, enabled)
            msg += "[{}]".format("Enabled" if enabled else "Disabled")
        else:
            instant = not g_settings.get(g_instant_key, g_default_instant)
            g_settings.set(g_instant_key, instant)
            msg += "[{}]".format("Instant" if instant else "On Select")
        sublime.save_settings(g_settings_filename)
        sublime.status_message(msg)
