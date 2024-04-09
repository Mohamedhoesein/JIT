source ./common.sh

script_dir=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )

cd "${script_dir}" || exit

dirs=$(ls -d ./*/)
for dir in $dirs; do
  full_dir=$(concat_dirs "${script_dir}" "${dir}")
  cd "${full_dir}" || exit
  compile_file=$(get_compile_script "./")
  if test -f "${compile_file}"; then
    $compile_file
  fi
done