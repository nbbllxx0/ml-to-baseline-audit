"""Fig. 7: primary workload-mean repayment upper bounds and unchanged board energy.

Recomputes N501-N503 from saved paired times without modifying evidence or
registries. Secondary median-input scenarios remain in Appendix B.8.
"""
import csv
import json
import pathlib
import statistics
import sys

sys.dont_write_bytecode = True
HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT / 'v4' / 'manuscript' / 'figures'))
import make_figures as mf
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import numpy as np

OUTS = [HERE / 'figures' / 'fig7_breakeven_energy.pdf', HERE.parent / 'arxiv' / 'figures' / 'fig7_breakeven_energy.pdf']
C = mf.C

def main():
    tt = mf.load('ttq_summary.json')
    oat = mf.load('oat_retest_summary.json')['stages']
    energy = mf.load('energy.json')
    reg = json.loads((HERE / 'numbers_review.json').read_text('utf-8'))
    offline_s = (168 + 16) * 86400.0  # H100-days of data generation and training, OAT Appendix G
    specifications = [(256, 'primary_ce_and_volume', 'N501', '256², volume condition', True),
                      (256, 'preregistered_ce_only', 'N502', '256², pre-registered rule', False),
                      (64, 'primary_ce_and_volume', 'N503', '64², both quality rules', True)]
    bounds, paired = [], []
    for size, rule, nid, label, filled in specifications:
        inf = {int(k): v['time_s'] for k, v in oat[f'OAT inference {size}']['per_problem'].items()}
        savings = []
        for p in tt[f'{size}_gpu']['per_problem']:
            m = p[rule]
            t = m['matched_wall_incl_setup_s'] if m['matched'] else p['wall_150_incl_setup_s']
            saving = t - inf[p['problem_id']]
            savings.append(saving)
            paired.append({'id': nid, 'problem': p['problem_id'], 'classical_s': t,
                           'inference_s': inf[p['problem_id']], 'saving_s': saving,
                           'censored': not m['matched']})
        mean = statistics.mean(savings)
        assert mean > 0
        tau = offline_s / mean
        assert abs(tau - reg[nid]['value']) < 1e-7, (nid, tau, reg[nid]['value'])
        assert reg[nid]['text'] == f'{tau/1e6:.1f} million'
        bounds.append({'id': nid, 'upper_bound_uses': tau, 'mean_saving_lower_bound_s': mean,
                       'label': label, 'filled': filled, 'size': size, 'rule': rule})
    for p in tt['64_gpu']['per_problem']:
        a, b = p['primary_ce_and_volume'], p['preregistered_ce_only']
        ta = a['matched_wall_incl_setup_s'] if a['matched'] else p['wall_150_incl_setup_s']
        tb = b['matched_wall_incl_setup_s'] if b['matched'] else p['wall_150_incl_setup_s']
        assert ta == tb

    fig = plt.figure(figsize=(mf.W2, 72 * mf.MM))
    gs = fig.add_gridspec(1, 2, left=0.26, right=0.98, bottom=0.25, top=0.81,
                         wspace=0.85, width_ratios=[1.3, 1])
    ax = fig.add_subplot(gs[0, 0])
    rows = []
    for i, item in enumerate(bounds):
        y, tau = 2-i, item['upper_bound_uses']
        ax.annotate('', xy=(1.06e6, y), xytext=(tau, y),
                    arrowprops={'arrowstyle': '->', 'lw': 0.9, 'color': C['gpu']})
        ax.plot(tau, y, marker='o', ms=4.8, mfc=C['gpu'] if item['filled'] else 'white',
                mec=C['gpu'], mew=0.9)
        ax.text(tau*1.18, y, '≤' + reg[item['id']]['text'], va='center', fontsize=8)
        rows.append(['a', item['label'], f'{tau:.9f}'])
    ax.set_xscale('log')
    ax.set_xlim(1e6, 1e8)
    ax.set_ylim(-0.65, 2.65)
    ax.set_yticks([2,1,0])
    ax.set_yticklabels([v['label'] for v in bounds], fontsize=8)
    ax.set_xticks([1e6, 1e7, 1e8], labels=['1', '10', '100'])
    ax.set_xlabel('Repayment uses (millions)', fontsize=8)
    fig.text(0.025, 0.94, 'a', fontsize=9, fontweight='bold')
    fig.text(0.065, 0.94, 'Workload-mean upper bounds', fontsize=9)
    ax = fig.add_subplot(gs[0,1])
    groups = [('energy OAT inference 64', 'OAT, 64²', C['oat'], 'o'),
              ('energy ours GPU 64', 'Classical, 64²', C['gpu'], 'o'),
              ('energy OAT inference 256', 'OAT, 256²', C['oat'], 's'),
              ('energy ours GPU 256', 'Classical, 256²', C['gpu'], 's')]
    energy_rows = []
    for i, (stage, label, color, marker) in enumerate(groups):
        values = np.array([r['board_j_per_design'] for r in energy['rows'] if r['stage'] == stage])
        assert len(values) == 5
        y = 3-i
        ax.plot(values, y+np.linspace(-0.15,0.15,len(values)), ls='none', marker=marker, ms=3.6, color=color)
        ax.plot([np.median(values)]*2, [y-0.3,y+0.3], color='black', lw=1.1)
        energy_rows += [['b', label.replace('Classical', 'Ours'), f'{v:.2f}'] for v in values]
        rows += [['b', label, f'{v:.2f}'] for v in values]
    with (mf.DATA / 'fig6_breakeven_energy.csv').open(newline='', encoding='utf-8') as f:
        legacy = [r for r in list(csv.reader(f))[1:] if r[0] == 'b']
    assert energy_rows == legacy, 'Board-energy marks changed'
    ax.set_xscale('log')
    ax.set_ylim(-0.65,3.65)
    ax.set_yticks([3,2,1,0])
    ax.set_yticklabels([g[1] for g in groups], fontsize=8)
    ax.set_xlabel('GPU board energy\nper design (J)', fontsize=8)
    ax.xaxis.set_major_formatter(mticker.LogFormatterSciNotation())
    fig.text(0.69, 0.94, 'b', fontsize=9, fontweight='bold')
    fig.text(0.73, 0.94, 'Board energy', fontsize=9)
    for out in OUTS:
        fig.savefig(out, metadata={'CreationDate': None})
        print('wrote', out)
    plt.close(fig)
    data = HERE / 'figures' / 'data'
    data.mkdir(exist_ok=True)
    with (data / 'fig7_breakeven_energy.csv').open('w', newline='', encoding='utf-8') as f:
        w = csv.writer(f)
        w.writerow(['panel','item','value'])
        w.writerows(rows)
    (HERE.parent / 'reports' / 'figure7_recalculation.json').write_text(
        json.dumps({'offline_gpu_seconds': offline_s, 'bounds': bounds, 'paired_inputs': paired,
                    'energy_matches_legacy': True}, indent=2), encoding='utf-8')

if __name__ == '__main__':
    main()
