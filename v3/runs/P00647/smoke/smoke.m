addpath('E:/AI/ml-to-baseline-audit/v3/third_party/DL3DTO-Deep-Learning-for-3D-Topology-Optimization');
maxNumCompThreads(1);
p = load('vfrmin.mat'); d = load('initialDes.mat');
fprintf('rows %d; row1 vf %.4f rmin %.4f; threads %d\n', size(p.var,1), p.var(1,1), p.var(1,2), maxNumCompThreads);
t0 = tic; [x, DH, it] = Top3D_maxbulk([0.01 0.01 0.01 32 32 32], d.voxel, p.var(1,1), 5, p.var(1,2), 2); toc(t0)
