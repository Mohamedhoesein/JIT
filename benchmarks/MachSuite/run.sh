script_dir=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
echo "started running ${script_dir}"
jit=$1
output_dir=$script_dir/output
rm "${script_dir}/error"
rm "${script_dir}/time_data.csv"
touch "${script_dir}/time_data.csv"
cd "$output_dir" || exit
dirs=$(ls -d ./*/)
for dir in $dirs; do
  echo "${dir}"
  echo "${dir}" >> "${script_dir}/error"
  full_dir="${output_dir}/${dir}"
  source=$(ls "${full_dir}"*.ll)
  source="${source//$'\n'/$' '}"
  application="${dir} ${full_dir}input.data ${full_dir}check.data"
  /usr/bin/time -q -a -o "${script_dir}/time_data.csv" -f \"%C\",\"%e\",\"%x\" "${jit}" -f"${source}" -a"${application}" > /dev/null 2>> "${script_dir}/error"
done
echo "finished running ${script_dir}"