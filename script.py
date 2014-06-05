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

from subprocess import check_output
from PyQt4 import QtGui, QtCore


class ScriptWidget(QtGui.QWidget):
    
    def __init__(self, run, every):
        super(ScriptWidget, self).__init__()
        self.run = run
        self.reload_text()
        # every <= 0 executes the script only once
        if(every > 0): 
            self._timer = QtCore.QTimer()
            QtCore.QObject.connect(self._timer, QtCore.SIGNAL("timeout()"), self.reload_text)
            self._timer.start(every * 1000)

    def paintEvent(self, e):
        p = QtGui.QPainter()
        p.begin(self)
        p.drawText(self.rect(), QtCore.Qt.AlignCenter, self._text)
        p.end()
        
    def reload_text(self):
        self._text = check_output(self.run, shell=True).decode("UTF-8")
        if self._text[-1] == "\n":
            self._text = self._text[:-1]
        self.update()
