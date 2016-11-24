#! /usr/bin/env bash

echo "Installing git hooks..."

script_location=$(dirname "$0")
install_location="$script_location"/../.git/hooks

declare -a hooks_to_copy=("commit-msg.py")

for i in "${hooks_to_copy[@]}"
do
   echo "$i"
   cp "$script_location"/"$i" "$install_location"
   mv "$install_location"/"$i" "$install_location"/"${i%%.*}" # Remove the file extension
   chmod +x "$install_location"/"${i%%.*}"
done
