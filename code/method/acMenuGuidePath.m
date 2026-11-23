function guard = acMenuGuidePath()
% Keep bare calls inside GUIDE wrappers on the pinned GUIDE search path.
root=fileparts(fileparts(fileparts(mfilename('fullpath'))));
old=path;
current=fullfile(root,'upstream','master');
if strcmp(pwd,current) || startsWith(pwd,[current,filesep])
    error('Acycle:Menu:WorkingDirectory','Run GUIDE calls outside the master source tree.');
end
parts=strsplit(old,pathsep);
remove=strcmp(parts,current) | startsWith(parts,[current,filesep]);
guard=[];
if ~any(remove), return; end
guard=onCleanup(@() path(old));
path(strjoin(parts(~remove),pathsep));
baseline=fullfile(root,'upstream','acycle');
for folder={fullfile(root,'upstream','recovered','code'),fullfile(baseline,'code'),fullfile(baseline,'data')}
    if isfolder(folder{1}), addpath(genpath(folder{1})); end
end
end
