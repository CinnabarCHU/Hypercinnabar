"""Generate scan-collated editorial links and exceptions for the all-station catalogue."""
from pathlib import Path
import csv, gzip, json, re
ROOT=Path(__file__).resolve().parents[1];D=ROOT/'data'
def read(name):
    with (D/name).open(newline='') as f:return list(csv.DictReader(f))
def save(name,rows):
    with (D/name).open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
SP='https://www-odp.tamu.edu/publications/prosp/digital/138prosp.pdf#page='
PR='https://www-odp.tamu.edu/publications/prelim/138PREL.PDF#page='
def plot_workflows():
    with gzip.open(D / 'pages.jsonl.gz', 'rt') as stream:
        pages = {r['pdf_page']: r['page_text'] for r in map(json.loads, stream) if r['doc_id'] == 'PR'}
    records = []
    for figure in read('pr_site_figures.csv'):
        role = figure['role']
        if role not in ('multi-hole composite compilation', 'calculated chronological series'):
            continue
        number = figure['item_id'].split('F')[1]
        caption = re.search(r'Figure\s+' + number + r'\.(.*?(?:filter|control points)\.)',
                            pages[int(figure['pdf_page'])], re.DOTALL | re.IGNORECASE)
        if caption is None:
            raise ValueError(f"Missing figure caption {number}")
        source = ' '.join(caption.group().split())
        composite = role == 'multi-hole composite compilation'
        evidence = ('spliced', 'mcd', '20-point gaussian filter') if composite else ('discrete sample points', 'mean value between stratigraphic control points')
        if not all(term in source.lower() for term in evidence):
            raise ValueError(f"Unexpected processing description in Figure {number}")
        records.append(dict(
            site=figure['site'], item_id=figure['item_id'], doc_id='PR', role=role,
            pdf_page=figure['pdf_page'], pdf_last=figure['pdf_last'],
            coordinate_axis='meters composite depth (mcd)' if composite else 'age (Ma)',
            splice='sections from multiple holes' if composite else '',
            smoothing='20-point Gaussian filter' if composite else '',
            smoothing_applies_to='GRAPE | magnetic susceptibility | color reflectance' if composite else '',
            mar_discrete_series='' if composite else 'discrete sample points',
            mar_interval_series='' if composite else 'mean value between stratigraphic control points',
            evidence_kind='published figure caption', source_caption_ocr=source,
            source_url=figure['source_url'],
            input_file_status='exact input files and parameterization not identified from caption'))
    save('pr_plot_workflows.csv', records)

def main():
    plot_workflows()
    pairs=read('site_crosswalk.csv')
    f={r['site']:r for r in read('pr_site_figures.csv') if r['role']=='published survey profile'}
    lines={'844':'Line C','845':'Line A','846':'Line G','847':'Line E','848':'Line P','849':'VENTURE 01, 9 Sept 1989, Station 6B survey annotations','851':'Line O','852':'Line N','853':'Line S','854':'Line L in SP only'}
    overlap=[]
    for r in pairs:
        site=r['site']
        if not site:continue
        g=f[site]
        cls='shared_survey_profile_graphic'
        note='Printed time ticks and reflector geometry match across the two versions; station annotation changes.'
        if site=='848':note='The prospectus labels two positions WEQ-5 on Line P; the preliminary report labels WEQ-5 and approximate Site 848. Its caption distinguishes them.'
        if site=='849':note='Matching survey annotations and reflector geometry; the prospectus labels WEQ-6, while the preliminary report draws separate arrows for WEQ-6 and Site 849.'
        if site=='850':cls='no_prospectus_site';note='The new site has a JOIDES Resolution profile. The site survey is recorded in the transit from Site 849.'
        if site=='854':cls='different_survey_product';note='The prospectus shows VENTURE 01 Line L; the preliminary report presents the 3.5 kHz survey made on JOIDES Resolution, with course changes and beacon drop.'
        overlap.append(dict(site=site,proposed_site=r['proposed_site'],profile_relation=cls,visible_line_reference=lines.get(site,''),sp_profile_pdf_page=r['sp_profile_pdf_page'],sp_source_url=(SP+r['sp_profile_pdf_page']) if r['sp_profile_pdf_page'] else '',pr_item=g['item_id'],pr_pdf_page=g['pdf_page'],pr_source_url=g['source_url'],pr_attributed_survey=g['acquisition_attribution'],evidence=note,scope='published image identity or collection attribution; raw trace identity unverified'))
    save('survey_profiles.csv',overlap)
    notes=[
     ('SP.S.WEQ-3','SP',17,'Printed identifier','The scan reads VNTRO1-04 PC with a wide capital O; other cards print VNTR01. The published letterform is kept. A physical-core cross-identifier would require separate evidence.'),
     ('SP.S.EEQ-2','SP',35,'Distinct time labels','The two survey times are labelled Primary site and Secondary site. A Crossing time occurs on other cards, but it is not the name of the second entry here.'),
     ('SP.S.WEQ-6','SP',26,'Analog survey','Seismic record is explicitly qualified analog seismic only. The associated profile carries Station 6B survey annotations; only the printed image is matched to PR Fig. 20.'),
     ('SP.S.WEQ-2','SP',14,'Priority','The secondary-priority proposal was occupied as Site 854. A prospective priority is distinct from actual occupancy.'),
     ('SP.S.EEQ-4A','SP',44,'Independent proposal','EEQ-4A has its own survey station, geographical location and priority. The reviewed PR station record does not name it as an occupied proposal; actual Hole 846A belongs to Site 846 (EEQ-4).'),
     ('SP.S.EEQ-5','SP',47,'Proposal-only','The candidate has an independent site card; none of the eleven preliminary site headings identifies an occupation of EEQ-5.'),
     ('PR.OPS.846','PR',83,'Changed sequence','The planned order after Site 845 was changed to pass Baltra and collect multishot cameras and batteries. EEQ-4 (846) preceded EEQ-3 (847). SP Table 2 lists the planned order.'),
     ('PR.OPS.849','PR',89,'Station location and datum','The preliminary operations report says the beacon was dropped approximately 7.5 km north of the proposed location. Comparing SP Table 1 coordinates and PR Table 1 Hole 849A coordinates gives 9.01 km great-circle separation. These are distinct comparisons with different named points.'),
     ('PR.OPS.850','PR',91,'New station','Available time allowed a new site to supplement the planned stations. Its science heading reads Site 850 (new site), PDF p. 18. There is no prospectus site card.'),
     ('PR.F15','PR',50,'Printed site identifier','The caption first prints Sites 881, later names 851. Site 851 is attached to the age-labelled line on the map. The remaining six western sites have station symbols and no independently labelled time series.'),
     ('PR.F15','PR',50,'Coordinate reading','The plotted modern centre yields 2.43 N, 109.95 W from the map ticks. Hole 851A in PR Table 1 is 2 degrees 46.22 minutes N and 110 degrees 34.31 minutes W. The graphical reading differs by about 79 km; no offset correction is applied.'),
     ('PR.F2','PR',32,'Magnetic lineations','Caption names eastern transect sites 844–847 and gives the ages of magnetic lineations in millions of years. Those labels are not individual age-tagged coordinates for the four sites.'),
     ('PR.T1','PR',29,'Reported maxima','Hole 846B interval drilled is 422.4 m. PR operations resume, PDF p. 99, gives maximum penetration of 393.6 m for the leg. Both values remain in their source-specific fields.'),
     ('PR.T1','PR',30,'Independent percentage field','Hole 849D XCB columns print 214.2 m cored, 219.69 m recovered and 102.3% recovery. The first two displayed values give 102.56%; the published percentage remains 102.3.'),
     ('PR.T1','PR',30,'Source totals','Site 854 uses APC on all holes. Overall and APC-only site totals both list 120.1 m cored and 122.93 m recovered; overall percent is 102.4 and the APC column prints 102.3.'),
     ('PR.TECH.LAB','PR',110,'Source totals','Lab statistics list 5536.6 m recovered. Scientific Table 1 and the operations resume list 5536.8 m. The sum of the 42 displayed hole values in Table 1 is 5536.78 m.'),
     ('PR.OPS.TIME','PR',100,'Printed rounding','The chart percentages 59.3, 34.4 and 6.4 sum to 100.1. All three labels retain their published precision.')
    ]
    save('editorial_notes.csv',[dict(note_id=f'PP{n:02d}',item_id=item,doc_id=d,pdf_page=pg,topic=topic,note=txt,source_url=(SP if d=='SP' else PR)+str(pg)) for n,(item,d,pg,topic,txt) in enumerate(notes,1)])
if __name__=='__main__':main()
