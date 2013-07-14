#!/usr/bin/env python

import os
import subprocess
import json
from contextlib import contextmanager

from  dmenu import Dmenu
from  dmenu import DMENU_OPTIONS

OPTIONS_DIR = os.path.expanduser("~/.dmenumory")
CACHE_FILE = os.path.expanduser("~/.dmenumory/cache.json")
OPTIONS_FILE = os.path.expanduser("~/.dmenumory/options.json")

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


def get_inf_value(val=0):
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
        return  dict(zip(DMENU_OPTIONS, get_inf_value('')))


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
        return dict(zip(self._get_app_list(), get_inf_value()))

    def _cache_to_app_list(self, cache):
        return sorted(cache, lambda x,y: cache[y] - cache[x])

    def _update_cache(self, cache):
        new_cache = self._get_new_cache()
        diff_old = set(cache).difference(set(new_cache))
        diff_new = set(new_cache).difference(set(cache))
        for app in diff_old:
            del cache[app]
        for app in diff_new:
            cache[app] = 0

    def run(self):
        with auto_save_dict(self.cache_file_name) as cache:
            if not cache:
                cache.update(self._get_new_cache())
            def runit(app):
                if app:
                    cache[app] = 1+ cache.get(app, 0)
                    subprocess.Popen(app)
                    self._update_cache(cache)

            dmenu = Dmenu(sorted(cache, lambda x,y: cache[y] - cache[x]), runit)
            dmenu.set_options(**self.options)
            dmenu.run()


if __name__ == '__main__':
    if not os.path.exists(OPTIONS_DIR):
        os.mkdir(OPTIONS_DIR)
    options = Options(OPTIONS_FILE)
    dmenumory = Dmenumory(CACHE_FILE,options)
    dmenumory.run()
