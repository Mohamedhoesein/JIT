source ../common.sh

script_dir=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )

additional_steps() {
  :
}

compile "${script_dir}" "./*/" "" "" additional_steps false