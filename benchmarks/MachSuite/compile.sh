script_dir=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
echo started compiling $script_dir
output_dir=$script_dir/output
source_dir=$script_dir/source
common_dir=$source_dir/common
rm -rf $output_dir
mkdir $output_dir
cd $source_dir
dirs=$(ls -d */**/)
cd $output_dir
for dir in $dirs; do
  if [[ $dir != *"common/test/" ]]; then
    echo $dir
    full_dir=$source_dir/$dir
    output=$output_dir/${dir%/*}
    output=$(echo ${output%/*}_${output##*/})
    mkdir -p $output
    cd $output
    source=$(ls $full_dir*.c $full_dir*.h | grep -v "test.c" | grep -v "generate.c")
    common=$(ls $common_dir/*.c $common_dir/*.h)
    data=$(ls $full_dir*.data)
    clang-17 -S -emit-llvm -O -Xclang -disable-llvm-passes -I$common_dir $source $common
    cp $data $output
  fi
done
echo finished compiling $script_dir