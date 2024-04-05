script_dir=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
echo started running $script_dir
jit=$1
output_dir=$script_dir/output
rm $script_dir/"time_data.csv"
touch $script_dir/"time_data.csv"
cd $output_dir
dirs=$(ls -d */)
for dir in $dirs; do
  echo $dir
  full_dir=$output_dir/$dir
  source=$(ls $full_dir*.ll)
  /usr/bin/time -q -a -o $script_dir/"time_data.csv" -f \"%C\",\"%e\",\"%x\" $jit $source
done
echo finished running $script_dir