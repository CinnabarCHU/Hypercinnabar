% A dedicated MATLAB process for the portable Acycle application.
root = getenv('ACYCLE_PORTABLE_WORKSPACE');
state = getenv('ACYCLE_PORTABLE_STATE');
token = getenv('ACYCLE_PORTABLE_TOKEN');
stopFile = getenv('ACYCLE_PORTABLE_STOP');
try
    cd(root);
    addpath(root);
    t = timer('ExecutionMode','fixedSpacing','Period',0.5,'BusyMode','drop', ...
        'TimerFcn',@(~,~)portable_stop(stopFile));
    start(t);
    fig = start_local_demo();
    setappdata(fig,'AcyclePortableStopTimer',t);
    receipt = struct('status','ready','token',token,'release',version('-release'), ...
        'arch',computer('arch'),'pid',feature('getpid'),'prefdir',prefdir,'tempdir',tempdir);
catch err
    receipt = struct('status','failed','token',token,'message',getReport(err,'extended','hyperlinks','off'));
end
target = fullfile(root,'generated','portable-host.json');
if ~isfolder(fileparts(target)), mkdir(fileparts(target)); end
fid = fopen([target,'.tmp'],'w','n','UTF-8');
fwrite(fid,jsonencode(receipt),'char'); fclose(fid);
movefile([target,'.tmp'],target,'f');

function portable_stop(file)
if isfile(file)
    delete(file);
    exit;
end
end
