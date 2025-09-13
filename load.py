import logging
import os
import tkinter as tk
import tkinter.messagebox as confirmDialog
from pathlib import Path
from semantic_version import Version

from config import appname  # type: ignore

from SpanshRouter.context import Context
from SpanshRouter.SpanshRouter import SpanshRouter


# A Logger is used per 'found' plugin to make it easy to include the plugin's
# folder name in the logging output format.
# NB: plugin_name here *must* be the plugin's folder name as per the preceding
#     code, else the logger won't be properly set up.
plugin_name = os.path.basename(os.path.dirname(__file__))
logger = logging.getLogger(f'{appname}.{plugin_name}')

# If the Logger has handlers then it was already set up by the core code, else
# it needs setting up here.
if not logger.hasHandlers():
    level = logging.INFO  # So logger.info(...) is equivalent to print()

    logger.setLevel(level)
    logger_channel = logging.StreamHandler()
    logger_formatter = logging.Formatter(r'%(asctime)s - %(name)s - %(levelname)s - %(module)s:%(lineno)d:%(funcName)s: %(message)s')
    logger_formatter.default_time_format = r'%Y-%m-%d %H:%M:%S'
    logger_formatter.default_msec_format = r'%s.%03d'
    logger_channel.setFormatter(logger_formatter)
    logger.addHandler(logger_channel)


Context.plugin_name = plugin_name
Context.logger = logger


def plugin_start3(plugin_dir: str) -> str:
    Context.plugin_dir = Path(plugin_dir).resolve()
    version_file = Context.plugin_dir / "version"
    Context.plugin_version = Version(version_file.read_text())
    Context.router = SpanshRouter()
    Context.router.check_for_update()
    return 'SpanshRouterRE'


def plugin_start(plugin_dir: str):
    """EDMC calls this function when running in Python 2 mode."""
    raise EnvironmentError("This plugin requires EDMC version 4.0 or later.")


def plugin_stop():
    Context.router.save_route()
    if Context.router.update_available:
        Context.router.install_update()


def journal_entry(cmdr: str, is_beta: bool, system: str, station: str, entry: dict, state: dict):
    if (
        entry['event'] in ['FSDJump', 'Location', 'SupercruiseEntry', 'SupercruiseExit']
        and entry["StarSystem"].lower() == Context.router.next_stop.lower()
    ):
        Context.router.update_route()
        Context.router.set_source_ac(entry["StarSystem"])
    elif entry['event'] == 'FSSDiscoveryScan' and entry['SystemName'] == Context.router.next_stop:
        Context.router.update_route()


def ask_for_update():
    if Context.router.update_available:
        update_txt = "New SpanshRouterRE update available!\n"
        update_txt += "If you choose to install it, you will have to restart EDMC for it to take effect.\n\n"
        update_txt += Context.router.spansh_updater.changelogs
        update_txt += "\n\nInstall?"
        install_update = confirmDialog.askyesno("SpanshRouterRE", update_txt)

        if install_update:
            confirmDialog.showinfo("SpanshRouterRE", "The update will be installed as soon as you quit EDMC.")
        else:
            Context.router.update_available = False


def plugin_app(parent: tk.Widget):
    Context.router.init_gui(parent)
    Context.router.open_last_route()
    parent.master.after_idle(ask_for_update)
