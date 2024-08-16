#!/bin/bash


if [ "$1" = "-h" ]; then
	stmt1="Start socket wrapper around a REPL/program"
	stmt2="Args: syntax full-command"
	stmt3="\tsyntax: language, such as python or bash, associated with full-command"
	stmt4="\tfull-command: the command to be wrapped by the socket.  EG: sqlite3 my_db.db"
	echo -e "$stmt1\n\n$stmt2\n$stmt3\n$stmt4"

	exit
fi

# Extract the first argument (a single word)
syntax=$1

# Extract the second argument (a full command)
# Using shift to move to the second argument, then capturing the rest as a single command
shift
full_command="$@"

if [ -z "$syntax" ] || [ -z "$full_command" ]; then
	echo "Must provide both syntax and full command arguments: [syntax] [full command]"
	exit
fi

echo -e "\nSyntax: '$syntax'\nCommand: '$full_command'"

socket_name="soc"
fifo_name="repl_fifo"

socket_dir="/tmp/$syntax"
socket_path="$socket_dir/$socket_name"
fifo_path="$socket_dir/$fifo_name"

mkdir -p $socket_dir

if [ -S "$socket_path" ]; then
	rm "$socket_path"
fi

# -p is for a file that's a named pipe
if [ ! -p "$fifo_path" ]; then
	mkfifo "$fifo_path"
fi

echo -e ""
echo "Starting socket at '$socket_path' for syntax '$syntax'"

cat "$fifo_path" | $full_command | nc -klU "$socket_path" > "$fifo_path"
