from CustomLibs import InputValidation as IV
from CustomLibs import list_functions
from CustomLibs import parse_system
from CustomLibs import parse_software
from CustomLibs import parse_sam
from CustomLibs import parse_ntuser
from Registry import Registry
import config
import psutil
import os

# list connected devices
def list_drives():
    counter = 1
    partitions = psutil.disk_partitions()
    drives = {}

    # add each drive to a dictionary and enumerate each entry
    for partition in partitions:
        drives[counter] = partition.device
        counter += 1

    return drives


menu = True

# get drive
def get_drive(drives):
    # prompt for drive selection
    print("Enter the number of the device you want to analyze: ")
    for number, drive in drives.items():  # print all connected devices
        print(f"{number}: {drive}")
    print("0: Go Back")
    drive_selected = IV.int_between_numbers("", 0, len(drives))  # get input on which drive to analyze
    if drive_selected == 0:
        return "Go Back"
    return drives[drive_selected]  # map input to drive

# is registry file function
def is_registry_file(filepath):
    try:
        with open(filepath, "rb") as file:
            # Read the first 4 bytes
            magic_number = file.read(4)
            return magic_number == b'regf'
    except IOError:
        return False

# identify hive
def identify_registry_hive(filepath):
    try:
        reg = Registry.Registry(filepath)
        root_keys = [key.name() for key in reg.root().subkeys()]

        if "ControlSet001" in root_keys:
            return "SYSTEM"
        elif "Microsoft" in root_keys:
            return "SOFTWARE"
        elif "Policy" in root_keys and "SAM" in root_keys:
            return "SECURITY"
        elif "SAM" in root_keys:
            return "SAM"
        elif "Software" in root_keys:
            return "NTUSER.DAT"
        else:
            return "Unknown registry hive"
    except Exception as e:
        return "Not a registry file"

# parse registry
def parse_registry(drive=None):
    potential_reg_files = ["SYSTEM", "SOFTWARE", "SAM", "NTUSER.DAT"]
    reg_file = None

    while True:
        if drive is not None:  # execute this block if drive is being analyzed
            # set variables
            registry_path = config.set_path("Windows\\System32\\config", drive)
            reg_list = []

            # add found registry files to reg_list
            for file in os.listdir(registry_path):
                if file in potential_reg_files:
                    reg_list.append(file)
            reg_list.append("NTUSER.DAT")

            # prompt reg file selection
            reg_list_numbered = list_functions.print_list_numbered(reg_list)
            selected_reg = IV.int_between_numbers(f"Select a registry file: {reg_list_numbered}\n0: Go Back\n", 0, len(reg_list))

            if selected_reg == 0:
                break

            try:
                reg_file = reg_list[selected_reg - 1]
            except Exception:
                reg_file = 0

            # parse file
            if reg_file == "SYSTEM":
                parse_system.main(drive)
            elif reg_file == "SOFTWARE":
                parse_software.main(drive)
            elif reg_file == "SAM":
                parse_sam.main(drive)
            elif reg_file == "NTUSER.DAT":
                parse_ntuser.main(drive, mount=True)
            elif reg_file == 0:
                break
        else:  # execute this block if a single file is being analyzed
            reg_path = ""
            while not is_registry_file(reg_path) or reg_file not in potential_reg_files:
                reg_path = IV.file_path("Enter path to registry file (Enter -1 to go back):\n")
                if reg_path == "-1":
                    break
                reg_file = identify_registry_hive(reg_path)
                if not is_registry_file(reg_path) or reg_file not in potential_reg_files:
                    print("Invalid file. Try again.\n")
            if reg_path == "-1":
                break

            # parse file
            if reg_file == "SYSTEM":
                parse_system.main(reg_path)
            elif reg_file == "SOFTWARE":
                parse_software.main(reg_path)
            elif reg_file == "SAM":
                parse_sam.main(reg_path)
            elif reg_file == "NTUSER.DAT":
                parse_ntuser.main(reg_path)

def set_timezone():
    # prompt time zone selection
    timezone_list = ["America/New_York (EST/EDT)", "America/Chicago (CST/CDT)", "America/Denver (MST/MDT)",
                     "America/Los_Angeles (PST/PDT)", "Europe/London (GMT/BST)", "Europe/Paris (CET/CEST)",
                     "Asia/Tokyo (JST)", "Asia/Shanghai (CST)", "Australia/Sydney (AEST/AEDT)",
                     "Pacific/Auckland (NZST/NZDT)", "UTC"]

    timezone_select = IV.int_between_numbers(
        f"Select a timezone to display timestamps in: {list_functions.print_list_numbered(timezone_list)}\n",
        1, len(timezone_list))

    config.timezone = timezone_list[timezone_select - 1].split(" ")[0]


global loop
loop = True

def main():
    drive_list = list_drives()  # load drives
    set_timezone()

    while loop:
        drive_or_file = IV.int_between_numbers("Analyze drive or single registry file?\n"
                                               "1) Drive\n"
                                               "2) Registry File\n"
                                               "3) Set Time Zone\n"
                                               "0) Exit Program\n", 0, 3)
        if drive_or_file == 1:
            drive = get_drive(drive_list)
            if drive != "Go Back":
                parse_registry(drive)
        elif drive_or_file == 2:
            parse_registry()
        elif drive_or_file == 3:
            set_timezone()
        else:
            break


if __name__ == "__main__":
    main()
