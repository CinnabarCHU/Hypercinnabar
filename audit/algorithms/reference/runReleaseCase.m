function runReleaseCase(root)
% Match the original FORTRAN's full frequency band, three tapers and NFFT 1024.
outdir=fullfile(root,'reference-evidence');
if ~isfolder(outdir),mkdir(outdir);end
raw=sortrows(readmatrix(fullfile(root,'benchmarks','fixtures','records','lavernock.csv')),1);
d=[raw(:,1),raw(:,2)-mean(raw(:,2))];
basePath=path;
old=pwd;
sandbox=tempname;mkdir(sandbox);cd(sandbox);
set(groot,'defaultFigureVisible','off');
report=struct;
for label=["v28","master"]
    path(basePath);
    if label=="v28",base=fullfile(root,'v28','code');
    else,base=fullfile(root,'upstream','master','code');end
    addpath(fullfile(base,'seriesanalysis'),fullfile(base,'package','swa'),'-begin');
    clear specswafdr spectralswafdr specswa redconfML moveMedian rhoAR1 hpsort
    global unit2fid
    unit2fid=[];
    evalc('[r,s,~,m]=redconfML(d(:,2),.03,2,1024,2,.2,1/(2*.03),0);');
    writematrix(m,fullfile(outdir,char(label+"-ml96-lavernock.csv")));
    report.(label)=struct('rho_ml96',r,'s0_ml96',s);
    if label=="v28"
        evalc('[f,p,b,~,~,fd]=specswafdr(raw,0);');
        writematrix([f(:),p(:),b(:),fd(:,2)],fullfile(outdir,'v28-lomb.csv'));
        for pad=[1 5]
            evalc('o=spectralswafdr(d,''mtm'',2,pad,0);');
            writematrix(o,fullfile(outdir,sprintf('v28-mtm-pad%d.csv',pad)));
        end
    end
end
fid=fopen(fullfile(outdir,'release-summary.json'),'w');
fprintf(fid,'%s\n',jsonencode(report,'PrettyPrint',true));fclose(fid);
cd(old);path(basePath);
end
