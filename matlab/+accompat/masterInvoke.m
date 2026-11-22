function [retval,id] = masterInvoke(operation,params,id,implementation)
% Record the exact public revision and keep the upstream sources scoped to execution.
[retval,id] = aclog.invoke(operation,params,id,@run);
    function [value,status] = run(input)
        guard = accompat.masterPath(); %#ok<NASGU>
        if nargout(implementation) == 2
            [value,status] = implementation(input);
        else
            value = implementation(input);
            status = 'done';
        end
    end
end
