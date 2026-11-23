"""Make a cross-site, source-specific query of organic carbon printed in IR station tables."""
from pathlib import Path
import argparse,csv,re,collections
def make(root,out):
    data=root/'ir/core/tables/carbons.csv'
    rows=list(csv.DictReader(data.open()))
    markers={('848','a'):'noncarbonate_residue_determination',('852','a'):'late_addition_excluded_from_other_tables_figures_statistics',('852','b'):'mean_of_two_measurements',('853','a'):'mean_of_two_measurements'}
    extracted=[];counts=[]
    for site in range(844,855):
        site=str(site);subset=[r for r in rows if r['site']==site];p=Path(subset[0]['source_path'])
        raw=(root/'ir/primary'/p).read_text().splitlines()
        good=[]
        for r in subset:
            val=r['organic_c_pct']
            if not val:continue
            m=re.fullmatch(r'([ab]?)\s*([-+]?(?:\d+(?:\.\d*)?|\.\d+))',val.strip())
            if not m:raise ValueError((site,r['source_line'],val))
            mark,num=m.groups()
            note=markers[(site,mark)] if mark else 'unmarked_published_value'
            fl=next((n for n,v in enumerate(raw,1) if mark and v.strip().startswith(mark) and any(s in v.lower() for s in ('mean','last minute','determined'))),'')
            good.append(dict(site=site,hole=r['reported_hole'],sample=r['sample_label'],depth_mbsf=r['depth_mbsf'],depth_mcd=r['depth_mcd'],published_organic_c=r['organic_c_pct'],organic_c_pct=num,footnote_marker=mark,footnote_role=note,footnote_source_line=fl,source_item=r['item_id'],source_line=r['source_line'],source_url='https://www-odp.tamu.edu/publications/138_IR/'+r['source_path']))
        extracted+=good
        counts.append(dict(site=site,source_rows=len(subset),with_org_c=len(good),blank_or_absent=len(subset)-len(good),footnoted=sum(bool(x['footnote_marker']) for x in good),negative_reported=sum(float(x['organic_c_pct'])<0 for x in good),source_item=subset[0]['item_id']))
    for name,records in [('carbon_reported.csv',extracted),('carbon_coverage.csv',counts)]:
        with (out/name).open('w',newline='') as f:w=csv.DictWriter(f,records[0]);w.writeheader();w.writerows(records)
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    from matplotlib.ticker import MultipleLocator
    plt.rcParams.update({'font.family':'DejaVu Sans','font.size':8,'pdf.fonttype':42,'svg.fonttype':'none','svg.hashsalt':'leg138ir-carbon'})
    fig,ax=plt.subplots(2,6,figsize=(12,5.4),sharex=True,sharey=True)
    fig.subplots_adjust(left=.065,right=.986,top=.88,bottom=.16,wspace=.13,hspace=.26)
    roles={'unmarked_published_value':('#364b56','o','Published value'), 'noncarbonate_residue_determination':('#28817b','s','Noncarbonate residue'), 'late_addition_excluded_from_other_tables_figures_statistics':('#b16831','^','Late addition'), 'mean_of_two_measurements':('#8b5278','D','Mean of two')}
    for i,(s,ca) in enumerate(zip(counts,ax.flat)):
        site=s['site'];vals=[r for r in extracted if r['site']==site]
        ca.set_title(f"Site {site}   ·   {len(vals)}",loc='left',fontsize=9,color='#24464d')
        for name,(color,mrk,title) in roles.items():
            sample=[r for r in vals if r['footnote_role']==name]
            ca.scatter([float(r['organic_c_pct']) for r in sample],[float(r['depth_mcd']) for r in sample],marker=mrk,s=9,color=color,alpha=.85,linewidths=0)
        if not vals:ca.text(.5,.48,'Organic C column\nabsent in this table',ha='center',va='center',transform=ca.transAxes,fontsize=8,color='#53676b')
        ca.set(xlim=(-.12,2.5),ylim=(490,-7))
        ca.xaxis.set_major_locator(MultipleLocator(1));ca.yaxis.set_major_locator(MultipleLocator(100))
        ca.spines['top'].set_visible(False);ca.spines['right'].set_visible(False);ca.grid(axis='y',alpha=.2,lw=.5);ca.tick_params(labelsize=7,length=2)
    legend=ax.flat[-1];legend.axis('off')
    handles=[plt.Line2D([],[],marker=m,color=c,lw=0,label=l,markersize=5) for c,m,l in roles.values()]
    legend.legend(handles=handles,loc='center left',frameon=False,fontsize=7,handletextpad=.15)
    fig.suptitle('Organic carbon in the published Leg 138 site tables',x=.065,ha='left',fontsize=14)
    fig.supxlabel('Organic carbon (wt %)',fontsize=9,y=.055);fig.supylabel('Composite depth (mcd)',fontsize=9,x=.018)
    for extension in ['pdf','svg']:
        opts={'CreationDate':None,'ModDate':None} if extension=='pdf' else {'Date':None}
        fig.savefig(out/('carbon_by_site.'+extension),metadata=opts)
    plt.close(fig)
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('root',type=Path);p.add_argument('out',type=Path);a=p.parse_args();make(a.root,a.out)
