function [retval, id] = analyzer(params, id)
% Undatable.analyzer parameters: inputfile input_bytes nsim xfactor bootpc combine savemat savebigmat debug writedir allowreversal run1nsim sar vcloud plotsar.
% Source: https://github.com/mingsongli/acycle/blob/b52ea9f510f3be00bde9a0238b9898a1e2315b74/code/package/undatable/undatable.m#L115
% Source: https://github.com/mingsongli/acycle/blob/b52ea9f510f3be00bde9a0238b9898a1e2315b74/code/package/undatable/undatable.m#L233
if nargin < 2, id = []; end
params=accompat.inputSnapshot(params);
[retval, id] = aclog.invoke('Undatable-v1.0/analyzer', params, id, @execute);
end

function r = execute(p)
if ~isfield(p,'input_bytes'), error('Acycle:Undatable:Input','Cannot read the input chronology.'); end
folder=tempname; mkdir(folder);
cleanup=onCleanup(@() rmdir(folder,'s'));
[~,stem,extension]=fileparts(p.inputfile);
if isempty(stem), error('Acycle:Undatable:Name','Input requires a filename.'); end
inputfile=fullfile(folder,[stem,extension]);
fid=fopen(inputfile,'wb'); if fid<0, error('Acycle:Undatable:Input','Cannot stage chronology input.'); end
closer=onCleanup(@() fclose(fid));
count=fwrite(fid,p.input_bytes,'uint8'); clear closer
if count~=numel(p.input_bytes), error('Acycle:Undatable:Input','Incomplete input file.'); end
[udoutput, shadingmat, sarsummarymat, sarshadingmat] = undatable( ...
    inputfile, p.nsim, p.xfactor, p.bootpc, ...
    'combine', p.combine, 'plotme', 0, 'printme', 0, ...
    'savemat', 1, 'savebigmat', p.savebigmat, 'debug', p.debug, ...
    'writedir', [folder,filesep], 'guimode', 0, 'allowreversal', p.allowreversal, ...
    'run1nsim', p.run1nsim, 'sar', p.sar, 'vcloud', p.vcloud, ...
    'plotsar', p.plotsar);
r = struct();
r.udoutput = udoutput;
r.shadingmat = shadingmat;
r.sarsummarymat = sarsummarymat;
r.sarshadingmat = sarshadingmat;
fields={'depth', 'depth1', 'depth2', 'age', 'ageerr', 'datetype', 'probtoplot', 'p95_4', 'p68_2', 'medians', 'depthrange', 'summarymat', 'shadingmat', 'sarsummarymat', 'sarshadingmat', 'debugme'};
if p.debug, fields{end+1}='agedepmat'; end
modelFile=fullfile(folder,[stem,'.mat']);
r.plotdata=load(modelFile,fields{:}); r.input_name=[stem,extension];
if ~isempty(p.writedir)
    if ~isfolder(p.writedir), mkdir(p.writedir); end
    files=dir(fullfile(folder,'*_admodel.txt'));
    for i=1:numel(files), copyfile(fullfile(folder,files(i).name),p.writedir); end
    if p.savemat || p.savebigmat, copyfile(modelFile,p.writedir); end
end
end
