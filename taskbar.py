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

from xctl import Window
from PyQt4 import QtGui, QtCore


class TaskbarWidget(QtGui.QWidget):
    
    def __init__(self, is_vertical=False, desktops=None):
        super(TaskbarWidget, self).__init__()
        self.is_vertical = is_vertical
        self.desktops = desktops if isinstance(desktops, list) and desktops else [desktops]
        self._buttons = []
        
        # This is really ugly TODO Figure out better way to get notifications on structure change
        self._timer = QtCore.QTimer()
        QtCore.QObject.connect(self._timer, QtCore.SIGNAL("timeout()"), self.update)
        self._timer.start(500)
        
    def mousePressEvent(self, e):
        prev = None
        h = e.y() if self.is_vertical else e.x()
        for x in self._buttons:
            if x["h"] > h:
                prev["win"].switch_to()
                return
            prev = x
        prev["win"].switch_to() # We are on the last element
        
    def paintEvent(self, e):
        p = QtGui.QPainter()
        addX = 0 if self.is_vertical else self.height()
        addY = self.width() if self.is_vertical else 0
        ptrX = 0
        ptrY = 0
        self._buttons = []
        
        p.begin(self)
        for w in TaskbarWidget._get_sorted_windows():
            if (self.desktops and not w.get_desktop() in self.desktops) or \
                (w.has_atom("_NET_WM_STATE", "_NET_WM_STATE_SKIP_TASKBAR")): 
                continue
            
            letter = w.get_class()[0]
            if w.is_active():
                letter = letter.upper()
            else:
                letter = letter.lower()
            
            p.drawText(ptrX, ptrY, 
                       max(addX, addY), max(addX, addY),
                       QtCore.Qt.AlignCenter,
                       letter) 

            self._buttons.append({ "h": max(ptrX, ptrY), "win": w})
            ptrX += addX
            ptrY += addY
        p.end()
       
    @staticmethod 
    def _get_sorted_windows():
        return sorted(Window.get_all_windows(), key=lambda w: w.win_id)
