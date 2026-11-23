function value = run(tag,role,varargin)
% Execute one public interface. Each call accepts the interface's original id.
menu = accore.register(tag);
role = char(role);
if strcmp(role,'workflow') && ~isempty(menu.workflow)
    value = feval(menu.workflow,varargin{:});
    return
end
if isempty(menu.entry) || ~ismember(role,strsplit(menu.roles))
    error('Acycle:Core:Role','%s does not provide %s.',menu.tag,role);
end
if strcmp(role,'helper')
    % Insert the Core policy only when the request has no explicit version.
    start = 1;
    input = struct();
    pos = 0;
    if ~isempty(varargin) && isstruct(varargin{1})
        input = varargin{1}; pos = 1; start = 2;
    end
    for k = start:2:numel(varargin)-1
        if isequal(string(varargin{k}),"input")
            input = varargin{k+1}; pos = k+1;
        end
    end
    if isstruct(input) && isscalar(input) && ~isfield(input,'operation')
        input.operation = menu.default;
        if pos, varargin{pos} = input; else, varargin = [{'input',input},varargin]; end
    end
end
value = feval([menu.entry,'_',role],varargin{:});
end
