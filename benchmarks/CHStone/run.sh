source ../common.sh

script_dir=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )

application_arguments() {
  dir=$1
  echo "${dir}"
}

jit=$1

run "${script_dir}" "${jit}" application_arguments