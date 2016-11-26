#!/usr/bin/env bash

set -e

ab_path=`pwd`
cmd_path=`dirname $0`

if [ ${cmd_path:0:1} = "/" ]; then
    src_dir=$cmd_path
else
    if [ ${cmd_path:0:1} = "." ]; then
        src_dir=$ab_path${cmd_path:1}
    else
        src_dir=$ab_path/$cmd_path
    fi
fi

cache=$src_dir/.install-cache

PREFIX=""
MODE=""

# For convenient, run-user will be set as current user.
# For safety, project owner should not be set as root automoticly. If current
# user is root, run-user will be set as nobody.
OPERATOR=`whoami`
if [ $OPERATOR = 'root' ]; then
	USER="nobody"
else
    USER=$OPERATOR
fi
GROUP=`id -gn $USER`

# exclude file
EXCLUDE="exclude.txt"
EXCLUDE_FROM="$src_dir/$EXCLUDE"


# util functions
usage() {
cat << _EOF

Usage: ./install.sh [OPTION]... [VAR=VALUE]...

Installation directories:
  --prefix=[dir]         project installation directory, required.

Installation mode:
  --mode=[adlog,admin]
                         install mode, required.

For better control, use the options below.
  --user=[user]          the system user who run this program, default is
                         [$USER]

  --group=[group]        the system group who run this program, default is
                         [$GROUP]

  --help                 print this help messages.

_EOF
}

for arg do
	case "$arg" in
	--prefix=*) PREFIX=`echo "$arg" | sed -e "s;--prefix=;;"` ;;
	--mode=*) MODE=`echo "$arg" | sed -e "s;--mode=;;"` ;;
	--user=*) USER=`echo "$arg" | sed -e "s;--user=;;"` ;;
	--group=*) GROUP=`echo "$arg" | sed -e "s;--group=;;"` ;;
	*)
		usage 
		exit 1
		;;
	esac
done

# check prefix 
if test -z $PREFIX; then
    echo "install path must be set, use --prefix to spefity."
    exit 1
fi

# check mode
if test -z $MODE; then
    echo "install mode must be set, use --mode to spefity."
    exit 1
fi

if [ "$MODE" != "adlog" -a "$MODE" != "admin" ]; then
    echo "invalid mode, use [adlog,admin]"
    exit 1
fi

###################################################

echo
echo "#######################################################"
echo
echo "             Build project dirs and files"
echo
echo "#######################################################"
echo

exclude_str=$(
cat $EXCLUDE_FROM | while read line;
do
    if test -z "$line"; then
        continue
    fi
    leading_char=`echo "$line" | cut -c1`
    if test "$leading_char" = "#"; then
        continue
    fi

    echo -n " -name \"$line\" -prune -o"
done)

# make cache dir
if [ -d "$cache" ]; then
    rm -Rf $cache    
fi

mkdir -p $cache

# for root path
cd $src_dir
prune_str="-name \"adlog\" -prune -o -name \"admin\" -prune -o"

find_cmd="find . $prune_str $exclude_str -print0 | cpio -pamdvu0 --quiet $cache"
eval $find_cmd
echo

# for mode path
cd $src_dir/$MODE
find_cmd="find . $exclude_str -print0 | cpio -pamdvu0 --quiet $cache"
eval $find_cmd
echo

running_dir="logs locks"

if [ "$MODE" != "user" ]; then
    running_dir="$running_dir htdocs/sys_js htdocs/xselect"
fi

for d in $running_dir; do
    if [ ! -d "$cache/$d" ]; then
        mkdir -p $cache/$d
    fi
done

# add etc profile
if [ $OPERATOR = 'root' ]; then
    ETC=/etc//mgame-assisant-server
    if [ ! -d "$ETC" ]; then
        mkdir "$ETC"
    fi

    echo "$PREFIX" > $ETC/$MODE
fi

echo
echo "#######################################################"
echo
echo "                Do sync to project dir"
echo
echo "#######################################################"
echo

filter=rsync-filter.txt

# make rsync filter
echo "- /$filter" > $cache/$filter
echo "- keepme" >> $cache/$filter
echo "- data" >> $cache/$filter

echo "+ *.sample" >> $cache/$filter
echo "+ __init__.py" >> $cache/$filter
echo "- /etc/*" >> $cache/$filter

echo "- *.pyc" >> $cache/$filter
echo "- *.pyo" >> $cache/$filter

for d in $running_dir; do
    echo "- /$d/*" >> $cache/$filter
done

# do rsync
cd $cache
echo
echo "rsync dist: $PREFIX"
echo

cmd="rsync -rLptgov --delete-after --filter=\"merge $filter\" ./ $PREFIX"
eval $cmd

# clean
rm -Rf $cache

##################################################

echo
echo "#######################################################"
echo
echo "                     Finish work"
echo
echo "#######################################################"
echo

echo
echo "Change owner (-R $USER:$GROUP)..."
set +e
chown -R $USER:$GROUP $PREFIX
set -e
echo

echo "Set \`etc' directory 700 permission..."
chmod 700 $PREFIX/etc
echo

# file need touch
exec_files="$PREFIX/app.py"

echo "Set $exec_files executable..."
chmod +x $exec_files
echo

echo "Update file timestamp..."
touch $exec_files
echo

echo "Done (maybe you should edit config files manually!)"
