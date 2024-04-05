script_dir=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
cd $script_dir
dirs=$(ls -d */)
for dir in $dirs; do
  full_dir=$script_dir/$dir
  compile_file=$full_dir"compile.sh"
  if test -f $compile_file; then
    $compile_file
  fi
done