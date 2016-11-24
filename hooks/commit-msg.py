#!/usr/bin/env python3

########################################################################################################################
# Git Hook: commit-msg                                                                                                 #
#                                                                                                                      #
# This script will verify the format of the git commit message and abort the commit if it is incorrect.                #
# Example of an acceptable commit message format:                                                                      #
#                                                                                                                      #
# """#5 :: Informative title relating to issue 5                                                                       #
#                                                                                                                      #
# A more detailed description."""                                                                                      #
#                                                                                                                      #
#                                                                                                                      #
########################################################################################################################

import sys
import re

print("Running commit-msg hook...")

commit_msg_path = sys.argv[1]

title_line_pattern = r'^#\d+ :: .*'

with open(commit_msg_path) as msg_file:
    commit_message = msg_file.read().splitlines()
    assert len(commit_message) > 0, "Cannot commit with an empty commit message!"
    assert re.match(title_line_pattern, commit_message[0]), "Title line does not match format"
    if len(commit_message) >= 2:
        assert commit_message[1] == '', "Title line must be followed by an empty line"
