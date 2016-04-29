#!/usr/bin/env bash

mkdir -p wheelhouse
docker run --rm -v `pwd`:/io $DOCKER_IMAGE $PRE_CMD /io/travis/build_manylinux_wheels.sh
ls wheelhouse/