#!/bin/bash
set -eu
# Build fuzzer in isolated OSS-Fuzz container. Do not install runtime dependencies.
python3 -m pip install --no-deps .
compile_python_fuzzer .clusterfuzzlite/fuzz_inputs.py
