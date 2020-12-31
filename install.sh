#!/usr/bin/env bash

conda create -y -p ./env python=2.7;
conda install -y -p ./env numpy=1.12.1 pandas=0.20.3 matplotlib=2.0.2 scipy=0.19.1 seaborn=0.8;
conda install -y -p ./env tqdm pytest;
conda install -y -p ./env -c bioconda bedtools=2.26.0 pybedtools=0.7.8 samtools=1.3.1 pysam=0.8.4 pybigwig=0.3.5;
conda install -y -p ./env -c bioconda ucsc-bedtobigbed

./env/bin/pip install cwlref-runner --prefix ./env;
./env/bin/pip install . --prefix ./env;

./env/bin/plot_map
