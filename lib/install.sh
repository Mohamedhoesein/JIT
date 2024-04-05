# install llvm 18.1.3
script_dir=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
cd $script_dir
git clone https://github.com/llvm/llvm-project.git
cd $script_dir/llvm-project
git checkout llvmorg-18.1.3
mkdir ../llvm
cd ../llvm
cmake -DCMAKE_BUILD_TYPE=$1 ../llvm-project/llvm
make -j $2
cd ../