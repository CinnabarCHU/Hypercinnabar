function test_migration
% Smoke tests shared by MATLAB and Octave. Source pinned in upstream/acycle.
root = fileparts(fileparts(mfilename('fullpath')));
addpath(root);
setup_migration();
folder = tempname;
mkdir(folder);
prior = getenv('ACYCLE_LOG_DIR');
setenv('ACYCLE_LOG_DIR', folder);
cleanup = onCleanup(@() restore(folder, prior));
x = [0; 1.1; 2.5; 3.1; 7.3; 9.2];
[opts, h] = acmethods.circularspec.helper(struct('data', x));
assert(opts.p1 == min(diff(x)) && opts.pn == 100);
opts.pn = 37;
[actual, a] = acmethods.circularspec.analyzer(opts);
[P, R, t0] = circularspec(x, opts.p1, opts.p2, 37, 2, 0);
assert(isequaln(actual.P,P) && isequaln(actual.R,R) && isequaln(actual.t0,t0));
events = journal(a);
assert(strcmp(events{1}.info.op, 'circularspec-v1.0/analyzer'));
assert(strcmp(events{end}.info.status, 'done'));
savedParams = aclog.read(a,events{1}.info.params);
savedReturn = aclog.read(a,events{end}.info.retval);
assert(isequaln(savedParams,opts) && isequaln(savedReturn,actual));
savedHelper = journal(h);
recommended = aclog.read(h,savedHelper{end}.info.retval);
assert(recommended.pn == 100);
bad = aclog.newId(folder);
caught = false;
try
    acmethods.circularspec.analyzer(rmfield(opts,'pn'), bad);
catch
    caught = true;
end
assert(caught);
e=journal(bad);
assert(strcmp(e{2}.attr,'error') && strcmp(e{3}.info.status,'cancelled') && isempty(e{3}.info.retval));
caught=false;
try
    acmethods.circularspec.analyzer(opts,fullfile(folder,'missing'));
catch err
    caught=strcmp(err.identifier,'Acycle:Logger:UnknownId');
end
assert(caught);
[rv, i] = aclog.invoke('test-v1/incomplete', struct(), [], @partial);
e=journal(i);
assert(strcmp(e{end}.info.status,'incomplete') && isequal(aclog.read(i,e{end}.info.retval),rv));
[~, n] = aclog.invoke('test-v1/empty',struct(),[],@(p) []);
e=journal(n); assert(strcmp(e{end}.info.status,'done') && isempty(e{end}.info.retval));
fprintf('Call journals, recovered parameters, full argument call, original exception and three outcomes passed.\n');
end

function [v, s] = partial(~)
v = 17;
s = 'incomplete';
end

function result = journal(id)
s = regexp(strtrim(fileread(id)), '\r?\n', 'split');
result = cellfun(@jsondecode,s,'UniformOutput',false);
end

function restore(folder, prior)
setenv('ACYCLE_LOG_DIR',prior);
rmdir(folder,'s');
end
