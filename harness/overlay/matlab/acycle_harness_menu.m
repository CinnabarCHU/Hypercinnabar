function acycle_harness_menu(requestFile,responseFile)
% Execute a registered Acycle menu role. Full arrays and types travel in Acycle's own journal.
q=jsondecode(fileread(requestFile)); p=q.payload; out=q.output_dir;
previousPath=path; previousDir=pwd; previousLog=getenv('ACYCLE_LOG_DIR');
visibility=get(groot,'DefaultFigureVisible'); existing=findall(groot,'Type','figure');
cleanup=onCleanup(@()acHarnessRestore(previousDir,previousPath,previousLog,visibility,existing)); %#ok<NASGU>
journal=''; logDir=fullfile(out,'journals'); mkdir(logDir); products=fullfile(out,'products'); mkdir(products);
r=struct('status','failed','completion','','journal','','files',{{}});
try
    cd(products); addpath(q.acycle_root); setup_migration();
    setenv('ACYCLE_LOG_DIR',logDir); set(groot,'DefaultFigureVisible','off');
    if strcmp(q.role,'replay')
        [value,journal]=aclog.replay(p.replay_journal);
    else
        m=acMenuCatalog(q.menu);
        if isempty(m.entry) || ~ismember(q.role,strsplit(m.roles)), error('Acycle:Harness:Role','Unavailable role.'); end
        entry=str2func([m.entry,'_',q.role]);
        id=acMenuNewId(); journal=aclog.interfaceId(id,true);
        switch q.role
        case 'helper'
            if isfield(p,'input'), input=p.input; else, input=struct(); end
            if isfield(p,'file_input')
                f=p.file_input;
                switch f.kind
                case 'matrix'
                    imported=readmatrix(f.path,'FileType','text');
                case 'image'
                    imported=imread(f.path);
                case 'path'
                    imported=f.path;
                end
                input.(f.field)=imported;
            end
            if isfield(p,'override'), change=p.override; else, change=struct(); end
            value=entry('input',input,'override',change,'id',id);
        case 'analyzer'
            if isfield(p,'helper_journal')
                h=acHarnessReadReturn(p.helper_journal); params=h.params;
            else
                params=p.params;
            end
            value=entry(params,id);
        case 'plotter'
            args={}; h=struct();
            if isfield(p,'helper_journal'), h=acHarnessReadReturn(p.helper_journal); end
            for field={'plt','params','dat','res'}
                k=field{1};
                if isfield(p,k), args(end+1:end+2)={k,p.(k)}; %#ok<AGROW>
                elseif isfield(h,k), args(end+1:end+2)={k,h.(k)}; end %#ok<AGROW>
            end
            if isfield(p,'analyzer_journal'), args(end+1:end+2)={'res',acHarnessReadReturn(p.analyzer_journal)}; end
            if strcmp(p.target_kind,'figure')
                args(end+1:end+2)={'target',figure('Visible','off')};
            elseif strcmp(p.target_kind,'axes')
                args(end+1:end+2)={'target',axes('Parent',figure('Visible','off'))};
            end
            value=entry(args{:},'id',id);
        end
    end
    [fin,init]=acHarnessRecords(journal);
    r.completion=fin.info.status;
    r.journal=acHarnessRelative(out,journal);
    if endsWith(init.info.op,'/helper'), r.plot_selector=value.plt.operation; end
    r.summary=acHarnessSummary(value,0);
    if endsWith(init.info.op,'/plotter')
        figs=flipud(findall(groot,'Type','figure'));
        figs=figs(~ismember(figs,existing)); drawnow;
        for k=1:numel(figs)
            filename=sprintf('figure_%02d.png',k);
            try
                exportgraphics(figs(k),fullfile(out,filename),'Resolution',150);
            catch
                print(figs(k),fullfile(out,filename),'-dpng','-r150');
            end
            r.files{end+1}=filename;
        end
    end
    r.status='ok';
catch err
    r.error=struct('identifier',err.identifier,'message',err.message);
    if isempty(journal)
        logs=dir(fullfile(logDir,'**','events.jsonl'));
        if isscalar(logs), journal=fullfile(logs.folder,logs.name); end
    end
    if ~isempty(journal) && isfile(journal)
        r.journal=acHarnessRelative(out,journal);
        try
            fin=acHarnessRecords(journal); r.completion=fin.info.status;
        catch
            % Failures before fin retain their original diagnostic and open journal.
        end
    end
end
[fid,msg]=fopen(responseFile,'w','n','UTF-8');
if fid<0, error('Acycle:Harness:Write','%s',msg); end
writer=onCleanup(@()fclose(fid)); %#ok<NASGU>
fprintf(fid,'%s',jsonencode(r));
end

function [fin,init] = acHarnessRecords(journal)
lines=regexp(strtrim(fileread(journal)),'\r?\n','split');
init=jsondecode(lines{1}); fin=jsondecode(lines{end});
if ~strcmp(init.attr,'init') || ~strcmp(fin.attr,'fin'), error('Acycle:Harness:Journal','Expected a closed Acycle journal.'); end
end

function value = acHarnessReadReturn(journal)
fin=acHarnessRecords(journal);
value=aclog.read(journal,fin.info.retval);
end

function rel = acHarnessRelative(root,path)
prefix=[root,filesep];
if ~startsWith(path,prefix), error('Acycle:Harness:Journal','Unexpected journal location.'); end
rel=strrep(path(numel(prefix)+1:end),filesep,'/');
end

function s = acHarnessSummary(value,depth)
s=struct('class',class(value),'size',size(value));
if isstruct(value) && isscalar(value)
    keys=fieldnames(value);
    s.fields=keys;
    if depth<2
        s.preview=struct();
        for k=1:min(24,numel(keys))
            key=keys{k}; s.preview.(key)=acHarnessSummary(value.(key),depth+1);
        end
    end
elseif (isnumeric(value) || islogical(value)) && isreal(value) && ~issparse(value)
    if numel(value)<=32, s.value=value; else, s.first=value(1:6); end
elseif ischar(value) && isrow(value)
    s.value=value(1:min(240,end));
elseif isstring(value) && isscalar(value)
    v=char(value); s.value=v(1:min(240,end));
end
end

function acHarnessRestore(directory,previousPath,logRoot,visibility,existing)
figs=findall(groot,'Type','figure'); delete(figs(~ismember(figs,existing)));
set(groot,'DefaultFigureVisible',visibility); cd(directory); path(previousPath); setenv('ACYCLE_LOG_DIR',logRoot);
end
