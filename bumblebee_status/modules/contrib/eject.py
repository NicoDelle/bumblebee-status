import core.module
import core.widget
import core.input

import util.cli
import dbus

class Module(core.module.Module):
    def __init__(self, config, theme):
        super().__init__(config, theme, core.widget.Widget(self.output))

        self.__mountpoint = self.parameter("mountpoint", "/mnt")
        self.__text = f"device mounted at {self.__mountpoint}"
        #self.__bus = dbus.SystemBus()
        self.clicked = False
        self.err = "not touched"

        event = {
            "type": "unmount",
            "action": self.unmount_USB,
            "button": core.input.LEFT_MOUSE
        }

        core.input.register(self, button=event["button"], cmd=event["action"])
        

    def get_mounted_USB(self):
        isMounted = util.cli.execute("cat /proc/self/mounts | grep " + self.__mountpoint + " > /dev/null && echo 1 || echo 0" , shell=True)

        return isMounted

    def unmount_USB(self, widget):
        self.clicked = True
        bus = dbus.SystemBus()
        ud_manager_obj = bus.get_object('org.freedesktop.UDisks2', '/org/freedesktop/UDisks2')
        ud_manager = dbus.Interface(ud_manager_obj, 'org.freedesktop.DBus.ObjectManager')

        for objPath, interfaces in ud_manager.GetManagedObjects().items():
            if \
                'org.freedesktop.UDisks2.Filesystem' in interfaces and \
                interfaces['org.freedesktop.UDisks2.Filesystem']['MountPoints']:

                mountpoint = interfaces['org.freedesktop.UDisks2.Filesystem']['MountPoints'][0]
                if bytes(mountpoint).decode('utf-8').rstrip('\x00') == self.__mountpoint:
                    filesystem_obj = bus.get_object('org.freedesktop.UDisks2', objPath)
                    filesystem = dbus.Interface(filesystem_obj, 'org.freedesktop.UDisks2.Filesystem')

                    try:
                        options = dbus.Dictionary(signature='sv')
                        filesystem.Unmount(options)
                        self.err = "done?"
                    except Exception as e:
                        self.err = str(e)
                        return

                    return

            
    def update(self):
        if self.clicked:
            self.__text = self.err

    def hidden(self):
        mounted = int(self.get_mounted_USB())
        if not mounted:
            return True
        return False
    
    def output(self, widget):
        return self.__text
