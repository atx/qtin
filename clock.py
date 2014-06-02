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

import time
from PyQt4 import QtGui, QtCore


class ClockWidget(QtGui.QWidget):
    
    def __init__(self, fmt="%H:%M"):
        super(ClockWidget, self).__init__()
        self.format = fmt
        
        self._timer = QtCore.QTimer()
        QtCore.QObject.connect(self._timer, QtCore.SIGNAL("timeout()"), self.update)
        self._timer.start(1000 if "%S" in self.format else 60 * 1000)

    def paintEvent(self, e):
        p = QtGui.QPainter()
        p.begin(self)
        p.drawText(self.rect(), QtCore.Qt.AlignCenter, time.strftime(self.format))
        p.end()
