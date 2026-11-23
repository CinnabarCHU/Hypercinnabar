function [session,records] = exchange(session,records)
% Export the role journals needed for standalone replay, or import them
% into a different log directory with freshly reserved ids.
exporting = nargin == 1;
if exporting, records = struct(); end
if isfield(session,'ids')
    ids = session.ids;
elseif isfield(session,'id')
    ids = struct('workflow',session.id);
else
    return
end
for key = reshape(fieldnames(ids),1,[])
    role = key{1}; id = ids.(role);
    if isempty(id), continue; end
    if exporting
        path = aclog.interfaceId(id,true);
        r = struct('events',fileread(path),'files',struct());
        for field = {'params','rng','retval','source'}
            name = field{1}; file = [path,'.',name,'.mat'];
            if isfile(file), r.files.(name) = bytes(file); end
        end
        records.(role) = r;
    elseif isfield(records,role)
        r = records.(role);
        try
            path = aclog.interfaceId(id,true);
            if strcmp(fileread(path),r.events) && isequal(bytes([path,'.params.mat']),r.files.params), continue; end
        catch err
            if ~strcmp(err.identifier,'Acycle:Logger:UnknownId') && ~strcmp(err.identifier,'Acycle:IO:Open'), rethrow(err); end
        end
        fresh = acMenuNewId();
        path = aclog.interfaceId(fresh,true);
        for name = reshape(fieldnames(r.files),1,[])
            if ~ismember(name{1},{'params','rng','retval','source'}), error('Acycle:IO:Exchange','Unknown snapshot field.'); end
            writeBytes([path,'.',name{1},'.mat'],r.files.(name{1}));
        end
        writeBytes(path,unicode2native(r.events,'UTF-8'));
        ids.(role) = fresh;
    end
end
if isfield(session,'ids'), session.ids = ids; else, session.id = ids.workflow; end
end

function value = bytes(file)
[fid,msg] = fopen(file,'rb');
if fid<0, error('Acycle:IO:Open','%s',msg); end
cleanup = onCleanup(@()fclose(fid)); %#ok<NASGU>
value = fread(fid,Inf,'*uint8');
end

function writeBytes(file,value)
[fid,msg] = fopen(file,'wb');
if fid<0, error('Acycle:IO:Open','%s',msg); end
cleanup = onCleanup(@()fclose(fid)); %#ok<NASGU>
if fwrite(fid,value,'uint8')~=numel(value), error('Acycle:IO:Write','Incomplete snapshot %s.',file); end
end
