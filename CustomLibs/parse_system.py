from Registry import Registry
from CustomLibs import InputValidation as IV
from CustomLibs import list_functions as LF
from CustomLibs import time_conversion as TC
from CustomLibs import display_functions
import datetime
import config
import os
import struct
import io
import contextlib

def filetime_to_datetime(filetime_bytes):
    # Unpack the bytes as a little-endian 64-bit integer
    filetime_int = int.from_bytes(filetime_bytes, byteorder='little')

    # Convert FILETIME to a datetime object
    # FILETIME epoch is January 1, 1601, so we calculate from that date
    windows_epoch = datetime.datetime(1601, 1, 1)
    timestamp = windows_epoch + datetime.timedelta(microseconds=filetime_int // 10)

    return timestamp.replace(microsecond=0)

# parse timezone
def parse_timezone(reg, all=False):
    key = reg.open(r"ControlSet001\Control\TimeZoneInformation")
    timezone_list = []
    timezone_list.append(key.value("TimeZoneKeyName").value())
    output = display_functions.one_value("Time Zone Information", timezone_list)

    for line in output:
        print(line)

    if not all:
        config.file_ask(output, "SYSTEM - Time Zone Information.txt")
    return output

# parse computer name
def parse_computer_name(reg, all=False):
    key = reg.open("ControlSet001\\Control\\ComputerName\\ComputerName")
    computer_name_list = []
    computer_name_list.append(key.value("ComputerName").value())
    output = display_functions.one_value("Computer Name", computer_name_list)
    for line in output:
        print(line)

    if not all:
        config.file_ask(output, "SYSTEM - Computer Name.txt")
    return output

# get USB information
def parse_USB_devices(reg, all=False):
    key = reg.open("ControlSet001\\Enum\\USB")
    USB_list = []

    for vid_key in key.subkeys():
        for device_key in vid_key.subkeys():
            try:
                timestamp_collection = ""
                try:
                    friendly_name = device_key.value("FriendlyName").value()
                except Exception:
                    friendly_name = ""
                device_name = device_key.value("DeviceDesc").value()
                for properties in device_key.subkeys():
                    for guid in properties.subkeys():
                        for folder in guid.subkeys():
                            for value in folder.values():
                                try:
                                    timestamp = str(filetime_to_datetime(value.raw_data()))
                                    if not timestamp.startswith("1601"):
                                        if len(timestamp_collection) == 0:
                                            timestamp_collection = timestamp
                                        else:
                                            timestamp_collection += f" :: {timestamp}"
                                except Exception:
                                    pass
                    if timestamp_collection != "":
                        USB_list.append([device_name, friendly_name, timestamp_collection])
            except Exception:
                pass

    USB_list.sort(key=lambda x: x[1], reverse=True)
    output = display_functions.three_values("Device Name", "Friendly Name", "Timestamps", USB_list)

    print("USB DEVICES")
    for line in output:
        print(line)

    if not all:
        config.file_ask(output, "SYSTEM - USB Devices.txt")
    return output

# get USB storage
def parse_USB_storage(reg, all=False):
    USB_storage_list = []
    key = reg.open("ControlSet001\\Enum\\USBSTOR")

    for device in key.subkeys():  # search device key
        first_installed, last_connected, last_removed, device_name = "", "", "", ""
        for serial_num in device.subkeys():  # search serial number key
            try:
                device_name = serial_num.value("FriendlyName").value()
            except Exception:
                continue
            for folder in serial_num.subkeys():  # search folders under serial_num key
                if folder.name() == "Properties":  # only search the "Properties" subkey
                    for guid in folder.subkeys():  # look through guid subkeys
                        for data in guid.subkeys():  # look through all the folders in the guid subkey
                            if data.name() == "0064":  # search for "first installed" time
                                try:
                                    first_installed = data.value("(default)").value()
                                    first_installed = str(first_installed)[:19]
                                except Exception:
                                    first_installed = ""
                            elif data.name() == "0066":  # search for "last connected"
                                try:
                                    last_connected = data.value("(default)").value()
                                    last_connected = str(last_connected)[:19]
                                except Exception:
                                    last_connected = ""
                            elif data.name() == "0067":  # search for "last removed"
                                try:
                                    last_removed = data.value("(default)").value()
                                    last_removed = str(last_removed)[:19]
                                except Exception:
                                    last_removed = ""

        USB_storage_list.append([device_name, first_installed, last_connected, last_removed])

    if ['', '', '', ''] in USB_storage_list:
        USB_storage_list.remove(['', '', '', ''])
    output = display_functions.four_values("Device Name", "First Installed", "Last Connected", "Last Removed",
                                           USB_storage_list)

    print("USB STORAGE")
    for line in output:
        print(line)

    if not all:
        config.file_ask(output, "SYSTEM - USB Storage.txt")
    return output

# parse last shutdown time
def parse_last_shutdown(reg, all=False):
    shutdown = []
    key = reg.open("ControlSet001\\Control\\Windows")
    data = key.value("ShutdownTime").value()
    decoded_data = struct.unpack("<Q", data)[0]
    timestamp = str(TC.filetime_convert(decoded_data))
    shutdown.append(timestamp)

    output = display_functions.one_value("Last Shutdown", shutdown)
    for line in output:
        print(line)

    if not all:
        config.file_ask(output, "SYSTEM - Last Shutdown.txt")
    return output

def parse_all(reg):
    output = []
    output.append(parse_computer_name(reg, all=True))
    output.append(parse_timezone(reg, all=True))
    output.append(["\nUSB DEVICES"])
    output.append(parse_USB_devices(reg, all=True))
    output.append(["\nUSB STORAGE"])
    output.append(parse_USB_storage(reg, all=True))
    output.append(parse_last_shutdown(reg, all=True))

    if IV.yes_or_no("Output to file? (y/n)\n"):
        with open("SYSTEM - All.txt", 'w') as file:
            for element in output:
                for line in element:
                    file.write(line + '\n')

def main(drive):
    # copy SYSTEM file
    if drive == "C:\\" and not os.path.exists("SYSTEM_copy"):
        config.copy_locked_reg("SYSTEM")
    elif drive != "C:\\" and len(drive) < 4:
        config.copy_reg(drive, "SYSTEM")

    # initialize registry object
    if len(drive) < 4:
        reg = Registry.Registry("SYSTEM_copy")
    else:
        reg = Registry.Registry(drive)

    info_list = ["Computer Name", "Time Zone Information", "USB Devices", "USB Storage", "Last Shutdown Time", "All"]

    while True:
        # prompt user on info to gather
        selected_info = IV.int_between_numbers(f"Select information to gather:{LF.print_list_numbered(info_list)}"
                                               f"\n0) Go Back\n",
                                               0, len(info_list))
        if selected_info == 0:
            break
        selected_info = info_list[selected_info - 1]

        # gather info
        if selected_info == "Computer Name":
            parse_computer_name(reg)
        elif selected_info == "Time Zone Information":
            parse_timezone(reg)
        elif selected_info == "USB Devices":
            parse_USB_devices(reg)
        elif selected_info == "USB Storage":
            parse_USB_storage(reg)
        elif selected_info == "Last Shutdown Time":
            parse_last_shutdown(reg)
        elif selected_info == "All":
            parse_all(reg)

    if len(drive) < 4:
        os.remove("SYSTEM_copy")
