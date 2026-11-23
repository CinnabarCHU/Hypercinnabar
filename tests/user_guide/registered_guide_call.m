function [reply,journal,runId]=registered_guide_call(menu,role,p,folder)
% A fixed client of *public* installed Harness tools. MATLAB here supplies test
% inputs, links cross-menu data, and grades returns. All roles execute in the
% Cordis tool -> packaged Node plugin -> Python -> separate MATLAB process.
ws=getenv('ACYCLE_WORKSPACE');
args=struct('menu',menu); journal=''; runId='';
for field={'input','override','params','plt','dat','res'}
    k=field{1}; if isfield(p,k), args.(k)=p.(k); end
end
if isfield(p,'file_input')
    [~,n,e]=fileparts(p.file_input.path); frozen=fullfile(ws,[n e]);
    copyfile(p.file_input.path,frozen);
    args.input_path=[n e]; args.input_kind=p.file_input.kind; args.input_field=p.file_input.field;
end
if isfield(p,'helper_journal'), args.helper_run_id=fromJournal(p.helper_journal); end
if isfield(p,'analyzer_journal'), args.analyzer_run_id=fromJournal(p.analyzer_journal); end
if isfield(p,'replay_journal'), args=struct('run_id',fromJournal(p.replay_journal)); end
if isfield(p,'target_kind')
    args.target=p.target_kind;
    if strcmp(args.target,'none'), args.target='original'; end
end
job=fullfile(folder,'public-call.json'); result=fullfile(folder,'public-result.json');
fid=fopen(job,'w'); fprintf(fid,'%s',jsonencode(struct('name',['acycle_menu_' role],'arguments',args))); fclose(fid);
% These paths belong to this test checkout and its runner temp directory.
cmd=sprintf('node "%s" "%s" "%s"',fullfile(fileparts(mfilename('fullpath')),'registered_tool.mjs'),job,result);
[rc,detail]=system(cmd); reply=struct('status','failed','completion','','files',{{}});
if ~isfile(result)
    reply.error=struct('identifier','Acycle:Test:ToolRegistry','message',detail); return
end
rec=jsondecode(fileread(result));
if rc~=0 || ~isfield(rec,'status') || ~strcmp(rec.status,'completed')
    reply.error=struct('identifier','Acycle:Test:PublicTool','message',jsonencode(rec)); return
end
runId=rec.run_id; journal=fullfile(ws,'.acycle','runs',runId,rec.journal);
reply.status='ok'; reply.completion=rec.completion;
for fields=fieldnames(rec.artifacts)'
    k=fields{1};
    if startsWith(k,'figure_') && isfile(rec.artifacts.(k))
        [~,n,e]=fileparts(rec.artifacts.(k)); copyfile(rec.artifacts.(k),fullfile(folder,[n e]));
        reply.files{end+1}=[n e];
    end
end
end
function id=fromJournal(journal)
t=regexp(journal,'[/\\]runs[/\\](\d{8}T\d{6}Z-[a-f0-9]{12})[/\\]outputs[/\\]journals[/\\]','tokens','once');
assert(~isempty(t),'Expected a registered Harness journal'); id=t{1};
end
