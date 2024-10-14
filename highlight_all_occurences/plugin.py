# 24/10/14 = Mon

# --- imports -----------------------------------------------------------------
# standard library
import re

# sublime
import sublime
import sublime_plugin

# --- globals -----------------------------------------------------------------
g_settings_filename = "HighlightAllOccurences.sublime-settings"
g_settings = None

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


# --- public functions --------------------------------------------------------
def plugin_loaded():
    global g_settings
    g_settings = sublime.load_settings(g_settings_filename)


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
                if region == word_region:
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
        if args["setting"] == "enabled":
            enabled = g_settings.get(g_enabled_key, g_default_enabled)
            g_settings.set(g_enabled_key, not enabled)
            sublime.save_settings(g_settings_filename)
        elif args["setting"] == "instant":
            instant = g_settings.get(g_instant_key, g_default_instant)
            g_settings.set(g_instant_key, not instant)
            sublime.save_settings(g_settings_filename)
