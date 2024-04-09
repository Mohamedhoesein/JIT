add_slash_if_needed() {
  if [[ $1 != *"/" ]]; then
    echo "${1}/"
  else
    echo "${1}"
  fi
}

concat_dirs() {
  left=$(add_slash_if_needed "${1}")
  right="${2}"
  output=$(add_slash_if_needed "${left}${right}")
  echo "${output}"
}

concat_dir_file() {
  left=$(add_slash_if_needed "${1}")
  right="${2}"
  echo "${left}${right}"
}

get_output_dir() {
  output=$(concat_dirs "${1}" "output")
  echo "${output}"
}

get_source_dir() {
  output=$(concat_dirs "${1}" "source")
  echo "${output}"
}

get_error_file() {
  output=$(concat_dir_file "${1}" "error")
  echo "${output}"
}

get_time_data_file() {
  output=$(concat_dir_file "${1}" "time_data.csv")
  echo "${output}"
}

get_compile_script() {
  output=$(concat_dir_file "${1}" "compile.sh")
  echo "${output}"
}

get_run_script() {
  output=$(concat_dir_file "${1}" "run.sh")
  echo "${output}"
}

rename_output_dir() {
  dir=$1
  start_dot=false
  start_slash=false
  end_slash=false
  if [[ ${dir} == "./"* ]]; then
    start_dot=true
    start_slash=true
  elif [[ ${dir} == "."* ]]; then
    start_dot=true
  elif [[ ${dir} == "/"* ]]; then
    start_slash=true
  fi
  if [[ ${dir} == *"/" ]]; then
    end_slash=true
  fi
  cleaned_dir=$dir
  if [[ $end_slash == true ]]; then
    cleaned_dir=${cleaned_dir::-1}
  fi
  if [[ $start_dot == true ]] && [[ $start_slash == true ]]; then
    cleaned_dir=${cleaned_dir:2}
  elif [[ $start_dot == true ]]; then
    cleaned_dir=${cleaned_dir:1}
  elif [[ $start_slash == true ]]; then
    cleaned_dir=${cleaned_dir:1}
  fi
  cleaned_dir=${cleaned_dir//\//\_}
  out_dir=$cleaned_dir
  out_dir=$out_dir/
  if [[ $start_slash == true ]]; then
    out_dir=/$out_dir
  fi
  if [[ $start_dot == true ]]; then
    out_dir=.$out_dir
  fi
  echo "${out_dir}"
}

compile() {
  echo "started compiling ${script_dir}"

  # Setup variables.
  script_dir=$1
  ls_dir=$2
  dir_filter=$3
  source_filter=$4
  additional_step=$5
  has_include=$6
  output_dir=$(get_output_dir "${script_dir}")
  source_dir=$(get_source_dir "${script_dir}")

  # Setup output directory.
  rm -rf "${output_dir}"
  mkdir "${output_dir}"

  # Retrieve source directories.
  cd "${source_dir}" || exit
  dirs=""
  if [ -z "${dir_filter}" ]; then
    dirs=$(ls -d $ls_dir)
  else
    dirs=$(ls -d $ls_dir | grep -v "${dir_filter}")
  fi
  # Go over the source directories
  cd "${output_dir}" || exit
  for dir in $dirs; do
    echo "${dir}"
    # Remove the ./ and / at the start and end of the directory to safely replace all / with an underscore to have
    # everything in the output directory itself.
    out_dir=$(rename_output_dir "${dir}")
    full_dir=$(concat_dirs "${source_dir}" "${dir}")
    output=$(concat_dirs "${output_dir}" "${out_dir}")
    mkdir "${output}"
    cd "${output}" || exit

    # Get the source files for the current directory.
    source=""
    if [ -z "${source_filter}" ]; then
      source=$(ls "${full_dir}"*.c "${full_dir}"*.h)
    else
      source=$(ls "${full_dir}"*.c "${full_dir}"*.h | grep -v "${source_filter}")
    fi
    source="${source//$'\n'/$' '}"

    # If there is an include also retrieve those.
    if [ $has_include = true  ]; then
      include=""
      common=""
      for ((i=7; i<=$#; i++))
      do
        folder=$(add_slash_if_needed "${source_dir}/${!i}")
        include+=" -I${folder}"
        common+=" "$(ls "${folder}"/*.c "${folder}"/*.h)
      done
      clang-17 -S -emit-llvm -O -Xclang -disable-llvm-passes $include $source $common
    else
      clang-17 -S -emit-llvm -O -Xclang -disable-llvm-passes $source
    fi

    # Do any additional steps.
    $additional_step "${full_dir}" "$output"
  done
  echo "finished compiling ${script_dir}"
}

run() {
  echo "started running ${script_dir}"

  # Setup variables.
  script_dir=$1
  jit=$2
  application_arguments=$3
  output_dir=$(get_output_dir "${script_dir}")
  error_file=$(get_error_file "${script_dir}")
  time_data_file=$(get_time_data_file "${script_dir}")

  # Remove the previous error and time files.
  [ -e "${error_file}" ] && rm "${error_file}"
  [ -e "${time_data_file}" ] && rm "${time_data_file}"
  touch "${time_data_file}"

  # Retrieve output directories.
  cd "$output_dir" || exit
  dirs=$(ls -d ./*/)
  for dir in $dirs; do
    echo "${dir}"
    echo "${dir}" >> "${error_file}"
    full_dir=$(concat_dirs "${output_dir}" "${dir}")

    # Get the source files.
    source=$(ls "${full_dir}"*.ll)
    source="${source//$'\n'/$' '}"

    # Retrieve any additional arguments that are needed for the application.
    application=$($application_arguments "${dir}" "${full_dir}")

    # Execute the application via time. The output format is a comma separated list of the command, real time, and exit code.
    /usr/bin/time -q -a -o "${time_data_file}" -f \"%C\",\"%e\",\"%x\" "${jit}" -f"${source}" -a"${application}" > /dev/null 2>> "${error_file}"
  done

  echo "finished running ${script_dir}"
}