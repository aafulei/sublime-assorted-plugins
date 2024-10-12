# ===== Git Blame Status Bar ==================================================
# Adapted from a gist by Rodrigo Bermúdez Schettino
# https://gist.github.com/rodrigobdz/dbcdcaac6c5af7276c63ec920ba894b0
# =============================================================================

# standard
import datetime
import os
import subprocess

# sublime
import sublime
import sublime_plugin


class ShowGitBlameInStatusBarListener(sublime_plugin.EventListener):
    def on_selection_modified_async(self, view):
        # --- WRONG --------
        # if not view.sel():
        # ------------------
        # view.sel() evaluates to True even if there are no selections
        if len(view.sel()) == 0:
            return
        cursor_row = view.rowcol(view.sel()[0].begin())[0] + 1
        file = view.file_name()
        if not file:
            return
        blame = self.get_blame(cursor_row, file)
        if not blame:
            return
        parsed = self.parse_blame(blame)
        author = parsed.get("author")
        if author == "Not Committed Yet":
            author = "New"
        author_time = int(parsed.get("author-time"))
        dt = datetime.datetime.fromtimestamp(author_time)
        date_time = dt.strftime("%Y-%m-%d=%a @ %H:%M:%S")
        view.set_status("git_blame", "{} @ {}".format(author, date_time))

    def get_blame(self, line, file):
        """
        Run 'git blame --porcelain -L line,line file'.

        Return
        ------
        String or None.
        """
        try:
            # some preparation work for Windows
            startup_info = subprocess.STARTUPINFO()
            startup_info.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        except Exception as e:
            startup_info = None
        cwd = os.path.dirname(os.path.realpath(file))
        try:
            out = subprocess.check_output(
                ["git", "blame", "--porcelain",
                 "-L {0},{0}".format(line), file],
                cwd=cwd,
                startupinfo=startup_info,
                stderr=subprocess.STDOUT)
            return out.decode()
        except subprocess.CalledProcessError as e:
            error_code = e.returncode
            error_info = e.output.decode()
        except FileNotFoundError:
            pass
        except UnicodeDecodeError:
            pass
        except Exception:
            pass

    def parse_blame(self, blame):
        """
        Parse multi-line info of 'git blame --porcelain -L n,n file'.

        Return
        ------
        A dict. Each line is an item. First word is key. Rest are value.
        """
        ret = {}
        for line in blame.splitlines()[1:]:
            # ----------------------------
            # git-blame --porcelain format
            # ----------------------------
            # 1. header line, including
            #    - commit SHA
            #    - line number in original file
            #    - line number in final file
            #    - number of lines in this group (only starter line has this)
            # 2. more header info, including
            #    - author
            #    - author-time
            #    - author-tz
            #    - committer
            #    - committer-time
            #    - committer-tz
            #    ...
            # 3. [TAB] actual line content
            #
            # -------
            # Example
            # -------
            # $ git blame --porcelain -L 1,1 adapted.py
            # 3807e6fa88471401ac749cdb9b58b692c91185fa 1 1 1
            # author aafulei
            # author-mail <aaron.fu@alumni.ust.hk>
            # author-time 1634222092
            # author-tz +0800
            # committer aafulei
            # committer-mail <aaron.fu@alumni.ust.hk>
            # committer-time 1634257836
            # committer-tz +0800
            # summary Init
            # boundary
            # filename adapted.py
            #         # standard
            if line.startswith("\t"):
                return ret
            words = line.split()
            if len(words) > 1:
                ret[words[0]] = " ".join(words[1:])
        return ret
