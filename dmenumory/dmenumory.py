#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import subprocess
import json
import re
from contextlib import contextmanager
from xdg import BaseDirectory
from xdg import DesktopEntry

from  libs.dmenu import Dmenu
from  libs.dmenu import DMENU_OPTIONS


OPTIONS_DIR = os.path.expanduser("~/.dmenumory")
CACHE_FILE = os.path.expanduser("~/.dmenumory/cache.json")
OPTIONS_FILE = os.path.expanduser("~/.dmenumory/options.json")


@contextmanager
def auto_save_dict(filename):
    if os.path.exists(filename):
        mode = 'r+'
    else:
        mode = 'w'
    with open(filename, mode) as fobj:
        try:
            data = json.load(fobj)
        except IOError:
            data = {}
        yield data
        fobj.seek(0)
        json.dump(data,fobj)
        fobj.truncate()


def getInfValue(val=0):
    while True:
        yield val

class Options(dict):
    def __init__(self, filename):
        with auto_save_dict(filename) as options:
            if not options:
                options.update(self._get_default())
            super(dict, self).__init__()
            self.update(options)
    def _get_default(self):
        options = dict(zip(DMENU_OPTIONS, getInfValue('')))
        options["ignorecase"] = True
        return  options


class Dmenumory(object):
    def __init__(self,cache_file_name, options={}):
        self.options = options
        self.CACHE_FILE_NAME = cache_file_name

    def _getDesktopEntries(self):
        all_exec = set()
        entries = []
        for d in BaseDirectory.xdg_data_dirs:
            path = os.path.join(d, "applications")
            if os.path.exists(path):
                for dirpath, dirnames, filenames in os.walk(path):
                     for filename in  filenames:
                         if ".desktop" not in filename:
                             continue
                         entries.append(os.path.join(dirpath, filename))
        return entries

    def _getNewCache(self):
        return dict(zip(self._getDesktopEntries(), getInfValue()))

    def _update_cache(self, cache):
        new_cache = self._getNewCache()
        diff_old = set(cache).difference(set(new_cache))
        diff_new = set(new_cache).difference(set(cache))
        for app in diff_old:
            del cache[app]
        for app in diff_new:
            cache[app] = 0

    def run(self):
        with auto_save_dict(self.CACHE_FILE_NAME) as cache:
            if not cache:
                cache.update(self._getNewCache())
            apps = {}
            for f in cache.keys():
                app = DesktopEntry.DesktopEntry(f)
                apps[app.getName()] = app

            def runit(selected):
                if selected:
                    app = re.sub(' \(.+\)$', '', selected)
                    filename = apps[app].getFileName()
                    cache[filename] = 1+ cache.get(filename, 0)
                    cmd = re.sub("( -{1,2}\w+\W?%\w)|( %\w)",
                                 "",
                                 apps[app].getExec()).strip()
                    subprocess.Popen(cmd, shell=True)
                self._update_cache(cache)

            names = sorted(apps.values(),
                           key=lambda x: -cache[x.getFileName()]
                           or ord(x.getName()[0]))
            names = ["%s (%s)" % (a.getName(), a.getExec().split()[0]) for a in names]
            dmenu = Dmenu(names, runit)
            dmenu.set_options(**self.options)
            dmenu.run()


if __name__ == '__main__':
    if not os.path.exists(OPTIONS_DIR):
        os.mkdir(OPTIONS_DIR)
    options = Options(OPTIONS_FILE)
    dmenumory = Dmenumory(CACHE_FILE,options)
    dmenumory.run()
