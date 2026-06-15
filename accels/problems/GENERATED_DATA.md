# Generated Data Policy

Large correctness data, benchmark inputs, and packaged handout archives are not stored in Git.
Keep the problem statements, source skeletons, PDF/PPT references, and deterministic generators.

Regenerate local data when needed:

```bash
# Minesweeper maps. Default stops at 4096 to avoid generating 500MB+ local files.
cd accels/problems/minesweeper/src
make map_generator
python3 generate_example_maps.py
python3 generate_example_maps.py --max-log-n 16  # full handout range

# Matrix multiplication reference outputs.
cd accels/problems/cmul/src
./generate_reference_outputs.sh 1x1x1 10x10x10

# SIMD convolution sample case.
cd accels/problems/convolution/simd-conv2/convolution_handout/2dconv
./generate_sample_data.sh

# mmap binary input.
cd accels/problems/mmap/src
./generate_sample_data.sh
```
