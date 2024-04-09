source ./common.sh

script_dir=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
jit=""
compile=false
if [[ $1 == "-c" ]]; then
  jit=$2
  compile=true
else
  jit=$1
fi

cd "${script_dir}" || exit

full_time_data_file=$(get_time_data_file "${script_dir}")
[ -e "${full_time_data_file}" ] && rm "${full_time_data_file}"
touch "${full_time_data_file}"

echo "\"Command\",\"Elapsed Time\",\"Exit Code\"" >> "${full_time_data_file}"

dirs=$(ls -d ./*/)
for dir in $dirs; do
  full_dir=$(concat_dirs "${script_dir}" "${dir}")
  cd "${full_dir}" || exit
  compile_file=$(get_compile_script "./")
  run_file=$(get_run_script "./")

  if test -f "${run_file}" && test -f "${compile_file}"; then
    if [[ $compile == true ]]; then
      $compile_file
    fi
    $run_file "${jit}"
    part_time_data_file=$(get_time_data_file "${full_dir}")
    cat "${part_time_data_file}" >> "${full_time_data_file}"
  fi
done