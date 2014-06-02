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

from PyQt4 import QtGui, QtCore


class BatteryWidget(QtGui.QWidget):
    
    def __init__(self, fmt="%s%%", path="/sys/class/power_supply/BAT0/capacity", pollrate=5000):
        super(BatteryWidget, self).__init__()
        self.format = fmt
        self.path = path

        self._timer = QtCore.QTimer()
        QtCore.QObject.connect(self._timer, QtCore.SIGNAL("timeout()"), self.update)
        self._timer.start(pollrate)
        
    def paintEvent(self, e):
        st = "Error"
        try:
            with open(self.path) as f:
                st = f.read()
        except IOError:
            pass
        
        if st[-1] == "\n":
            st = st[0:-1] # Remove trailing newline
            
        p = QtGui.QPainter()
        p.begin(self)
        p.drawText(self.rect(), QtCore.Qt.AlignCenter, self.format % st)
        p.end()
        
