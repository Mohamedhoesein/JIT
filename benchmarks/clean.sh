source ./common.sh

script_dir=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )

cd "${script_dir}" || exit

dirs=$(ls -d ./*/)
for dir in $dirs; do
  full_dir=$(concat_dirs "${script_dir}" "${dir}")
  output=$(get_output_dir "${full_dir}")
  rm -rf "${output}"

  error=$(get_error_file "${full_dir}")
  rm "${error}"
done

find "${script_dir}" -type f -name *.gch -delete