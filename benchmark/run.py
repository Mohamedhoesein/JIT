import os
import subprocess
import typing

from . import common


def main(args: typing.Any):
    base_directory = os.path.dirname(__file__)
    directories = common.get_all_concat_directories(base_directory)
    common.remove_data_files(base_directory)
    component = common.args_to_component(args)
    for directory in directories:
        print("started " + directory)
        run_file = common.add_run_file(directory)
        if not os.path.isfile(run_file):
            print("finished " + directory)
            continue
        os.chdir(os.path.dirname(base_directory))
        run_module = os.path.relpath(run_file).replace("/", ".")[:-3]
        print(args)
        print(run_module)
        print(common.args_to_run_array(args))
        subprocess.run(["python3", "-m", run_module] + common.args_to_run_array(args), check=True)
        common.copy_data_files(directory, base_directory, component, args.f, args.b)
        print("finished " + directory)


if __name__ == '__main__':
    main(common.full_parse_jit_args())
