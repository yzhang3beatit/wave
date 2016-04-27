# wave
A python tool to calculate UT coverage of new changed C/C++ codes


### 1. How to generate diff file ?

Currently, I just test with output of command line 'diff --git ...' or 'git diff ... '; If you want to use
other diff files, you can modify 'class Diffs' in source codes.

### 2. How to generate gcov files ?
#### Step 1. Adding `-fprofile-arcs -ftest-coverage` in gcc compiling flag
#### Step 2. Run `gcov <source codes filename>.c` in source code folder

### 3. How to use Wave ?

Run `python wave.py <diff filename> <gcov folder>`
