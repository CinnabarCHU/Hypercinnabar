function test_exported_methods()
% Enter the exported directory with only the MATLAB runtime on path.
folder=fullfile(getenv('RUNNER_TEMP'),'acycle-methods');
assert(isfolder(folder),'Run migration/export_method.py Bandpass TimeOpt Undatable --output "$RUNNER_TEMP/acycle-methods" first.');
oldPath=path; origin=pwd; logroot=getenv('ACYCLE_LOG_DIR'); journal=tempname; mkdir(journal);
cleanup=onCleanup(@() restore(oldPath,origin,logroot,journal));
cd(folder); restoredefaultpath; addpath(folder); setup_method; rehash;
setenv('ACYCLE_LOG_DIR',journal);
assert(isempty(which('AC')) && isempty(which('acmethods.PowerSpectrum.analyzer')));
assert(startsWith(which('timeOptAc'),folder) && startsWith(which('undatable'),folder));
location=fileparts(which('undatable'));
assert(isfile(fullfile(location,'private','IntCal20.14c')));
t=(0:255)'; dat=[t,sin(2*pi*t/21)+.25*cos(t/12)];
p=acmethods.TimeOpt.helper(struct('dat',dat)); p.sedmin=.3; p.sedmax=1; p.numsed=4; p.cormethod=1;
[r,id]=acmethods.TimeOpt.analyzer(p); assert(isequaln(r,aclog.replay(id)));
assert(any(isfinite(r.xx(:,4))) && size(r.datopt,1)==size(dat,1));
fprintf('The exported TimeOpt package ran and replayed without the GUIDE or the repository on path.\n');
end

function restore(oldPath,origin,logroot,journal)
cd(origin); path(oldPath); setenv('ACYCLE_LOG_DIR',logroot); rmdir(journal,'s');
end
