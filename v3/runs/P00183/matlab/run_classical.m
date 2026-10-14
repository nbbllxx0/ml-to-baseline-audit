function run_classical(threads, tag)
% P00183 classical runs (v3/plan/CENSUS_PREREG.md §9, P00183 row). The repository's augmented-Lagrangian TO through
% infill_logged.m (logging only) on angles 16, 62, 75 of linspace(0, pi, 100): one warm-up and 3 timed repeats per
% angle, or one run when the first exceeds 1 h. threads: 1 (L1) or 0 (MATLAB default threading, L2).
% Quality: compliance_eval.m (the repository evaluator calculate_compliance.m, repaired; REPAIRS.md) on every stage-end design and on the generator designs
% in ../timing/phi_gen_100.mat. Writes ../timing/classical_<tag>.mat.
here = fileparts(mfilename('fullpath'));
repo = 'E:/AI/ml-to-baseline-audit/v3/third_party/Theory_Driven_TO/CAD code';
addpath(here); addpath(repo);
if threads > 0
    maxNumCompThreads(threads);
end
theta = linspace(0, pi, 100);
idx = [16 62 75];
g = load(fullfile(here, '..', 'timing', 'phi_gen_100.mat'));
runs = struct('angle_index', {}, 'repeat', {}, 'seconds', {}, 'stage_t', {}, 'stage_beta', {}, 'stage_budget', {}, ...
              'stage_c', {}, 'c_final_eval', {}, 'budget', {});
for k = 1:numel(idx)
    i = idx(k);
    nrep = 4;
    r = 0;
    while r < nrep
        r = r + 1;
        t0 = tic;
        [c, y, budget, LOG] = infill_logged(theta(i));
        s = toc(t0);
        if r == 1 && s > 3600
            nrep = 1;                                % §6.4: one run, no warm-up
        end
        sc = zeros(1, numel(LOG));
        for j = 1:numel(LOG)
            sc(j) = compliance_eval(theta(i), LOG(j).phi);
        end
        runs(end+1) = struct('angle_index', i, 'repeat', r - (nrep > 1), 'seconds', s, 'stage_t', [LOG.t], ...
                             'stage_beta', [LOG.beta], 'stage_budget', [LOG.budget], 'stage_c', sc, ...
                             'c_final_eval', compliance_eval(theta(i), y), 'budget', budget); %#ok<AGROW>
        fprintf('angle %d repeat %d: %.1f s, %d FE analyses, c_eval %.4f\n', i, r, s, budget, runs(end).c_final_eval);
        save(fullfile(here, '..', 'timing', ['classical_' tag '.mat']), 'runs', 'threads');
    end
end
gen_c = zeros(1, 100);
for i = 1:100
    gen_c(i) = compliance_eval(theta(i), double(g.phi_gen(i, :))');
end
save(fullfile(here, '..', 'timing', ['classical_' tag '.mat']), 'runs', 'threads', 'gen_c', 'idx');
fprintf('generator compliance on angles %s: %s\n', mat2str(idx), mat2str(gen_c(idx), 6));
end
