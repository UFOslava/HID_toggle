"""Detects pointing devices, disables Touchpad if any other devices found."""

import subprocess
# import dbus


class HID:
    """xinput entry representation object"""
    name: str = ""
    device_id: int | None = None
    ignored: bool = False  # True if HID should be ignored
    toggled: bool = False  # True if HID should be enabled or disabled

    def __init__(self, name: str, device_id: int | None = None):
        if device_id:
            self.device_id = device_id
        self.name = name

    def __repr__(self):
        return f'HID(name="{self.name}", device_id={self.device_id})'

    def __str__(self):
        return f'HID "{self.name}" (id:{self.device_id})'

    def __bool__(self):
        return bool(self.device_id)

    def ignore(self, state: bool | None = None):
        """Set ignore state bool or set to None to toggle it"""
        if state is None:
            self.ignored = not self.ignored
        else:
            self.ignored = state

        if self.ignored:
            self.toggled = False
        pass

    def toggle(self, state: bool | None = None):
        """Set toggled state bool or set to None to toggle it"""
        if state is None:
            self.toggled = not self.toggled
        else:
            self.toggled = state

        if self.toggled:
            self.ignored = False
        pass


def map_HID() -> list[HID]:
    """scans xinput and populates a list of Pointer objects"""
    try:
        output = subprocess.check_output(['xinput', 'list']).decode('utf-8').split("\n")
        _HID_list: list[HID] = []
        for line in output:
            # if "↳" in line and "pointer" in line:
            if "↳" in line:
                device_name = line.split("\t")[0][5:].strip()
                device_id = int(line.split('id=')[1].split('\t')[0].strip())
                _HID_list.append(HID(device_name, device_id))
        return _HID_list
    except subprocess.CalledProcessError:
        print("Error getting HID list from xinput.")


def get_touchpad_id():
    """Gets the touchpad ID using xinput."""
    try:
        output = subprocess.check_output(['xinput', 'list']).decode('utf-8')
        for line in output.splitlines():
            if 'TouchPad' in line and 'id=' in line:
                print(line)
                return line.split('id=')[1].split('\t')[0]
    except subprocess.CalledProcessError:
        print("Error getting touchpad ID.")
    return None


if __name__ == "__main__":
    HID_list = map_HID()
    print(HID_list)

# TODO Make config file and store HID data in it.
# TODO establish unix socket connection between the both parts.
