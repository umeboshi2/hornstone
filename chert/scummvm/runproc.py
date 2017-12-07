import os
from configparser import ConfigParser, NoSectionError

main_config = ConfigParser()
main_config.read('config/main.ini')

scummvm_config = ConfigParser()
scummvm_config.read('config/scummvm.ini')

add_sdl_var = False
if 'main' in scummvm_config.sections():
    cfgopt = 'add_sdl_environ_var'
    add_sdl_var = scummvm_config['main'].getboolean(cfgopt, False)
if add_sdl_var:
    os.environ['SDL_MOUSE_RELATIVE'] = '0'


def build_cmd(directory):
    mdata = scummvm_config.items('main')
    cmd = [mdata['scummvm_bin'], '-e', mdata['music_driver']]
    try:
        if scummvm_config.getboolean('main', 'full_screen'):
            cmd.append('-f')
    except NoSectionError:
        pass
    cmd += ['-g', mdata['graphics_scaler']]
    cmd += ['-p', directory]
    return cmd
