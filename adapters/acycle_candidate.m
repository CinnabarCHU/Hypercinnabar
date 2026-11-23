function acycle_candidate(requestDir, outputDir, acycleRoot)
% Call the Acycle implementation installed at the selected checkout.
q = jsondecode(fileread(fullfile(requestDir,'request.json')));
old = path; restore = onCleanup(@() path(old));
addpath(fullfile(acycleRoot,'code','seriesanalysis'),fullfile(acycleRoot,'code','package','swa'));
misc = fullfile(acycleRoot,'code','misc');
if isfolder(misc), addpath(misc); end
d = readmatrix(fullfile(requestDir,'data.csv'),'NumHeaderLines',1);
p = q.params;
switch q.operation
    case 'linear'
        result = interpolate(d,p.step);
    case 'periodogram'
        [power,f] = periodogram(d(:,2),[],p.nfft,1/p.sample_interval);
        result = [f,power];
    case 'swa'
        d(:,2) = d(:,2)-mean(d(:,2));
        sp = spectralswafdr(d,p.method,p.nw,p.padding,0);
        result = sp(:,[1 2 3 5 6 10]);
    case 'gaussian'
        bounds = p.bands_per_ka;
        result = zeros(size(d,1),3);
        result(:,1) = d(:,1);
        for k = 1:2
            y = gaussfilter(d(:,2),mean(diff(d(:,1))),mean(bounds(k,:)),bounds(k,1),bounds(k,2));
            result(:,k+1) = y(:);
        end
    otherwise
        error('Unsupported Acycle operation %s',q.operation);
end
if ~isfolder(outputDir), mkdir(outputDir); end
tbl = array2table(result,'VariableNames',cellstr(string(q.output_columns)));
writetable(tbl,fullfile(outputDir,'result.csv'));
% Avoid querying an unrelated checkout when a source export has no Git metadata.
priorDir = pwd; restoreDir = onCleanup(@() cd(priorDir));
cd(acycleRoot); [status,revision] = system('git rev-parse HEAD'); cd(priorDir);
if status~=0, revision='unversioned'; end
meta = struct('method','Acycle','version',strtrim(revision),'runtime',version);
fid = fopen(fullfile(outputDir,'method.json'),'w'); assert(fid>=0);
closer = onCleanup(@() fclose(fid)); fprintf(fid,'%s\n',jsonencode(meta));
end
