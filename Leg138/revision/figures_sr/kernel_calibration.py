"""Test normalized Gaussian weights against Chapter 15's distributed analytical series."""
import numpy as np


def calibrate(data):
    output={"calibration_table":"SR.C15.TABLE7","full_support_ma":.00599,
            "display_widths_source":"Chapter 15 captions, Figures 1 and 5",
            "informative_grid_rule":"Published numeric value with at least two Table 5 contributors within ±2.995 kyr.",
            "metric":"Absolute error below 0.006 per mil on printed Table 7 values (0.01 per mil precision).",
            "series":{}}
    fractions=[1/8,1/7,1/6,1/5,1/4,1/3,1/2]
    for col in ["d18o","d13c"]:
        samples=[(float(r["age_ma"]),float(r[col])) for _,r in data["SR.C15.TABLE5"]
                 if r[col] not in ("","NA","-9999.00")]
        x,y=np.asarray(samples).T
        grids=data["SR.C15.TABLE7"]
        candidates={f:[] for f in fractions}
        masks_disagree=0
        for _,row in grids:
            center=float(row["age_ma"]);published=float(row[col])
            dx=x-center
            use=np.abs(dx)<=.00599/2
            if np.any(use)!=(published!=-9999):
                masks_disagree+=1
            if np.sum(use)<2 or published==-9999:continue
            for frac in fractions:
                w=np.exp(-.5*np.square(dx[use]/(.00599*frac)))
                error=abs(np.average(y[use],weights=w)-published)
                candidates[frac].append((center,error))
        tests={}
        for fraction,values in candidates.items():
            centers,errors=np.asarray(values).T
            tests["1/%d"%round(1/fraction)]={
                "multisample_points":len(values),
                "fraction_within_0.006":round(float(np.mean(errors<.006)),5),
                "median_absolute_error_permil":round(float(np.median(errors)),6),
                "younger_than_4Ma_fraction":round(float(np.mean(errors[centers<4]<.006)),5),
                "4Ma_or_older_fraction":round(float(np.mean(errors[centers>=4]<.006)),5)}
        output["series"][col]={"grid_rows":len(grids),"presence_mask_disagreements":masks_disagree,
                                "sigma_to_full_width":tests}
    return output
