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
  - [ ] For arguments add an argument to the `create` function that is a list of strings.
  - [x] For the callback, the front-end receives the name of the function that the back-end want, and gives back a module
    for the specific function. Later we may want to switch to class names if we include languages that have classes.
- [x] Have a compilation flag for each back-end.
- [ ] Define the structure to handle arguments for the back-end itself and the application that is run, alongside the  files.
    - [ ] `-back-end=\<args> -file=\<file> ...`
        - [ ] `-back-end` being split on space and being passed as a list of strings to the back-end.
        - [ ] `-file` will be present for each source file.
        - [ ] everything after that is considered an argument for the application.
- [ ] For the arguments store the core combinations for each back-end in a file with a name associated with the back-end,
  you can have multiple for the same back-end. Which is used for the benchmarks.
