function run_rows(threads, tag)
% P00647 L1/L2 runs (v3/plan/CENSUS_PREREG.md §9, P00647 rows): the repository's Top3D_maxbulk.m, unchanged, on
% rows 438, 1696 and 2082 of vfrmin.mat, penal 5, ft 2, as dataGeneration32_bulk.m calls it. Each run is timed once
% (runs exceed 1 h; §6.4). threads: 1 for L1 (one core, as in the article), 0 for MATLAB's default (L2).
% Writes results_<tag>.mat and results_<tag>.txt in this folder; the iteration log goes to stdout.
repo = 'E:/AI/ml-to-baseline-audit/v3/third_party/DL3DTO-Deep-Learning-for-3D-Topology-Optimization';
addpath(repo);
here = fileparts(mfilename('fullpath'));
if threads > 0
    maxNumCompThreads(threads);
end
p = load(fullfile(repo, 'vfrmin.mat')); d = load(fullfile(repo, 'initialDes.mat'));
rows = [438 1696 2082];
res = struct('row', {}, 'vf', {}, 'rmin', {}, 'seconds', {}, 'iterations', {}, 'bulk', {}, 'volume', {}, 'DH', {});
fid = fopen(fullfile(here, ['results_' tag '.txt']), 'w');
fprintf(fid, 'threads=%d maxNumCompThreads=%d %s\n', threads, maxNumCompThreads, version);
for k = 1:numel(rows)
    r = rows(k);
    t0 = tic;
    [x, DH, it] = Top3D_maxbulk([0.01 0.01 0.01 32 32 32], d.voxel, p.var(r, 1), 5, p.var(r, 2), 2);
    s = toc(t0);
    bulk = (DH(1,1)+DH(2,2)+DH(3,3)+DH(1,2)+DH(1,3)+DH(2,1)+DH(3,1)+DH(2,3)+DH(3,2)) / 9;
    res(end+1) = struct('row', r, 'vf', p.var(r, 1), 'rmin', p.var(r, 2), 'seconds', s, 'iterations', it, ...
                        'bulk', bulk, 'volume', mean(x(:)), 'DH', DH); %#ok<AGROW>
    fprintf(fid, 'row %d vf %.4f rmin %.4f seconds %.1f iterations %d bulk %.6f volume %.4f\n', ...
            r, p.var(r, 1), p.var(r, 2), s, it, bulk, mean(x(:)));
    save(fullfile(here, ['results_' tag '.mat']), 'res');
end
fclose(fid);
end
