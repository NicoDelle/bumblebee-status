import core.module
import core.widget

import util.cli

class Module(core.module.Module):
    def __init__(self, config, theme):
        super().__init__(config, theme, core.widget.Widget(self.get_output))
        self.__mountpoint = self.parameter("mountpoint", "/mnt")

    def __get_mounted_USB(self):
        isMounted = util.cli.execute("cat /proc/self/mounts | grep " + self.__mountpoint + " > /dev/null && echo 1 || echo 0" , shell=True)

        return isMounted

    def __unmount_USB(self, mountpoint):
        ris = util.cli.execute("umount " + mountpoint, shell=True)
        return ris
    
    def hidden(self):
        mounted = int(self.__get_mounted_USB())
        if not mounted:
            return True
        return False
    
    def get_output(self, widgets):
        if not self.hidden():
            return "Device mounted at " + self.__mountpoint
        #return self.__mountpoint #placeholder
