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

import xwrapper #@UnresolvedImport

class Window:
    
    def __init__(self, winid):
        self.win_id = winid
        
    def get_title(self):
        return xwrapper.get_string(self.win_id, "_NET_WM_VISIBLE_NAME")
    
    def get_class(self):
        return xwrapper.get_string(self.win_id, "WM_CLASS")
    
    def get_desktop(self):
        return xwrapper.get_cardinal(self.win_id, 0, "_NET_WM_DESKTOP")
    
    def reserve_space(self, left=0, right=0, top=0, bottom=0):
        self.set_x_property("_NET_WM_STRUT_PARTIAL", 
                            [left, right, top, bottom, 0, 0, 0, 0, 0, 0, 0, 0], 
                            tpe="cardinal")
        
    def is_active(self):
        return xwrapper.get_cardinal(xwrapper.get_root_window(), 0, 
                                     "_NET_ACTIVE_WINDOW") == self.win_id
        
    def switch_to(self):
        root = xwrapper.get_root_window()
        
        xwrapper.send_event(root, "_NET_CURRENT_DESKTOP", self.get_desktop(), 0, 0, 0, 0)
        xwrapper.send_event(self.win_id, "_NET_ACTIVE_WINDOW", 2, 0, 0, 0, 0)
        
        
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
        
    @staticmethod
    def get_all_windows():
        root = xwrapper.get_root_window()
        ret = []
        i = 0
        while not ret or ret[-1] != None:
            wid = xwrapper.get_cardinal(root, i, "_NET_CLIENT_LIST")
            if not wid:
                break   
            ret.append(wid)
            i += 1
            
        return [Window(x) for x in ret]
