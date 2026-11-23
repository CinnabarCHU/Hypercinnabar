function value = acMenuInvoke(tag,role,varargin)
% Dispatch an enumerated public menu role. Live graphics never enter MAT snapshots.
args=varargin;
id=[];
live=[];
if strcmp(role,'analyzer')
    if numel(args)>=2, id=args{2}; args(2)=[]; end
else
    start=1;
    if ~isempty(args) && isstruct(args{1}), start=2; end
    remove=false(size(args));
    seenId=false;
    for k=start:2:numel(args)-1
        key=args{k};
        if isequal(key,'id') || isequal(key,"id")
            if ~seenId, id=args{k+1}; remove(k:k+1)=true; seenId=true; end
        elseif strcmp(role,'plotter') && (isequal(key,'target') || isequal(key,"target"))
            target=args{k+1};
            if isscalar(target) && (isgraphics(target,'axes') || isgraphics(target,'figure'))
                live=target;
                args{k+1}=struct('kind',get(target,'Type'));
            elseif ~isempty(target)
                args{k+1}=struct('kind','invalid');
            end
        end
    end
    args(remove)=[];
end
journal=aclog.interfaceId(id,false);
% A relocated chronology must retain its input bytes in the public journal.
for k=1:numel(args)
    if isstruct(args{k}) && isscalar(args{k}) && isfield(args{k},'inputfile')
        args{k}=accompat.inputSnapshot(args{k});
    end
end
request=struct('args',{args});
if strcmp(tag,'linegenerator') && strcmp(role,'helper')
    % Capture the seed expression from both pinned redmark.m files, line 21.
    request.redNoiseSeed=sum(100*clock); %#ok<CLOCK>
end
value=acMenuExecute(tag,role,request,journal,live);
end
