# Official OSS-Fuzz Python builder, pinned by digest. Fuzzing dependencies are CI-only.
FROM gcr.io/oss-fuzz-base/base-builder-python:v1@sha256:21f6fab17ace4dc76e1c56de91ee95d3d03da021df94b41056ba036f6c6f55e9
COPY . $SRC/signalforge/
WORKDIR $SRC/signalforge
COPY .clusterfuzzlite/build.sh $SRC/build.sh
