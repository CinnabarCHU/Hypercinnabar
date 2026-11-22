function testModuleInventoryLayout()
% Verify the flat interface/private lookup and representative existing Core candidates.
root = fileparts(fileparts(fileparts(mfilename('fullpath'))));
oldPath = path;
tempRoot = tempname;
mkdir(tempRoot);
cleanup = onCleanup(@() acInventoryRestoreFixture(oldPath,tempRoot)); %#ok<NASGU>
codeDir = fullfile(tempRoot,'code');
privateDir = fullfile(codeDir,'private');
interfaceDir = fullfile(codeDir,'interface','Interpolation');
mkdir(privateDir);
mkdir(interfaceDir);
acInventoryWriteFixture(privateDir,'acInventoryFixtureKernel', ...
    'function y=acInventoryFixtureKernel(x), y=x+1; end');
acInventoryWriteFixture(codeDir,'acInventoryFixtureLookup', ...
    'function fn=acInventoryFixtureLookup(), fn=@acInventoryFixtureKernel; end');
acInventoryWriteFixture(interfaceDir,'acInventoryFixture_analyzer', ...
    'function y=acInventoryFixture_analyzer(x), fn=acInventoryFixtureLookup(); y=fn(x); end');
acInventoryWriteFixture(interfaceDir,'acInventoryFixtureDirect', ...
    'function y=acInventoryFixtureDirect(x), y=acInventoryFixtureKernel(x); end');
addpath(codeDir,interfaceDir);
assert(acInventoryFixture_analyzer(41)==42);
directWasHidden = false;
try
    acInventoryFixtureDirect(41);
catch err
    directWasHidden = ~isempty(strfind(err.message,'acInventoryFixtureKernel')); %#ok<STREMP>
end
assert(directWasHidden,'The interface directory should not see code/private directly.');
for revision = {'acycle','master'}
    native = fullfile(root,'upstream',revision{1},'code','seriesanalysis');
    addpath(native);
    assert(strcmp(which('interpolate'),fullfile(native,'interpolate.m')));
    data = [2 20 8;0 2 4;2 24 6;1 10 2];
    assert(isequal(select_interval(data,1,2),data([1 3 4],:)));
    assert(isequal(findduplicate(data),[0 2 4;1 10 2;2 22 7]));
    assert(isequal(findduplicate(data([1 2 4],:)),data([1 2 4],:)));
    assert(isequal(interpolate([0 2 5;2 6 8],1),[0 2;1 4;2 6]));
    assert(isequal(moveMedian((1:5)',3),[1.5;2;3;4;4.5]));
    assert(abs(rhoAR1ML([1;2;3;4])-5/11)<1e-12);
    if strcmp(revision{1},'acycle')
        padded = zeropad2([(0:5)',(1:6)'],2,1);
    else
        padded = zeropad2([(0:5)',(1:6)'],2,1,false);
        assert(~acycleSamplingIsUneven((0:5)',1e-5));
        assert(acycleSamplingIsUneven([0;1;4],1e-5));
        [strict,info] = acycleInterpolateSeries([0 2 5;2 6 9],1, ...
            'MaximumPoints',100,'MaximumElements',1000);
        assert(isequal(strict,[0 2 5;1 4 7;2 6 9]) && info.UnfilledTail==0);
        addpath(fullfile(root,'upstream','master','code','misc'));
        records = struct('name',{'b','a'},'datenum',{1,2},'bytes',{20,3});
        sorted = ac_sort_dir_entries(records,5);
        assert(isequal({sorted.name},{'a','b'}));
    end
    assert(isequal(padded(:,1),(-1:6)'));
    rmpath(native);
end
end

function acInventoryWriteFixture(folder,name,contents)
[file,msg] = fopen(fullfile(folder,[name,'.m']),'w');
assert(file>=0,msg);
cleanup = onCleanup(@() fclose(file)); %#ok<NASGU>
fprintf(file,'%s\n',contents);
end

function acInventoryRestoreFixture(oldPath,tempRoot)
path(oldPath);
rmdir(tempRoot,'s');
end
