function result = acycle_native(request)
%ACYCLE_NATIVE Typed transport to the pinned, unmodified Acycle implementation.
% No numerical algorithm is reimplemented here. See docs/NATIVE_API.md.
root = char(request.acycle_root);
outputDir = char(request.output_dir);
catalog = jsondecode(fileread(fullfile(fileparts(mfilename('fullpath')),'native_catalog.json')));
entries = catalog.entries;
oldPath = path; oldFolder = pwd; oldRng = rng;
oldVisible = get(groot,'DefaultFigureVisible');
oldFigures = findall(groot,'Type','figure');
cleanup = onCleanup(@()restoreState(oldPath,oldFolder,oldRng,oldVisible,oldFigures)); %#ok<NASGU>
assert(~isfile(fullfile(outputDir,'analysis.mat')),'Harness:OutputExists','Output already exists.');
if ~isfolder(outputDir), mkdir(outputDir); end
cd(outputDir);
set(groot,'DefaultFigureVisible','off');
% Verify ALL .m bytes: unchanged entrypoint bytes alone do not pin dependencies.
for k=1:numel(entries)
    source = fullfile(root,char(entries(k).id));
    assert(isfile(source) && strcmp(hashFile(source),entries(k).sha256), ...
        'Harness:SourceMismatch','Pinned source differs: %s',entries(k).id);
end
for k=1:numel(catalog.resources)
    resource=catalog.resources(k);
    source=fullfile(root,char(resource.id));
    assert(isfile(source)&&strcmp(hashFile(source),resource.sha256), ...
        'Harness:ResourceMismatch','Pinned resource differs: %s',resource.id);
end
directories = asCell(catalog.path_directories);
for k=1:numel(directories), addpath(fullfile(root,char(directories{k})),'-end'); end
bridge = fileparts(mfilename('fullpath'));
shim = fullfile(bridge,'native_dialogs');
addpath(bridge,'-begin'); addpath(shim,'-begin');
p = request.parameters;
if isfield(p,'seed'), rng(double(p.seed),'twister'); end
initialRng = rng;
inputs = getDefault(request,'inputs',struct());
inputNames = fieldnames(inputs);
for k=1:numel(inputNames)
    item = inputs.(inputNames{k});
    assert(strcmp(hashFile(item.path),item.sha256),'Harness:InputChanged','Frozen input changed.');
end
state = struct();
dialogSpecs = asCell(getDefault(p,'dialogs',{}));
dialogs = cell(size(dialogSpecs));
for k=1:numel(dialogSpecs)
    item = dialogSpecs{k};
    values = asCell(item.outputs);
    for j=1:numel(values), values{j}=decodeValue(values{j},state,inputs,outputDir,root,entries); end
    dialogs{k}=struct('name',char(item.name),'outputs',{values});
end
acycle_native_dialog('initialize',dialogs);
steps = asCell(p.steps);
receipts = cell(size(steps));
savedOutputs = struct();
artifacts = struct();
warnings = {};
for k=1:numel(steps)
    step = steps{k};
    id = char(step.id);
    assert(isvarname(id)&&~startsWith(id,'hn_')&&~isfield(state,id),'Harness:StepID','Invalid step ID.');
    before = findall(groot,'Type','figure');
    action = char(getDefault(step,'action','call'));
    outputs = {};
    receipt = struct('id',id,'action',action);
    switch action
        case {'call','script'}
            entry = lookup(entries,char(step.entrypoint));
            assert(strcmp(entry.visibility,'public'),'Harness:Private','Private helper requires its public owner.');
            functionPath = fullfile(root,char(entry.id));
            dependencyIDs=dependencyClosure(entries,char(entry.id),{});
            for j=1:numel(dependencyIDs)
                dependency=lookup(entries,dependencyIDs{j});
                if strcmp(dependency.visibility,'public')
                    addpath(fileparts(fullfile(root,dependency.id)),'-begin');
                end
            end
            % Prioritize only this entrypoint's directory; keep sibling packages
            % after MATLAB toolboxes. Always record the path actually resolved.
            addpath(fileparts(functionPath),'-begin');
            resolved = which(char(entry.name));
            assert(samePath(resolved,functionPath),'Harness:Shadowed','Wrong function resolution: %s',resolved);
            if ~strcmp(entry.kind,'script'), nativeFunction=str2func(char(entry.name)); end
            addpath(shim,'-begin');
            receipt.entrypoint = entry.id;
            receipt.resolved_path = resolved;
            receipt.sha256 = entry.sha256;
            receipt.dependency_resolution=struct();
            for j=1:numel(dependencyIDs)
                dependency=lookup(entries,dependencyIDs{j});
                if strcmp(dependency.visibility,'public')
                    receipt.dependency_resolution.(char(dependency.name))=which(char(dependency.name));
                end
            end
            if strcmp(action,'script')
                assert(strcmp(entry.kind,'script'),'Harness:Kind','Expected a script.');
                workspace = getDefault(step,'workspace',struct());
                names = fieldnames(workspace);
                for j=1:numel(names)
                    workspace.(names{j})=decodeValue(workspace.(names{j}),state,inputs,outputDir,root,entries);
                end
                outputs=runScript(functionPath,workspace,asCell(getDefault(step,'outputs',{})));
            else
                assert(~strcmp(entry.kind,'script'),'Harness:Kind','Use script action for scripts.');
                argv=asCell(getDefault(step,'arguments',{}));
                for j=1:numel(argv), argv{j}=decodeValue(argv{j},state,inputs,outputDir,root,entries); end
                defaultOut=double(~isempty(entry.outputs));
                nout=double(getDefault(step,'nargout',defaultOut));
                validateattributes(nout,{'numeric'},{'scalar','integer','>=',0,'<=',64});
                outputs=cell(1,nout);
                addpath(fileparts(functionPath),'-begin'); addpath(shim,'-begin');
                [outputs{:}]=nativeFunction(argv{:});
            end
        case {'ui_set','ui_get','ui_invoke','ui_inspect'}
            target=decodeValue(step.target,state,inputs,outputDir,root,entries);
            assert(isscalar(target),'Harness:UITarget','UI action requires one target.');
            switch action
                case 'ui_set'
                    names=fieldnames(step.properties);
                    for j=1:numel(names)
                        name=names{j};
                        assert(~endsWith(name,'Fcn')&&~endsWith(name,'Callback'), ...
                            'Harness:CallbackMutation','Cannot replace original callbacks.');
                        target.(name)=decodeValue(step.properties.(name),state,inputs,outputDir,root,entries);
                    end
                case 'ui_get'
                    names=asCell(step.properties); value=struct();
                    for j=1:numel(names), value.(char(names{j}))=target.(char(names{j})); end
                    outputs={value};
                    receipt.properties=struct();
                    for j=1:numel(names), receipt.properties.(char(names{j}))=describe(value.(char(names{j}))); end
                case 'ui_inspect'
                    outputs={inspectUI(target)};
                    receipt.ui=outputs{1};
                case 'ui_invoke'
                    property=char(getDefault(step,'callback','Callback'));
                    callback=target.(property);
                    event=struct('Source',target,'EventName',property);
                    if isfield(step,'event'), event=decodeValue(step.event,state,inputs,outputDir,root,entries); end
                    if isa(callback,'function_handle')
                        callback(target,event);
                    elseif iscell(callback)&&~isempty(callback)&&isa(callback{1},'function_handle')
                        feval(callback{1},target,event,callback{2:end});
                    else
                        error('Harness:UICallback','Callback must be an original function handle or handle cell; string evaluation is not supported.');
                    end
            end
        otherwise
            error('Harness:NativeAction','Unknown native action: %s',action);
    end
    drawnow;
    created = newFigures(before);
    state.(id)=struct('outputs',{outputs},'figures',{num2cell(created)});
    saved=cell(size(outputs)); descriptions=cell(size(outputs));
    for j=1:numel(outputs)
        saved{j}=snapshot(outputs{j},0);
        descriptions{j}=describe(outputs{j});
        stem=sprintf('%s_output_%d',id,j);
        value=outputs{j};
        if (isnumeric(value)||islogical(value))&&ismatrix(value)&&~isempty(value)&&isreal(value)
            destination=fullfile(outputDir,[stem '.csv']);
            writematrix(value,destination); artifacts.(stem)=destination;
        elseif istable(value)||istimetable(value)
            if istimetable(value), value=timetable2table(value); end
            destination=fullfile(outputDir,[stem '.csv']);
            writetable(value,destination); artifacts.(stem)=destination;
        end
    end
    savedOutputs.(id)=saved;
    receipt.outputs=descriptions;
    receipt.figure_count=numel(created);
    receipts{k}=receipt;
    % Checkpoint after each step: a later GUI dialog failure preserves progress.
    writeJson(fullfile(outputDir,'native-progress.json'),struct('completed_steps',{receipts(1:k)}));
end
dialogTrace=acycle_native_dialog('finish');
finalRng=rng;
matPath=fullfile(outputDir,'analysis.mat');
save(matPath,'savedOutputs','receipts','initialRng','finalRng','dialogTrace','-v7.3');
artifacts.analysis_mat=matPath;
figures=newFigures(oldFigures);
for k=1:numel(figures)
    stem=sprintf('figure_%03d',k);
    try
        destination=fullfile(outputDir,[stem '.fig']);
        savefig(figures(k),destination); artifacts.([stem '_fig'])=destination;
    catch err
        warnings{end+1}=sprintf('%s FIG: %s',stem,err.message); %#ok<AGROW>
    end
    try
        destination=fullfile(outputDir,[stem '.png']);
        try, exportgraphics(figures(k),destination,'Resolution',150);
        catch, print(figures(k),destination,'-dpng','-r150'); end
        artifacts.([stem '_png'])=destination;
    catch err
        warnings{end+1}=sprintf('%s PNG: %s',stem,err.message); %#ok<AGROW>
    end
end
% Register files explicitly produced by original functions, including nested
% Undatable/COCO output directories. Never register files outside this run.
files=dir(fullfile(outputDir,'**','*'));
registered=struct2cell(artifacts);
for k=1:numel(files)
    if files(k).isdir, continue; end
    destination=fullfile(files(k).folder,files(k).name);
    if ~any(strcmp(registered,destination))
        artifacts.(sprintf('native_file_%04d',k))=destination;
    end
end
result=struct('status','completed','backend','matlab','operation','native', ...
    'summary',struct('steps',{receipts},'warnings',{warnings},'dialog_trace',{dialogTrace}), ...
    'artifacts',artifacts,'parameters',p, ...
    'provenance',struct('repository',catalog.repository,'revision',catalog.revision, ...
    'all_source_hashes_verified',true,'source_files',numel(entries), ...
    'bundled_resources_verified',numel(catalog.resources), ...
    'matlab_version',version,'transport','typed-native-v1', ...
    'scientific_equivalence_validated',false));
end

function value=decodeValue(spec,state,inputs,outputDir,root,entries)
switch char(spec.kind)
    case 'literal'
        value=spec.value;
    case 'array'
        data=spec.data;
        if iscell(data)
            numeric=zeros(1,numel(data));
            for k=1:numel(data)
                if ischar(data{k})||isstring(data{k}), numeric(k)=str2double(data{k});
                else, numeric(k)=double(data{k}); end
            end
            data=numeric;
        end
        value=reshape(cast(data,char(getDefault(spec,'dtype','double'))),double(spec.shape(:)'));
    case 'complex'
        value=complex(decodeValue(spec.real,state,inputs,outputDir,root,entries), ...
            decodeValue(spec.imag,state,inputs,outputDir,root,entries));
    case 'cell'
        value=asCell(spec.items);
        for k=1:numel(value), value{k}=decodeValue(value{k},state,inputs,outputDir,root,entries); end
    case 'struct'
        value=struct(); names=fieldnames(spec.fields);
        for k=1:numel(names), value.(names{k})=decodeValue(spec.fields.(names{k}),state,inputs,outputDir,root,entries); end
    case 'input'
        item=inputs.(char(spec.name));
        switch char(getDefault(spec,'format','matrix'))
            case 'matrix', value=readmatrix(item.path);
            case 'table', value=readtable(item.path);
            case 'path', value=char(item.path);
            case 'image', value=imread(item.path);
            case 'mat'
                loaded=load(item.path,char(spec.variable));
                value=loaded.(char(spec.variable));
            otherwise, error('Harness:InputFormat','Unsupported input format.');
        end
    case 'ref'
        previous=state.(char(spec.step));
        value=previous.outputs{double(getDefault(spec,'output',1))};
    case 'figure'
        previous=state.(char(spec.step));
        value=previous.figures{double(getDefault(spec,'index',1))};
    case 'output_path'
        relative=char(spec.path);
        assert(~startsWith(relative,filesep)&&~contains(relative,'..')&&~contains(relative,':'), ...
            'Harness:OutputPath','Output path must be relative.');
        value=fullfile(outputDir,relative);
        parent=fileparts(value); if ~isfolder(parent), mkdir(parent); end
    case 'function'
        entry=lookup(entries,char(spec.entrypoint));
        assert(strcmp(entry.visibility,'public')&&strcmp(entry.kind,'function'),'Harness:FunctionHandle','Expected public function.');
        expected=fullfile(root,char(entry.id));
        addpath(fileparts(expected),'-begin');
        assert(samePath(which(char(entry.name)),expected),'Harness:Shadowed','Function handle resolution mismatch.');
        value=str2func(char(entry.name));
    case 'ui'
        owner=decodeValue(spec.owner,state,inputs,outputDir,root,entries);
        if isfield(spec,'component')
            value=owner.(char(spec.component));
        else
            if isa(owner,'matlab.apps.AppBase'), owner=owner.UIFigure; end
            values=findall(owner);
            for property={'tag','type','text'}
                key=property{1};
                if ~isfield(spec,key), continue; end
                matches=false(size(values));
                for j=1:numel(values)
                    names=struct('tag','Tag','type','Type','text','Text');
                    name=names.(key);
                    if isprop(values(j),name), matches(j)=isequal(values(j).(name),spec.(key)); end
                end
                values=values(matches);
            end
            if isfield(spec,'index'), value=values(double(spec.index));
            else
                assert(numel(values)==1,'Harness:UIAmbiguous','UI selector matched %d objects; refine or supply index.',numel(values));
                value=values(1);
            end
        end
    otherwise
        error('Harness:Value','Unknown value descriptor.');
end
if isfield(spec,'fields')
    names=asCell(spec.fields);
    for k=1:numel(names), value=value.(char(names{k})); end
end
if isfield(spec,'columns'), value=value(:,double(spec.columns)); end
end

function hn_outputs=runScript(hn_path,hn_workspace,hn_names)
% All variable names were validated. Script text is only pinned upstream text.
hn_fields=fieldnames(hn_workspace);
for hn_i=1:numel(hn_fields)
    assert(isvarname(hn_fields{hn_i})&&~startsWith(hn_fields{hn_i},'hn_'),'Harness:Variable','Invalid workspace name.');
    eval([hn_fields{hn_i} '=hn_workspace.(hn_fields{hn_i});']);
end
[~,hn_scriptname]=fileparts(hn_path);
assert(isvarname(hn_scriptname),'Harness:Script','Invalid pinned script name.');
% RUN(fullpath) changes the folder to the upstream source directory. Invoke
% the pinned name in this workspace so relative outputs start in the run.
eval(hn_scriptname);
hn_outputs=cell(1,numel(hn_names));
for hn_i=1:numel(hn_names)
    hn_name=char(hn_names{hn_i});
    assert(isvarname(hn_name)&&~startsWith(hn_name,'hn_'),'Harness:Variable','Invalid output name.');
    hn_outputs{hn_i}=eval(hn_name);
end
end

function info=inspectUI(owner)
if isa(owner,'matlab.apps.AppBase'), owner=owner.UIFigure; end
objects=findall(owner); info=cell(size(objects));
for k=1:numel(objects)
    item=struct('index',k,'class',class(objects(k)));
    for property={'Type','Tag','Text','String','Value','Name','Enable','Visible','Data'}
        key=property{1};
        if isprop(objects(k),key), item.(key)=describe(objects(k).(key)); end
    end
    callbacks={};
    for property={'Callback','ButtonPushedFcn','ValueChangedFcn','SelectionChangedFcn','MenuSelectedFcn','CellEditCallback'}
        key=property{1};
        if isprop(objects(k),key)&&~isempty(objects(k).(key)), callbacks{end+1}=key; end %#ok<AGROW>
    end
    item.callbacks=callbacks; info{k}=item;
end
end

function info=describe(value)
info=struct('class',class(value),'size',size(value));
if (isnumeric(value)||islogical(value))&&numel(value)<=256&&isreal(value)&&all(isfinite(value(:)))
    info.value=value;
elseif ischar(value)||isstring(value)
    if numel(value)<=2000, info.value=value; end
elseif isstruct(value)
    info.fields=fieldnames(value);
elseif istable(value)||istimetable(value)
    info.variables=value.Properties.VariableNames;
elseif iscell(value)&&numel(value)<=100
    info.items=cellfun(@describe,value,'UniformOutput',false);
end
end

function value=snapshot(value,depth)
if depth>30, value=struct('omitted','nesting depth'); return; end
if isa(value,'function_handle')
    value=struct('native_handle',func2str(value));
elseif iscell(value)
    for k=1:numel(value), value{k}=snapshot(value{k},depth+1); end
elseif isstruct(value)
    names=fieldnames(value);
    for k=1:numel(value)
        for j=1:numel(names), value(k).(names{j})=snapshot(value(k).(names{j}),depth+1); end
    end
elseif isobject(value)&&~istable(value)&&~istimetable(value)&&~isstring(value)&&~isa(value,'datetime')&&~isa(value,'duration')
    value=struct('native_object_class',class(value),'note','Live handles are session-local; inspect exported FIG/UI outputs.');
end
end

function entry=lookup(entries,id)
index=find(strcmp({entries.id},id));
assert(numel(index)==1,'Harness:Entry','Unknown catalog entrypoint.'); entry=entries(index);
end

function ids=dependencyClosure(entries,id,seen)
if any(strcmp(seen,id)), ids={}; return; end
seen{end+1}=id;
entry=lookup(entries,id); dependencies=asCell(entry.dependencies); ids={};
for k=1:numel(dependencies)
    child=char(dependencies{k});
    if any(strcmp(seen,child)), continue; end
    nested=dependencyClosure(entries,child,[seen,ids]);
    ids=unique([ids,nested,{child}],'stable');
end
end

function values=asCell(value)
if isempty(value), values={};
elseif iscell(value), values=value;
elseif isstruct(value)||isnumeric(value)||islogical(value), values=num2cell(value);
else, values=cellstr(value); end
end

function value=getDefault(s,key,fallback)
if isfield(s,key), value=s.(key); else, value=fallback; end
end

function digest=hashFile(path)
fid=fopen(path,'rb'); assert(fid>=0,'Harness:Read','Cannot read source/input.');
cleanup=onCleanup(@()fclose(fid)); %#ok<NASGU>
bytes=fread(fid,Inf,'*uint8'); md=java.security.MessageDigest.getInstance('SHA-256');
md.update(bytes); digest=lower(reshape(dec2hex(typecast(md.digest(),'uint8'),2)',1,[]));
end

function tf=samePath(first,second)
first=char(java.io.File(first).getCanonicalPath()); second=char(java.io.File(second).getCanonicalPath());
if ispc, tf=strcmpi(first,second); else, tf=strcmp(first,second); end
end

function figures=newFigures(before)
current=findall(groot,'Type','figure'); figures=current(~ismember(current,before));
end

function restoreState(oldPath,oldFolder,oldRng,oldVisible,oldFigures)
try, acycle_native_dialog('reset'); catch, end
try, figures=newFigures(oldFigures); delete(figures); catch, end
try, set(groot,'DefaultFigureVisible',oldVisible); catch, end
try, rng(oldRng); catch, end
try, cd(oldFolder); catch, end
path(oldPath);
end

function writeJson(destination,value)
fid=fopen(destination,'w'); assert(fid>=0,'Harness:Write','Cannot write progress.');
cleanup=onCleanup(@()fclose(fid)); %#ok<NASGU>
fprintf(fid,'%s\n',jsonencode(value));
end
