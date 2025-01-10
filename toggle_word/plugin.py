# 23/02/18 = Sat
# 24/10/12 = Sat
# 24/10/14 = Mon

"""
Toggle Words
============
A Sublime Text plugin for toggling and cycling through words.

This plugin allows users to switch between predefined words or cycle through
a list of words using keyboard shortcuts. For example,

- Toggle between "True" and "False".
- Cycle through "Red", "Blue", and "Green".

The word list is customizable via the settings file, allowing users to define
their own words for toggling or cycling through. The default word list includes
variations of "True" and "False".

Author: Aaron Fu Lei
Date: Feb 18, 2023; Oct 12-14, 2024
License: MIT
"""

# --- imports -----------------------------------------------------------------
# standard
import re

# sublime
import sublime
import sublime_plugin

# --- globals -----------------------------------------------------------------
g_plugin_name = "Toggle Words"
g_plugin_tag = "toggle-words"

g_default_word_list = [["True", "False"], ["TRUE", "FALSE"], ["true", "false"]]
g_settings_filename = "ToggleWords.sublime-settings"
g_word_list_key = "word_list"

g_settings = sublime.load_settings(g_settings_filename)
g_word_list = g_default_word_list


# --- internal functions ------------------------------------------------------
def log_error(*args):
    """
    Log an error message to the console.

    This function prefixes the message with the plugin name and prints it to
    the console.

    Args:
        *args: Variable length argument list for error messages.
    """
    print("({}) [Error]".format(g_plugin_name), *args)


def log_info(*args):
    """
    Log an informational message to the console.

    This function prefixes the message with the plugin name and prints it to
    the console.

    Args:
        *args: Variable length argument list for informational messages.
    """
    print("({}) [Info]".format(g_plugin_name), *args)


def check_word_list(word_list):
    """
    Validate the word list structure.

    This function checks if the provided word list is a list of lists of
    strings, ensuring that each sublist contains at least two unique string
    elements. It also verifies that each string meets specific criteria such as
    being nonempty, consisting only of letters, numbers, or underscores, and,
    as a whole, not containing duplicates.

    Args:
        word_list (list): The list of words to validate.

    Returns:
        bool: True if the word list is valid, False otherwise.
    """
    if not isinstance(word_list, list):
        log_error("Word list not a list.")
        return False
    all_words = set()
    for lst in word_list:
        if not isinstance(lst, list):
            log_error("Word list not a list of lists.")
            return False
        if len(lst) < 2:
            log_error("Length-{} list found in word list.".format(len(lst)))
            return False
        for word in lst:
            if not isinstance(word, str):
                log_error("Non-str element found in word list.")
                return False
            if len(word) == 0:
                log_error("Empty string found in word list.")
                return False
            if not re.match(r"^[A-Za-z0-9_]+$", word):
                log_error("Bad string \"{}\" found in word list.".format(word),
                          "Accept only letters, numbers and underscores.")
                return False
            if word in all_words:
                log_error("Duplicate string \"{}\" found in word list."
                          .format(word))
                return False
            all_words.add(word)
    return True


def load_word_list():
    """
    Load the word list settings from the configuration file.

    This function attempts to load the word list from the specified settings
    file. If the word list is not found or is invalid, the default word list
    will be used. The function is also registered as a callback for
    settings.add_on_change(), allowing it to be called whenever the local
    settings file is modified.

    Returns:
        None
    """
    global g_word_list
    g_word_list = g_default_word_list
    if not g_settings.has(g_word_list_key):
        log_error("Word list not found. Will use default word list.")
    elif not check_word_list(g_settings.get(g_word_list_key)):
        log_error("Word list is invalid. Will use default word list.")
    else:
        g_word_list = g_settings.get(g_word_list_key)
    log_info("Using word list:", g_word_list)


def get_word_to_swap_with(old_word):
    """
    Get the next word to swap with.

    Given an old word, this function finds the next word in the predefined list
    to toggle or cycle to.

    Args:
        old_word (str): The current word to swap.

    Returns:
        str: The next word to swap with, or an empty string if not found.
    """
    for i, lst in enumerate(g_word_list):
        for j, target in enumerate(lst):
            if old_word == target:
                new_word = lst[(j + 1) % len(lst)]
                return new_word
    return ""


# --- public functions --------------------------------------------------------
def plugin_loaded():
    """
    Initialize plugin settings when the plugin is loaded.

    This function is called when the plugin is loaded and is responsible for
    loading the settings.

    Returns:
        None
    """
    load_word_list()
    g_settings.add_on_change(tag=g_plugin_tag, callback=load_word_list)


# --- commands ----------------------------------------------------------------
class ToggleWordCommand(sublime_plugin.TextCommand):
    """
    Command to toggle a word in the active view.

    This command replaces the selected word with the next word in the
    predefined list of words.
    """

    def run(self, edit):
        """
        Execute the toggle word command.

        This method collects the current selections, expands them to words if
        empty, and replaces the words with their toggled counterparts.

        Args:
            edit: The edit object used to modify the view.

        Returns:
            None
        """
        old_selections = list(self.view.sel())
        to_modify = []
        # 1. collect old words, expanding cursors to words if needed
        for region in old_selections:
            word_region = self.view.word(region) if region.empty() else region
            old_word = self.view.substr(word_region)
            new_word = get_word_to_swap_with(old_word)
            if new_word:
                b = word_region.begin()
                e = word_region.end()
                to_modify.append((b, e, new_word))
        # 2. populate new words
        to_modify = sorted(list(set(to_modify)))
        offset = 0
        for b, e, new_word in to_modify:
            region = sublime.Region(b + offset, e + offset)
            self.view.replace(edit, region, new_word)
            old_word_len = e - b
            offset += len(new_word) - old_word_len
        return
