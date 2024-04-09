source ../common.sh

script_dir=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )

additional_step() {
  full_dir=$1
  output=$2
  data=$(ls "$full_dir"*.data)
  cp $data $output
}

compile "${script_dir}" "./*/**/" "./common/test/" "test.c\|generate.c" additional_step true "common"
