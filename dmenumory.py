#!/usr/bin/env python

import os
from dmenu import Dmenu
import subprocess
import json
from contextlib import contextmanager


CACHE_FILE = "/home/robal/.dmenumory"


@contextmanager
def auto_save_dict(filename):
    if os.path.exists(filename):
        mode = 'r+'
    else:
        mode = 'w'
    with file(filename, mode) as fobj:
        try:
            data = json.load(fobj)
        except IOError:
            data = {}
        yield data
        fobj.seek(0)
        json.dump(data,fobj)
        fobj.truncate()

def get_zero():
    while True:
        yield 0

class Dmenumory(object):
    def __init__(self,cache_file_name, options={}):
        self.options = options
        self.cache_file_name = cache_file_name

    def _get_app_list(self):
        all_exec = set()
        for path in os.environ["PATH"].split(':'):
            if os.path.exists(path):
                all_exec.update([app for app in os.listdir(path)
                                 if os.access(os.path.join(path, app),
                                              os.X_OK)])
        return list(all_exec)

    def _get_new_cache(self):
        return dict(zip(self._get_app_list(),get_zero()))

    def run(self):
        app_list = self._get_app_list()
        with auto_save_dict(self.cache_file_name) as cache:
            for app in cache:
                try:
                    app_list.remove(app)
                except ValueError:
                    pass
            print cache
            app_list = sorted(cache, lambda x,y: cache[y] - cache[x]) + app_list

            def runit(app):
                if app:
                    cache[app] = 1+ cache.get(app, 0)
                    subprocess.Popen(app)

            dmenu = Dmenu(app_list, runit)
            dmenu.set_options(**self.options)
            dmenu.run()


if __name__ == '__main__':
    dmenumory = Dmenumory(CACHE_FILE)
    dmenumory.run()
