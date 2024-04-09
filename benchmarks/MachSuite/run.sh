source ../common.sh

script_dir=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )

application_arguments() {
  dir=$1
  full_dir=$2
  echo "${dir} ${full_dir}input.data ${full_dir}check.data"
}

jit=$1

run "${script_dir}" "${jit}" application_arguments