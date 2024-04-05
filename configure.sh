script_dir=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
compile=Debug
jobs=1
do
    case "${flag}" in
        c) compile=${OPTARG};;
        j) jobs=${OPTARG};;
        *)
    esac
done

./$script_dir/lib/install.sh $compile $jobs