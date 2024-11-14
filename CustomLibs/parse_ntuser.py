from CustomLibs import list_functions as LF
from CustomLibs import InputValidation as IV
from CustomLibs import NTUSER_functions as NTF
from Registry import Registry
import config
import os

def get_users(drive):
    exclusion_list = ["All Users", "Default", "Default User", "Public"]
    if drive == "C:\\":
        users_path = f"{drive}Users"
    else:
        users_path = f"{drive}[root]\\Users"
    user_list = []
    for user in os.listdir(users_path):
        full_path = os.path.join(users_path, user)
        if os.path.isdir(full_path) and user not in exclusion_list:
            user_list.append(user)

    return user_list

def main(drive, mount=False):
    # get specific NTUSER.DAT file if they're analyzing a drive
    if mount:
        user_list = get_users(drive)  # get user list

        # prompt user selection
        user = IV.int_between_numbers(f"Select a user: {LF.print_list_numbered(user_list)}\n0: Go Back\n",
                                      0, len(user_list))
        if user == 0:
            return
        else:
            user = user_list[user - 1]

        # copy NTUSER.DAT file
        if drive == "C:\\" and not os.path.exists("NTUSER.DAT_copy"):
            config.copy_locked_reg("NTUSER.DAT", user)
        elif drive != "C:\\" and len(drive) < 4:
            config.copy_reg(drive, "NTUSER.DAT", user)

    # initialize registry object
    if len(drive) < 4:
        reg = Registry.Registry("NTUSER.DAT_copy")
    else:
        reg = Registry.Registry(drive)

    # prompt info selection
    info_list = ["RecentDocs", "ComDlg32", "UserAssist", "TypedPaths", "MountPoints2", "Run", "IE Typed URLs", "All"]

    while True:
        # prompt user on info to gather
        selected_info = IV.int_between_numbers(f"Select information to gather:{LF.print_list_numbered(info_list)}"
                                               f"\n0) Go Back\n",
                                               0, len(info_list))
        if selected_info == 0:
            if os.path.exists("NTUSER.DAT_copy"):
                os.remove("NTUSER.DAT_copy")
            break
        selected_info = info_list[selected_info - 1]

        if selected_info == "ComDlg32":
            NTF.parse_comdlg32(reg)
        elif selected_info == "RecentDocs":
            NTF.parse_recent_docs(reg)
        elif selected_info == "UserAssist":
            NTF.parse_user_assist(reg)
        elif selected_info == "TypedPaths":
            NTF.parse_typed_paths(reg)
        elif selected_info == "MountPoints2":
            NTF.parse_mount_points(reg)
        elif selected_info == "Run":
            NTF.parse_run(reg)
        elif selected_info == "IE Typed URLs":
            NTF.parse_IE_urls(reg)
        elif selected_info == "All":
            NTF.parse_all(reg)
