function tests=test_acycle_native
% Prepared for later MATLAB execution; not run during this fork's creation.
tests=functiontests(localfunctions);
end

function testDepthToTimeParityAndShape(testCase)
root=getenv('ACYCLE_ROOT'); assert(isfolder(root),'ACYCLE_ROOT is required.');
output=tempname; mkdir(output); cleanup=onCleanup(@()rmdir(output,'s')); %#ok<NASGU>
depth=[0;1;2;3]; model=[0,10;3,40];
first=struct('id','convert','entrypoint','code/seriesanalysis/depthtotime.m', ...
    'arguments',{{array(depth),array(model)}},'nargout',2);
request=struct('acycle_root',root,'output_dir',output,'inputs',struct(), ...
    'parameters',struct('steps',{{first}},'seed',7));
oldPath=path; oldFolder=pwd; oldRng=rng;
result=acycle_native(request);
saved=load(result.artifacts.analysis_mat);
addpath(fullfile(root,'code','seriesanalysis'));
[expected,rates]=depthtotime(depth,model);
path(oldPath);
verifyEqual(testCase,saved.savedOutputs.convert{1},expected,'AbsTol',1e-12);
verifyEqual(testCase,saved.savedOutputs.convert{2},rates,'AbsTol',1e-12);
verifyEqual(testCase,size(saved.savedOutputs.convert{1}),size(expected));
verifyEqual(testCase,pwd,oldFolder);
verifyEqual(testCase,rng,oldRng);
verifyTrue(testCase,result.provenance.all_source_hashes_verified);
end

function testMultiStepReferences(testCase)
root=getenv('ACYCLE_ROOT'); assert(isfolder(root),'ACYCLE_ROOT is required.');
output=tempname; mkdir(output); cleanup=onCleanup(@()rmdir(output,'s')); %#ok<NASGU>
% The source Gaussian membership helper accepts a numeric vector and parameters.
% Two ordinary numerical steps test reference transport without a surrogate implementation.
x=(-3:0.1:3)';
first=struct('id','gaussian','entrypoint','code/misc/gaussmf.m', ...
    'arguments',{{array(x),array([1,0])}},'nargout',1);
second=struct('id','rho','entrypoint','code/seriesanalysis/rhoAR1.m', ...
    'arguments',{{struct('kind','ref','step','gaussian','output',1)}},'nargout',1);
request=struct('acycle_root',root,'output_dir',output,'inputs',struct(), ...
    'parameters',struct('steps',{{first,second}}));
result=acycle_native(request); saved=load(result.artifacts.analysis_mat);
oldPath=path; restore=onCleanup(@()path(oldPath)); %#ok<NASGU>
addpath(fullfile(root,'code','misc'),fullfile(root,'code','seriesanalysis'));
verifyEqual(testCase,saved.savedOutputs.gaussian{1},gaussmf(x,[1,0]),'AbsTol',1e-12);
verifyEqual(testCase,saved.savedOutputs.rho{1},rhoAR1(gaussmf(x,[1,0])),'AbsTol',1e-12);
end

function testDialogOrderFailsWithoutInventingAnswer(testCase)
acycle_native_dialog('initialize',{struct('name','questdlg','outputs',{{'Yes'}})});
cleanup=onCleanup(@()acycle_native_dialog('reset')); %#ok<NASGU>
verifyError(testCase,@()requestWrongDialog(),'Harness:DialogOrder');
end

function requestWrongDialog
answer=acycle_native_dialog('inputdlg'); %#ok<NASGU>
end

function value=array(x)
value=struct('kind','array','data',x(:)','shape',size(x),'dtype','double');
end
