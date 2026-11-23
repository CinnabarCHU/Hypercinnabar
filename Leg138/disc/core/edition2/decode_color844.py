"""Recover the nine evidence-backed arrays in the published COL844B.FIN container."""
import argparse
import hashlib
import json
import struct
from array import array
from pathlib import Path
from extract_fields import writer,write_rows

LABELS=["MBSF","Blue","Red","Near IR","Composite Depth (m)","affine","Red/Blue","IR/Red","IR/Blue"]
KEYS=["mbsf","blue_pct","red_pct","near_ir_pct","composite_depth_m","affine","red_over_blue","ir_over_red","ir_over_blue"]
ARRAY_STARTS=[908,39689,78471,117253,156035,194817,233599,272380,311162]
def binary32(x):
    return struct.pack(">f",x)
def as_float(x):
    return struct.unpack(">f",x)[0]

def normalized_with_addresses(raw):
    values=bytearray()
    addresses=array("I")
    i=0
    while i<len(raw):
        addresses.append(i)
        if raw.startswith(b"\r\n",i):
            values.append(10)
            i+=2
        else:
            values.append(raw[i])
            i+=1
    addresses.append(len(raw))
    return bytes(values),addresses

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("primary",type=Path)
    p.add_argument("output",type=Path)
    a=p.parse_args()
    d=a.primary/"SITE_844/COLOR"
    path=d/"COL844B.FIN"
    raw=path.read_bytes()
    norm,addr=normalized_with_addresses(raw)
    assert raw.count(b"\n")==raw.count(b"\r\n")==2736
    assert list(struct.unpack_from(">9H",norm,512))==[6441]*9
    assert [norm[548+40*i:548+40*i+40].split(b"\0")[0].decode("ascii") for i in range(9)]==LABELS
    ascii_rows=[]
    removed=[]
    for companion in [d/"COL844BH.FIN",d/"COL844BX.FIN"]:
        for line,row in enumerate(companion.read_text().splitlines(),1):
            if companion.stem.endswith("X") and line<=3:
                removed.append((companion.name,line,row))
                continue
            tokens=row.split()
            sample,fields=tokens[:8],tokens[8:14]
            ascii_rows.append((companion.name,line,sample,list(map(float,fields))))
    assert len(ascii_rows)==6441
    all_values={}
    ratio_discrepancies=[]
    repaired=[]
    summaries=[]
    with writer(a.output/"binary_color_byte_map.csv.gz",["row_1_based","field","download_offset_0_based","download_length","source_decode"]) as bytemap:
        for j,(label,key,begin) in enumerate(zip(LABELS,KEYS,ARRAY_STARTS)):
            offset=begin
            decoded=[]
            repairs=0
            for i,(filename,line,sample,fields) in enumerate(ascii_rows):
                if j<6:
                    expected=binary32(fields[j])
                else:
                    numerator=(2,3,3)[j-6]
                    denominator=(1,2,1)[j-6]
                    expected=binary32(as_float(binary32(fields[numerator]))/as_float(binary32(fields[denominator])))
                if i==0 and j in [6,7]:
                    printed=as_float(norm[offset:offset+4])
                    ratio_discrepancies.append((i+1,key,printed,as_float(expected)))
                    expected=norm[offset:offset+4]
                compressed=expected.replace(b"\r\n",b"\n")
                nxt=offset+len(compressed)
                assert norm[offset:nxt]==compressed,(key,i+1)
                source_offset,source_end=addr[offset],addr[nxt]
                value_bytes=raw[source_offset:source_end].replace(b"\r\n",b"\n")
                rule="download_CRLF_to_LF"
                if len(value_bytes)==3:
                    # Original 0D 0A is indistinguishable in transport from original 0A.
                    # Exactly one inverse layout must fit the independent ASCII or ratio evidence.
                    possibilities=[value_bytes[:k]+b"\r"+value_bytes[k:] for k,c in enumerate(value_bytes) if c==10]
                    selected=[v for v in possibilities if v==expected]
                    assert len(selected)==1
                    value_bytes=selected[0]
                    rule="embedded_0D0A_restored_with_reference"
                    repairs+=1
                    repaired.append((i+1,key,source_offset,source_end-source_offset,expected.hex()))
                assert value_bytes==expected
                decoded.append(as_float(value_bytes))
                bytemap.writerow((i+1,key,source_offset,source_end-source_offset,rule))
                offset=nxt
            all_values[key]=decoded
            summaries.append((key,label,addr[548+40*j],addr[begin],addr[offset],offset-begin,6441,repairs))
    with writer(a.output/"binary_color844.csv.gz",["binary_row","ascii_file","ascii_line","ascii_sample_id",*KEYS]) as out:
        for i,(file,line,sample,_) in enumerate(ascii_rows):
            out.writerow([i+1,file,line," ".join(sample),*[format(all_values[key][i],".9g") for key in KEYS]])
    write_rows(a.output/"binary_arrays.csv",["field","embedded_label","download_label_offset","download_data_start","download_data_end_exclusive","norm_data_bytes","items","ambiguous_CRLF_recoveries"],summaries)
    write_rows(a.output/"binary_ascii_only.csv",["ascii_file","line","source_text"],removed)
    write_rows(a.output/"binary_repair_notes.csv",["row","field","download_start","download_bytes","reconstructed_hex"],repaired)
    write_rows(a.output/"binary_ratio_differences.csv",["row","field","binary32_published","binary32_recomputed"],ratio_discrepancies)
    report={"source_file":"SITE_844/COLOR/COL844B.FIN","source_bytes":len(raw),"source_sha256":hashlib.sha256(raw).hexdigest(),"array_rows":6441,"column_count":9,"source_addressed_values":6441*9,"values_matching_six_companion_ascii_columns":6441*6,"ratio_values_equal_to_binary32_quotient":6441*3-len(ratio_discrepancies),"ratio_first_row_differences":len(ratio_discrepancies),"ambiguous_byte_sequences_resolved":len(repaired),"ascii_bx_only_rows":3,"container_metadata_outside_arrays":"undocumented"}
    (a.output/"binary_verification.json").write_text(json.dumps(report,indent=2)+"\n")
    print(report)
if __name__=="__main__":
    main()
