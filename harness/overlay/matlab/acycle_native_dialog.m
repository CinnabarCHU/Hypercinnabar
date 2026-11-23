function varargout=acycle_native_dialog(action,varargin)
%ACYClE_NATIVE_DIALOG Ordered explicit responses; never choose a GUI default.
persistent queue index trace
switch action
    case 'initialize'
        queue=varargin{1}; index=1; trace={};
    case 'reset'
        queue={}; index=1; trace={};
    case 'finish'
        assert(index>numel(queue),'Harness:UnusedDialogAnswers', ...
            'Unused scripted dialog responses indicate a changed GUI path.');
        varargout={trace};
    otherwise
        assert(~isempty(index)&&index<=numel(queue),'Harness:InteractionRequired', ...
            'Original Acycle requested %s. Supply its explicit dialog response or use a calculation entrypoint.',action);
        item=queue{index};
        assert(strcmp(item.name,action),'Harness:DialogOrder', ...
            'Expected dialog %s but original Acycle requested %s.',item.name,action);
        assert(numel(item.outputs)==nargout,'Harness:DialogOutputs', ...
            'Dialog %s requested %d outputs; response supplies %d.',action,nargout,numel(item.outputs));
        trace{end+1}=struct('name',action,'output_count',nargout); %#ok<AGROW>
        index=index+1; varargout=item.outputs;
end
end
