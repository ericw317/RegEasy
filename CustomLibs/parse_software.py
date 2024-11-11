from Registry import Registry
from CustomLibs import InputValidation as IV
from CustomLibs import list_functions as LF
from CustomLibs import time_conversion as TC
from CustomLibs import display_functions
import config
import os
import struct
from datetime import datetime, timezone
import pytz

def format_date(date_str):
    # Ensure the input is a string and exactly 8 characters long
    if len(date_str) != 8 or not date_str.isdigit():
        raise ValueError("Date must be in YYYYMMDD format")

    # Extract the year, month, and day parts
    year = date_str[:4]
    month = date_str[4:6]
    day = date_str[6:]

    # Format the date as YYYY-MM-DD
    formatted_date = f"{year}-{month}-{day}"
    return formatted_date

# decode date
def decode_date(date_bytes):
    # Unpack the data in little-endian format
    year, month, unknown, day, hour, minute, second, _ = struct.unpack('<HHHHHHHH', date_bytes)

    # Construct datetime object
    dt_utc = datetime(year, month, day, hour, minute, second, tzinfo=pytz.UTC)

    # Convert to the target timezone
    dt_converted = dt_utc.astimezone(pytz.timezone("America/New_York"))

    return dt_converted


# parse installed apps
def parse_installed_applications(reg, all=False):
    key = reg.open(r"Microsoft\Windows\CurrentVersion\Uninstall")
    installed_applications_list = []
    for application in key.subkeys():
        try:
            # check values
            display_name = application.value("DisplayName").value()
            publisher = application.value("Publisher").value()
            install_date = format_date(application.value("InstallDate").value())
            install_location = application.value("InstallLocation").value()
            # add to lists
            installed_applications_list.append([display_name, publisher, install_date, install_location])
        except Registry.RegistryValueNotFoundException:
            pass

    # print values and write to file
    output = display_functions.four_values("Display Name", "Publisher", "Install Date",
                                           "Install Location", installed_applications_list)
    print("INSTALLED APPLICATIONS")
    for line in output:
        print(line)

    if not all:
        config.file_ask(output, "SYSTEM - Installed Applications.txt")
    else:
        return output

# parse installed apps
def parse_autostart_programs(reg, all=False):
    key = reg.open(r"Microsoft\Windows\CurrentVersion\Run")
    autostart_programs_list = []

    for program in key.values():
        try:
            # check values
            program_name = program.name()
            install_location = program.value()
            # add to list
            autostart_programs_list.append([program_name, install_location])
        except Registry.RegistryValueNotFoundException:
            pass

    # print values
    output = display_functions.two_values("Program Name", "Install Location", autostart_programs_list)
    print("AUTOSTART PROGRAMS")
    for line in output:
        print(line)

    if not all:
        config.file_ask(output, "SOFTWARE - Autostart Programs.txt")
    else:
        return output

# parse operating system information
def parse_OS_info(reg, all=False):
    key = reg.open(r"Microsoft\Windows NT\CurrentVersion")
    OS_info_list = []

    product_name = key.value("ProductName").value()
    install_date = key.value("InstallDate").value()
    install_date = str(TC.convert_unix_epoch_seconds(install_date))
    registered_owner = key.value("RegisteredOwner").value()

    OS_info_list.append([product_name, install_date, registered_owner])

    # print values
    output = display_functions.three_values("Product Name", "Install Date", "Registered Owner",
                                            OS_info_list)
    print("OPERATING SYSTEM INFORMATION")
    for line in output:
        print(line)

    if not all:
        config.file_ask(output, "SOFTWARE - Operating System Info.txt")
    else:
        return output

# parse last logged on user
def parse_last_logged_on_user(reg, all=False):
    key = reg.open(r"Microsoft\Windows\CurrentVersion\Authentication\LogonUI")
    user = []

    last_user = str(key.value("LastLoggedOnUser").value())
    last_user = last_user.replace(".\\", "")
    user.append(last_user)

    # print values
    output = display_functions.one_value("LAST LOGGED ON USER", user)
    for line in output:
        print(line)

    if not all:
        config.file_ask(output, "SOFTWARE - Last Logged On User.txt")
    else:
        return output

# parse network list
def parse_network_list(reg, all=False):
    key = reg.open(r"Microsoft\Windows NT\CurrentVersion\NetworkList\Profiles")
    network_list = []

    for profile in key.subkeys():
        # get profile name
        network_name = profile.value("ProfileName").value()

        # get profile type
        network_type = profile.value("NameType").value()
        if network_type == 6:
            network_type = "Wired"
        elif network_type == 71:
            network_type = "Wireless"
        elif network_type == 53:
            network_type = "Virtual"
        else:
            network_type = "Unknown"

        # get first and last connected dates
        first_connected = str(decode_date(profile.value("DateCreated").value()))
        last_connected = str(decode_date(profile.value("DateLastConnected").value()))

        network_list.append([network_name, network_type, first_connected, last_connected])

    # display values
    output = display_functions.four_values("Network Name", "Type", "First Connected",
                                           "Last Connected", network_list)

    print("NETWORK LIST")
    for line in output:
        print(line)

    if not all:
        config.file_ask(output, "SOFTWARE - Network List.txt")
    else:
        return output

def parse_svchost(reg, all=False):
    key = reg.open(r"Microsoft\Windows NT\CurrentVersion\Svchost")
    svchost_list = []

    for service in key.values():
        service_name = service.name()
        svchost_list.append(service_name)

    output = display_functions.one_value("SVCHOST SERVICES", svchost_list)
    for line in output:
        print(line)

    if not all:
        config.file_ask(output, "SOFTWARE - Svchost Services.txt")
    else:
        return output


# parse all
def parse_all(reg):
    output = []
    output.append(["OPERATING SYSTEM INFORMATION"])
    output.append(parse_OS_info(reg, all=True))
    output.append(parse_last_logged_on_user(reg, all=True))
    output.append(["INSTALLED APPLICATIONS"])
    output.append(parse_installed_applications(reg, all=True))
    output.append(["AUTOSTART PROGRAMS"])
    output.append(parse_autostart_programs(reg, all=True))
    output.append(["NETWORK LIST"])
    output.append(parse_network_list(reg, all=True))
    output.append(parse_svchost(reg, all=True))

    if IV.yes_or_no("Output to file? (y/n)\n"):
        with open("SOFTWARE - All.txt", 'w') as file:
            for element in output:
                for line in element:
                    file.write(line + '\n')

def main(drive):
    # copy SYSTEM file
    if drive == "C:\\" and not os.path.exists("SOFTWARE_copy"):
        config.copy_locked_reg("SOFTWARE")
    elif drive != "C:\\" and len(drive) < 4:
        config.copy_reg(drive, "SOFTWARE")

    # initialize registry object
    if len(drive) < 4:
        reg = Registry.Registry("SOFTWARE_copy")
    else:
        reg = Registry.Registry(drive)

    info_list = ["Operating System Information", "Last Logged On User", "Installed Applications", "Autostart Programs",
                 "Network List", "Svchost Services", "All"]

    while True:
        # prompt user on info to gather
        selected_info = IV.int_between_numbers(f"Select information to gather:{LF.print_list_numbered(info_list)}"
                                               f"\n0) Go Back\n",
                                               0, len(info_list))
        if selected_info == 0:
            break
        selected_info = info_list[selected_info - 1]

        # gather info
        if selected_info == "Operating System Information":
            parse_OS_info(reg)
        elif selected_info == "Last Logged On User":
            parse_last_logged_on_user(reg)
        elif selected_info == "Installed Applications":
            parse_installed_applications(reg)
        elif selected_info == "Autostart Programs":
            parse_autostart_programs(reg)
        elif selected_info == "Network List":
            parse_network_list(reg)
        elif selected_info == "Svchost Services":
            parse_svchost(reg)
        elif selected_info == "All":
            parse_all(reg)

    if len(drive) < 4:
        os.remove("SOFTWARE_copy")
