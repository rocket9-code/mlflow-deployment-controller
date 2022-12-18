import re


def rclone_source(source, backend):
    if backend == "blob":
        pattern = r"(?<=net/).*"
        rclonesource = re.search(pattern, source).group()
        conatiner_pattern = r"(?<=/)\w+"
        conatiner_name = re.search(conatiner_pattern, source).group()
        return "wasbs://" + conatiner_name + "/" + rclonesource
    else:
        return source
