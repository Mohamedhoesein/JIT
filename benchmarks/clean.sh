script_dir=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
cd $script_dir
dirs=$(ls -d */)
for dir in $dirs; do
  full_dir=$script_dir/$dir
  rm -rf $full_dir"output"
done
find $script_dir -type f -name *.gch -delete