"""Python wrapper for dmenu

http://tools.suckless.org/dmenu/

"""
from subprocess import Popen, PIPE

DMENU_OPTIONS = {"bottom" : "-b",
                 "ignorecase" : "-i",
                 "lines" : "-l",
                 "monitor" : "-m",
                 "prompt" : "-p",
                 "font" : "-fn",
                 "normal_background" :  "-nb",
                 "normal_foreground" : "-nf",
                 "selected_background" : "-sb",
                 "selected_foreground" : "-sf"}


class BadDmenuOption(Exception):
    pass

class Dmenu(object):
    def __init__(self, items, callback):
        self.items = items
        self.callback = callback
        self.options = {}

    def set_options(self, **options):
        """Set one or more of options:
        - `items`: A list of strings to choose from.
        - `bottom`: dmenu appears at the bottom of the screen.
        - `ignorecase`: dmenu matches menu items case insensitively.
        - `lines`: dmenu lists items vertically, with the given number of lines.
        - `monitor`: dmenu appears on the given Xinerama screen.
        - `prompt`: defines the prompt to be displayed to the left of the input field.
        - `font`: defines the font or font set used.
        - `normal_background`: defines  the  normal background color (#RGB, #RRGGBB).
        - `normal_foreground`: defines the normal foreground color (#RGB, #RRGGBB).
        - `selected_background`: defines the selected background color (#RGB, #RRGGBB).
        - `selected_foreground`: defines the selected foreground color (#RGB, #RRGGBB).
        """
        for option in options:
            if option in DMENU_OPTIONS:
                self.options[option] = options[option]
            else:
                raise BadDmenuOption


    @staticmethod
    def _build_commandline(bottom=False,
                           ignorecase=False,
                           lines=None,
                           monitor=None,
                           prompt=None,
                           font=None,
                           normal_background=None,
                           normal_foreground=None,
                           selected_background=None,
                           selected_foreground=None):
        """Build the dmenu command line
        """
        options = locals()
        args = ["dmenu"]
        for o in options:
            if options[o] and o!="ignorecase":
                args.extend( (DMENU_OPTIONS[o], str(options[o])))
            elif options[o] and o=="ignorecase":
                args.append(DMENU_OPTIONS[o])
        return args

    def _dmenu(self, items,
        bottom=False,
        ignorecase=False,
        lines=None,
        monitor=None,
        prompt=None,
        font=None,
        normal_background=None,
        normal_foreground=None,
        selected_background=None,
        selected_foreground=None):
        """
        Open a dmenu to select an item
        - `items`: A list of strings to choose from.
        - `bottom`: dmenu appears at the bottom of the screen.
        - `ignorecase`: dmenu matches menu items case insensitively.
        - `lines`: dmenu lists items vertically, with the given number of lines.
        - `monitor`: dmenu appears on the given Xinerama screen.
        - `prompt`: defines the prompt to be displayed to the left of the input field.
        - `font`: defines the font or font set used.
        - `normal_background`: defines  the  normal background color (#RGB, #RRGGBB).
        - `normal_foreground`: defines the normal foreground color (#RGB, #RRGGBB).
        - `selected_background`: defines the selected background color (#RGB, #RRGGBB).
        - `selected_foreground`: defines the selected foreground color (#RGB, #RRGGBB).
        """

        cli = self._build_commandline(bottom, ignorecase, lines, monitor,
                                      prompt, font, normal_background,
                                      normal_foreground, selected_background,
                                      selected_foreground)

        input_str = "\n".join(items) + "\n"

        proc = Popen(cli, stdout=PIPE, stdin=PIPE)
        return proc.communicate(input_str)[0].strip()


    def run(self):
        self.callback(self._dmenu(self.items, **self.options))

if __name__ == '__main__':
    def f(a):
        print "U picked '%s', my Master!" % a
    dmenu = Dmenu(items=['Test', 'of', 'module'],
                  callback=f)
    dmenu.run()
