def four_values(name1, name2, name3, name4, list_name):
    # getting spacing sizes
    list1_space = len(name1)
    for value in list_name:
        if len(value[0]) > list1_space:
            list1_space = len(value[0])

    list2_space = len(name2)
    for value in list_name:
        if len(value[1]) > list2_space:
            list2_space = len(value[1])

    list3_space = len(name3)
    for value in list_name:
        if len(value[2]) > list3_space:
            list3_space = len(value[2])

    list4_space = len(name4)
    for value in list_name:
        if len(value[3]) > list4_space:
            list4_space = len(value[3])

    total_space = list1_space + list2_space + list3_space + list4_space

    # display values
    output = []
    output.append(f"{name1:<{list1_space}} | {name2:<{list2_space}} | {name3:<{list3_space}} | {name4}")
    output.append("-" * total_space)
    for value in list_name:
        output.append(f"{value[0]:<{list1_space}} | {value[1]:<{list2_space}} | {value[2]:<{list3_space}} | {value[3]:<{list4_space}}")
        output.append("-" * total_space)
    output.append("")

    return output

def three_values(name1, name2, name3, list_name):
    # getting spacing sizes
    list1_space = len(name1)
    for value in list_name:
        if len(value[0]) > list1_space:
            list1_space = len(value[0])

    list2_space = len(name2)
    for value in list_name:
        if len(value[1]) > list2_space:
            list2_space = len(value[1])

    list3_space = len(name3)
    for value in list_name:
        if len(value[2]) > list3_space:
            list3_space = len(value[2])

    total_space = list1_space + list2_space + list3_space

    # display values
    output = []
    output.append(f"{name1:<{list1_space}} | {name2:<{list2_space}} | {name3}")
    output.append("-" * total_space)
    for value in list_name:
        output.append(
            f"{value[0]:<{list1_space}} | {value[1]:<{list2_space}} | {value[2]}")
        output.append("-" * total_space)
    output.append("")

    return output

def two_values(name1, name2, list_name):
    # get spacing sizes
    list1_space = len(name1)
    for value in list_name:
        if len(value[0]) > list1_space:
            list1_space = len(value[0])

    list2_space = len(name2)
    for value in list_name:
        if len(value[1]) > list2_space:
            list2_space = len(value[1])

    total_space = list1_space + list2_space

    # display values
    output = []
    output.append(f"{name1:<{list1_space}} | {name2}")
    output.append("-" * total_space)
    for value in list_name:
        output.append(f"{value[0]:<{list1_space}} | {value[1]}")
        output.append("-" * total_space)
    output.append("")

    return output

def one_value(name, list_name):
    spacing = len(name)

    output = []
    output.append(name)
    output.append("-" * spacing)

    for value in list_name:
        output.append(value)
    output.append("")

    return output