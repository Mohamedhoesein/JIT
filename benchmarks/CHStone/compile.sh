script_dir=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
echo started compiling $script_dir
output_dir=$script_dir/output
source_dir=$script_dir/source
rm -rf $output_dir
mkdir $output_dir
cd $source_dir
dirs=$(ls -d */)
cd $output_dir
for dir in $dirs; do
  echo $dir
  full_dir=$source_dir/$dir
  output=$output_dir/$dir
  mkdir $output
  cd $output
  source=$(ls $full_dir*.c $full_dir*.h)
  clang-17 -S -emit-llvm -O -Xclang -disable-llvm-passes $source
done
echo finished compiling $script_dir