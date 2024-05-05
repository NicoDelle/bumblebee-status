import core.module
import core.widget
import core.input

import util.cli
import dbus

class Module(core.module.Module):
    def __init__(self, config, theme):
        super().__init__(config, theme, core.widget.Widget(self.output))

        self.__mountpoint = self.parameter("mountpoint", "/mnt")
        self.__text = ""
        # = f"device mounted at {self.__mountpoint}"
        self.__bus = dbus.SystemBus()
        #self.__bus = dbus.SystemBus()
        self.clicked = False
        self.err = "not touched"

        event = {
            "type": "unmount",
            "action": self.unmount_USB,
            "button": core.input.RIGHT_MOUSE
        }

        core.input.register(self, button=event["button"], cmd=event["action"])
        

    def get_mounted_USB(self):
        isMounted = util.cli.execute("cat /proc/self/mounts | grep " + self.__mountpoint + " > /dev/null && echo 1 || echo 0" , shell=True)

        return isMounted

    def mount_USB(self, widget):
        """
        DEBUG: viene montato a /run/media/nico/*cose*, non si vede che è montato e non si riesce a fare l'unmount. Però viene montato :)
        """
        ud_manager_obj = self.__bus.get_object('org.freedesktop.UDisks2', '/org/freedesktop/UDisks2')
        ud_manager = dbus.Interface(ud_manager_obj, 'org.freedesktop.DBus.ObjectManager')

        for objPath, interfaces in ud_manager.GetManagedObjects().items():
            if \
                'org.freedesktop.UDisks2.Filesystem' in interfaces and \
                'sda1' in objPath:

                block_obj = self.__bus.get_object('org.freedesktop.UDisks2', objPath)
                block = dbus.Interface(block_obj, 'org.freedesktop.UDisks2.Filesystem')

                try:
                    options = dbus.Dictionary(signature='sv')
                    self.err = block.Mount(options, )
                except Exception as e:
                    self.err = str(e)
        return

    def unmount_USB(self, widget):
        self.clicked = True
        
        ud_manager_obj = self.__bus.get_object('org.freedesktop.UDisks2', '/org/freedesktop/UDisks2')
        ud_manager = dbus.Interface(ud_manager_obj, 'org.freedesktop.DBus.ObjectManager')

        for objPath, interfaces in ud_manager.GetManagedObjects().items():
            if \
                'org.freedesktop.UDisks2.Filesystem' in interfaces and \
                interfaces['org.freedesktop.UDisks2.Filesystem']['MountPoints']:

                mountpoint = interfaces['org.freedesktop.UDisks2.Filesystem']['MountPoints'][0]
                if bytes(mountpoint).decode('utf-8').rstrip('\x00') == self.__mountpoint:
                    filesystem_obj = self.__bus.get_object('org.freedesktop.UDisks2', objPath)
                    filesystem = dbus.Interface(filesystem_obj, 'org.freedesktop.UDisks2.Filesystem')

                    try:
                        options = dbus.Dictionary(signature='sv')
                        filesystem.Unmount(options)
                        # DEBUG --> self.err = "done?"
                    except Exception as e:
                        # DEBUG --> self.err = str(e)
                        # TODO: handle error printing some red text
                        return

                    return

            
    def update(self):
        if self.clicked:
            self.__text = self.err
        else:
            mounted = int(self.get_mounted_USB())
            if mounted:
                self.__text = f"device mounted at {self.__mountpoint}"
            else:
                return
                #self.mount_USB(self)

    def hidden(self):
        mounted = int(self.get_mounted_USB())
        if not mounted:
            return False
        return False
    
    def output(self, widget):
        return self.__text
