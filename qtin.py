#!/usr/bin/env python3
#
# Copyright (C) 2014 Josef Gajdusek <atx@atx.name>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import argparse
import signal
import json
import sys
import jsonschema
from xctl import Window #@UnresolvedImport
from os import path
from PyQt4 import QtGui, QtCore
from PyQt4.QtCore import Qt

from taskbar import TaskbarWidget
from script import ScriptWidget

CONFIG_SCHEMA = {
    "title": "qtin configuration file schema",
    "type": "object",
    "properties": {
        "orientation": {
            "type": "string",
            "enum": ["vertical", "horizontal"]
        },
        "vpos": {
            "type": "string",
            "enum": ["top", "bottom"]
        },
        "hpos": {
            "type": "string",
            "enum": ["left", "right"]
        },
        "width": {
            "type": "integer",
            "minimum": 1
        },
        "height": {
            "type": "integer",
            "minimum": 1
        },
        "bgcolor": {
            "type": "string"
        },
        "fgcolor": {
            "type": "string"
        },
        "margin": {
            "type": "string",
            "pattern": "^([0-9]+ ){3}([0-9]{1})$"
        },
        "widgets": {
            "type": "array",
            "items": {
                "type": "object",
                "minItems": 1,
                "properties": {
                    "type": {
                        "type": "string",
                        "enum": ["spacer", "script", "taskbar"]
                    },
                    "height": {
                        "type": "integer",
                        "minimum": 1
                    },
                    "run": {
                        "type": "string"
                    },
                    "every": {
                        "type": "number"
                    },
                    "size": {
                        "type": "integer",
                        "minimum": 1
                    },
                    "font": {
                        "type": "string"
                    }
                },
                "required": ["type", "height"]
            }
        }
    },
    "required": ["orientation", "vpos", "hpos", "width", "height", "widgets"]
}

def build_widget_style(w):
    style = ""
    # Font
    if w.get("font"):
        style += "font-family: %s;\n" % w["font"] # Yes, we have CSS style injection here
    if w.get("weight"):
        style += "font-weight: %s;\n" % w["weight"]
    if w.get("size"):
        style += "font-size: %spx;\n" % w["size"]
    
    # Color
    if w.get("fgcolor"):
        style += "color: %s;" % w["fgcolor"]
        
    return style

# Parse command line options
parser = argparse.ArgumentParser(description="Starts qtin.")

parser.add_argument("-c", "--config", dest="config", required=True, 
                    type=lambda x: x if path.isfile(x) else parser.error("Config file does not exists."), 
                    nargs=1, action="store", help="config file to use")

args = parser.parse_args()

f = open(args.config[0], "r")
try:
    cfg = json.load(f)
except ValueError:
    parser.error("Parsing of config file failed.")

try:
    jsonschema.validate(cfg, CONFIG_SCHEMA)
except jsonschema.ValidationError as e:
    parser.error(e.message)

# Init
if __name__ == "__main__":
    signal.signal(signal.SIGINT, signal.SIG_DFL) # Exit on Ctrl+C
    
    app = QtGui.QApplication(sys.argv)
    gui = QtGui.QWidget()
    gui.setWindowFlags(Qt.FramelessWindowHint)
    gui.setFocusPolicy(Qt.NoFocus)
    
    # CSS Style
    style = ""
    if cfg.get("bgcolor"):
        style += "background: %s;\n" % cfg["bgcolor"] 
    
    if cfg.get("fgcolor"):
        style += "color: %s;\n" % cfg["fgcolor"]
    
    gui.setStyleSheet(style)
    
    isvert = cfg["orientation"] == "vertical"
    # Size
    width = cfg["width"] if isvert else cfg["height"]
    height = cfg["height"] if isvert else cfg["width"]
    
    # Margin
    mg = [0, 0, 0, 0]
    if cfg.get("margin"):
        mg = [int(x) for x in cfg["margin"].split()]
    
    # Position
    screen = app.desktop().screenGeometry()
    gui.setGeometry(0 if cfg["hpos"] == "left" else (screen.width() - width - mg[0] - mg[2]),
                    0 if cfg["vpos"] == "top" else (screen.height() - height - mg[1] - mg[3]),
                    width + mg[0] + mg[2], height + mg[1] + mg[3])
    
    # Layout
    lot = QtGui.QVBoxLayout() if isvert else QtGui.QHBoxLayout()
    lot.setAlignment(Qt.AlignTop if isvert else Qt.AlignLeft)
    lot.setContentsMargins(int(mg[0]), int(mg[1]), 
                           int(mg[2]), int(mg[3]))
    gui.setLayout(lot)
    
    for i, w in enumerate(cfg["widgets"]):
        typ = w.get("type")
        style = build_widget_style(w)
        widget = None
        if typ == "spacer":
            widget = QtGui.QWidget()
            
        elif typ == "taskbar":
            widget = TaskbarWidget(is_vertical=isvert, 
                                   desktops=w.get("desktops"))
        elif typ == "script":
            widget = ScriptWidget(w["run"], w["every"] if w.get("every") else -1)
        
        widget.setStyleSheet(style)
        widget.setFixedWidth(width if isvert else w["height"])
        widget.setFixedHeight(w["height"] if isvert else height)
        lot.addWidget(widget)
    
    gui.show()
    
    # Reserve space and set type to dock
    win = Window(gui.winId())
    win.reserve_space(left=gui.width() if cfg["hpos"] == "left" and isvert else 0, 
                      right=gui.width() if cfg["hpos"] == "right" and isvert else 0, 
                      top=gui.height() if cfg["vpos"] == "top" and not isvert else 0, 
                      bottom=gui.height() if cfg["vpos"] == "bottom" and not isvert else 0)
    win.set_x_property("_NET_WM_WINDOW_TYPE", "_NET_WM_WINDOW_TYPE_DOCK")
    
    # Quite hackish way to set the X properties, but it has to be done after entering the Qt loop
    timer = QtCore.QTimer()
    callback = lambda: win.set_x_property("_NET_WM_STATE", ["_NET_WM_STATE_SKIP_TASKBAR", 
                                                            "_NET_WM_STATE_SKIP_PAGER", 
                                                            "_NET_WM_STATE_ABOVE"]) or \
                       win.set_x_property("_NET_WM_ALLOWED_ACTIONS", ["_NET_WM_ACTION_CHANGE_DESKTOP", 
                                                                      "_NET_WM_ACTION_BELOW"])
    QtCore.QObject.connect(timer, QtCore.SIGNAL("timeout()"), callback)
    timer.setSingleShot(True)
    timer.start(500)
    
    sys.exit(app.exec_())
