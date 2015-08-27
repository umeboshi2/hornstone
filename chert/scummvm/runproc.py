import os
import subprocess
from ConfigParser import ConfigParser

main_config = ConfigParser()
main_config.read('config/main.ini')

scummvm_config = ConfigParser()
scummvm_config.read('config/scummvm.ini')

add_sdl_var = scummvm_config.getboolean('main', 'add_sdl_environ_var')
if add_sdl_var:
    os.environ['SDL_MOUSE_RELATIVE'] = '0'


def build_cmd(directory):
    mdata = scummvm_config.items('main')
    cmd = [mdata['scummvm_bin'], '-e', mdata['music_driver']]
    if scummvm_config.getboolean('main', 'full_screen'):
        cmd.append('-f')
    cmd += ['-g', mdata['graphics_scaler']]
    cmd += ['-p', directory]
    return cmd

