Benchmarks:
- [ ] Shell scripts:
    - [ ] Make shared variables:
        - [ ] Name of compile scripts.
        - [ ] Name of run scripts.
        - [ ] Name of CSV files.
    - [ ] Create a base function for the compiling and running, which takes as an argument the source and jit.
    - [ ] Create a logic to compile and run a binary with some optimisations as a reference.
- [ ] Handle the arguments for the back-end.
- [ ] See if we need to rerun the same application multiple times or just once.

JIT:
- [x] Create an abstract class for the back-end.
  - [x] Adding modules can stay as it is.
  - [x] For arguments add an argument to the `create` function that is a list of strings.
  - [x] For the callback, the front-end receives the name of the function that the back-end want, and gives back a module
    for the specific function. Later we may want to switch to class names if we include languages that have classes.
- [x] Have a compilation flag for each back-end.
- [x] Define the structure to handle arguments for the back-end itself and the application that is run, alongside the  files.
    - [x] `-back-end=\<args> -file=\<file> -application=\<args>`
        - [x] `-back-end` will be the arguments for the backend, split on space unless something is in quotes.
          So `arg1 "arg2 arg3" arg4`, will be split into `arg1`, `arg2 arg3`, and `arg4`.
        - [x] `-file` will be the files of the application.
        - [x] `-application` will be the arguments for the application, split on space unless something is in quotes.
          So `arg1 "arg2 arg3" arg4`, will be split into `arg1`, `arg2 arg3`, and `arg4`.
- [ ] Expand the simple JIT implementation to have multiple optimisations and allow for arguments to select the optimisations.
- [ ] For the arguments store the core combinations for each back-end in a file with a name associated with the back-end,
  you can have multiple for the same back-end. Which is used for the benchmarks.
