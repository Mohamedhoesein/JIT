script_dir=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
jit=$1
cd $script_dir
rm $script_dir/"time_data.csv"
touch $script_dir/"time_data.csv"
dirs=$(ls -d */)
echo "\"Command\",\"Elapsed Time\",\"Exit Code\"" >> $script_dir/"time_data.csv"
for dir in $dirs; do
  full_dir=$script_dir/$dir
  run_file=$full_dir"run.sh"
  compile_file=$full_dir"compile.sh"
  if test -f $run_file && test -f $compile_file; then
    $compile_file
    $run_file $jit
    cat $full_dir"time_data.csv" >> $script_dir/"time_data.csv"
  fi
done