-- Published replicate analyses and the separately archived final series.
SELECT print_page,panel,print_row,section,offset_cm,species,lab,d18o,d13c
FROM c43_appa_print WHERE section='846B-1H-1' AND offset_cm='33';
SELECT source_line,depth_rmcd,age_ma,d18o,d13c FROM noaa_final WHERE depth_rmcd='0.330';

-- Two published temperatures for one sample.
SELECT print_page,print_row,sample,rmcd,sst_c FROM c27_t1_print WHERE row_no=171;
SELECT source_line,col_01 AS sample,col_03 AS rmcd,col_16 AS sst_c
FROM pangaea_807824 WHERE col_01='138-846C-4H-1,68-70';

-- Regular grid with gaps converted to SQL NULL.
SELECT age_ma,d18o,d13c FROM c15_interpolated_numeric ORDER BY row_no;

-- Versions of the bulk-sediment table and unclear datum boundaries.
SELECT edition,scope,row_count,source FROM datasets WHERE item='c39_t2';
SELECT source_line,source_line_end,datum,raw_literal FROM c23_t3_cd WHERE record_note<>'';
