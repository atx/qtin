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

from subprocess import Popen, PIPE
import xwrapper #@UnresolvedImport

class Window:
    
    def __init__(self, winid):
        self.win_id = winid
        
    def get_title(self):
        return " ".join(self._get_relevant_wmctrl().split()[3:])
    
    def get_desktop(self):
        return int(self._get_relevant_wmctrl().split()[1])
    
    def reserve_space(self, left=0, right=0, top=0, bottom=0):
        self.set_x_property("_NET_WM_STRUT_PARTIAL", 
                            [left, right, top, bottom, 0, 0, 0, 0, 0, 0, 0, 0], 
                            tpe="cardinal")
        
    def switch_to(self):
        Popen(["wmctrl", "-i", "-a", hex(self.win_id)])
    
    def has_atom(self, name, value):
        return xwrapper.has_atom(self.win_id, name, value)
    
    def set_x_property(self, name, values, tpe="atom"): # Supports only atoms and cardinals
        if not isinstance(values, list):
            return self.set_x_property(name, [values])
  
        xwrapper.delete_property(self.win_id, name)
        
        for at in values:
            if tpe == "atom":
                xwrapper.add_atom(self.win_id, name, at)
            elif tpe == "cardinal":
                xwrapper.add_cardinal(self.win_id, name, at)
        
    def does_exist(self):
        return self._get_relevant_wmctrl() != None
        
    def _get_relevant_wmctrl(self):
        for x in Window._get_wmctrl_list():
            if x.startswith("0x%.8x" % self.win_id):
                return x
        return None
    
    @staticmethod
    def get_all_windows():
        res = []
        for l in Window._get_wmctrl_list():
            spl = l.split()
            if(len(spl) < 1):
                continue
            res.append(Window(int(spl[0], 16)))
        return res
    
    @staticmethod
    def _get_wmctrl_list():
        w = Popen(["wmctrl", "-l"], stdout=PIPE)
        out = w.communicate()[0]
        w.wait()
        return str(out, encoding="UTF-8").split("\n")