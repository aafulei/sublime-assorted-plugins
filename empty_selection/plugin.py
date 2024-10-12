# 23/02/26 = Sun

# Empty Selection
# ---------------
# based on a forum post by C0D312:
# https://www.sublimetext.com/forum/viewtopic.php?f=2&t=4716#p21219

# Note that the context conditions are required in the key binding rule -
"""
{
 "keys": [
     "escape"
 ],
 "command": "deselect",
 "context": [
     {
         "key": "num_selections",
         "operand": 1
     },
     {
         "key": "selection_empty",
         "operand": false,
     }
 ]
},
"""
# because this text command should only be called when
# - (1) there is only 1 selection and
# - (2) that selection is nonempty.
# - In other cases,
#   - when the number of selections is not 1, the built-in command
#     single_selection should be called;
#   - when there is 1 selection but the selection is empty (i.e. a single
#     caret), the built-in commands for hiding panels and so on should be
#     called, depending on the context.

# - [TextCommand]         ... sublime_plugin.TextCommand
#   - [View]              ... sublime_plugin.TextCommand.view
#       - [Selection]     ... sublime_plugin.TextCommand.view.sel()
#           - [Region]    ... sublime_plugin.TextCommand.view.sel()[0]
#               - [Point] ... sublime_plugin.TextCommand.view.sel()[0].b

#   - sublime_plugin.TextCommand
#       - A TextCommand is a Command instantiated once per View.
#   - sublime.View
#       - A View represents a view into a text Buffer. Note that multiple views
#         may refer to the same Buffer, but they have their own unique
#         selection and geometry.
#   - sublime.Selection
#       - Maintains a set of sorted non-overlapping Regions. A selection may be
#         empty.
#   - sublime.Region
#       - A singular selection region. This region has a order - b may be
#         before or at a.
#   - sublime.Point
#       - Represents the offset from the beginning of the editor buffer.

import sublime_plugin


class EmptySelectionCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        # "sublime.Region.b" is always the location of the caret. It may be
        #  less than "sublime.Region.a".
        caret_point = self.view.sel()[0].b
        self.view.sel().clear()
        self.view.sel().add(caret_point)
