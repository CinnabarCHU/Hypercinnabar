function test_master_export()
folder = fullfile(getenv('RUNNER_TEMP'),'acycle-master-methods');
oldPath = path; oldDir = pwd;
guard = onCleanup(@() restore(oldPath,oldDir)); %#ok<NASGU>
cd(folder); restoredefaultpath; setup_method;
assert(isempty(which('acmethods.Bandpass.analyzer')));
p=acmaster.RegularInterpolation.helper(struct('data',[(0:7)',(0:7)'.^2],'samplingInterval',2));
[r,id]=acmaster.RegularInterpolation.analyzer(p);
assert(isequal(r.interpolated,[0 0;2 4;4 16;6 36]) && isequaln(r,aclog.replay(id)));
assert(isempty(which('acycleInterpolateSeries')));
end
function restore(oldPath,oldDir)
cd(oldDir); path(oldPath);
end
