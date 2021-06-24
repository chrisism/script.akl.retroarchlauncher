﻿# -*- coding: utf-8 -*-
#
# Retroarch Launcher plugin for AEL
#
# --- Python standard library ---
from __future__ import unicode_literals
from __future__ import division

import sys
import logging
import json

try:
    from urlparse import urlsplit, parse_qs
except ImportError:
    from urllib.parse import urlsplit, parse_qs

# AEL main imports
from globals import *
from launchers import *
from utils import kodilogging, text, kodi
import settings

from resources.lib.launcher import RetroarchLauncher

kodilogging.config()
logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------------------------
# This is the plugin entry point.
# ---------------------------------------------------------------------------------------------
def run_plugin():
    # --- Some debug stuff for development ---
    logger.debug('------------ Called Advanced Emulator Launcher Plugin: Retroarch Launcher ------------')
    logger.debug('addon.id         "{}"'.format(addon_id))
    logger.debug('addon.version    "{}"'.format(addon_version))
    for i in range(len(sys.argv)): logger.debug('sys.argv[{}] "{}"'.format(i, sys.argv[i]))

    path = urlsplit(sys.argv[0]).path
    path = path.rstrip('/')    
    args = parse_qs(sys.argv[2][1:])
    
    if path.lower() == '/launcher/retroarch':
        launch_rom(args)
    elif path.lower() == '/launcher/retroarch/configure':
        configure_launcher(args)
    else:
        kodi.notify('Can only be used as plugin for AEL')
    
    logger.debug('Advanced Emulator Launcher Plugin:  Retroarch Launcher -> exit')

def launch_rom(args):
    logger.debug('Retroarch Launcher: Starting ...')
    launcher_settings   = json.loads(args['settings'][0])
    arguments           = args['args'][0]

    execution_settings = ExecutionSettings()
    execution_settings.delay_tempo = settings.getSettingAsInt('delay_tempo')
    execution_settings.display_launcher_notify = settings.getSettingAsBool('display_launcher_notify')
    execution_settings.is_non_blocking = True if args['is_non_blocking'][0] == 'true' else False
    execution_settings.media_state_action = settings.getSettingAsInt('media_state_action')
    execution_settings.suspend_audio_engine = settings.getSettingAsBool('suspend_audio_engine')
    execution_settings.suspend_screensaver = settings.getSettingAsBool('suspend_screensaver')
            
    executor_factory = get_executor_factory()
    launcher = RetroarchLauncher(executor_factory, execution_settings, launcher_settings)
    launcher.launch(arguments)

def configure_launcher(args):
    logger.debug('Retroarch Launcher: Configuring ...')

    romset_id:str   = args['romset_id'][0] if 'romset_id' in args else None
    launcher_id:str = args['launcher_id'][0] if 'launcher_id' in args else None
    settings:str    = args['settings'][0] if 'settings' in args else None
    
    launcher_settings = json.loads(settings)    
    launcher = RetroarchLauncher(None, None, launcher_settings)
    if launcher_id is None and launcher.build():
        launcher.store_launcher_settings(romset_id)
        return
    
    if launcher_id is not None and launcher.edit():
        launcher.store_launcher_settings(romset_id, launcher_id)
        return
    
    kodi.notify_warn('Cancelled creating launcher')

try:
    run_plugin()
except Exception as ex:
    message = text.createError(ex)
    logger.fatal(message)
    