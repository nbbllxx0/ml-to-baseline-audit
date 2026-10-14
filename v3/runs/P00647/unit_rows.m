function unit_rows(threads, tag)
% P00647 unit cost (CENSUS_PREREG §9, dev17): Top3D_maxbulk_unit.m (10 iterations, per-iteration timer) on row 438
% of vfrmin.mat, penal 5, ft 2. threads: 1 (as L1) or 0 (MATLAB default threading, L2). The iteration log with
% per-iteration seconds goes to stdout (-logfile).
repo = 'E:/AI/ml-to-baseline-audit/v3/third_party/DL3DTO-Deep-Learning-for-3D-Topology-Optimization';
here = fileparts(mfilename('fullpath'));
addpath(here); addpath(repo);
if threads > 0
    maxNumCompThreads(threads);
end
fprintf('tag %s threads=%d maxNumCompThreads=%d %s\n', tag, threads, maxNumCompThreads, version);
p = load(fullfile(repo, 'vfrmin.mat')); d = load(fullfile(repo, 'initialDes.mat'));
t0 = tic;
[~, ~, it] = Top3D_maxbulk_unit([0.01 0.01 0.01 32 32 32], d.voxel, p.var(438, 1), 5, p.var(438, 2), 2);
fprintf('total %.1f s for %d iterations including setup\n', toc(t0), it);
end
