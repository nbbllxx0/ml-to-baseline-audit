# P00663 (DeepNNforTopoOptisation) environment. The repository's requirements.txt is a macOS (osx-64) conda export;
# the FEniCS 2019.1 image on quay.io can no longer be pulled (schema-1 manifest). This image installs the same package
# versions from conda-forge Linux builds (user approval, 2026-09-25). Versions from requirements.txt at commit 6c042e5,
# including the native libraries FEniCS links against (a first build without these pins picked a newer superlu_dist
# and dolfin failed to import).
FROM condaforge/miniforge3:latest
RUN mamba create -y -n dnn -c conda-forge \
        python=3.9 fenics=2019.1.0 mshr=2019.1.0 petsc=3.14.5 petsc4py=3.14.1 slepc=3.14.2 slepc4py=3.14.0 \
        suitesparse=5.6.0 superlu=5.2.2 superlu_dist=6.2.0 hypre=2.18.2 mumps-mpi=5.2.1 scotch=6.0.9 ptscotch=6.0.9 \
        parmetis=4.0.3 hdf5=1.10.6 boost-cpp=1.74.0 mpich=3.4.1 eigen=3.3.9 \
        numpy=1.20.2 scipy=1.6.2 matplotlib-base=3.4.1 scikit-learn=0.24.1 sympy=1.8 \
        pytorch=1.8.0 "pytorch=*=cpu*" \
    && mamba clean -afy
ENV PATH=/opt/conda/envs/dnn/bin:$PATH
WORKDIR /work
