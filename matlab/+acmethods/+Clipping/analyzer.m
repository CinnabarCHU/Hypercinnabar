function [retval, id] = analyzer(params, id)
% Clipping.analyzer parameters: data clip_value clip_high clip_set.
% Source: https://github.com/mingsongli/acycle/blob/b52ea9f510f3be00bde9a0238b9898a1e2315b74/code/guicode/AC.m#L2378
if nargin < 2, id = []; end
[retval, id] = aclog.invoke('Clipping-v1.0/analyzer', params, id, @execute);
end

function r = execute(p)
data = p.data;
clip_value = p.clip_value;
clip_high = p.clip_high;
clip_set = p.clip_set;
if ~ismember(clip_set,0:2), error('Acycle:Clipping:Mode','Expected mode 0, 1 or 2.'); end
%% Copied from mingsongli/acycle@b52ea9f510f3be00bde9a0238b9898a1e2315b74 code/guicode/AC.m:L2378-L2384
                    time = data(:,1);
                    y = data(:,2);
                    
                    if clip_high == 1
                        if clip_set == 0
                            y(y<clip_value) = clip_value;
                            y = y - clip_value;
%% End copied source
%% Copied from mingsongli/acycle@b52ea9f510f3be00bde9a0238b9898a1e2315b74 code/guicode/AC.m:L2386-L2388
                        elseif clip_set ==1
                            time(y<clip_value) = [];
                            y(y<clip_value) = [];
%% End copied source
%% Copied from mingsongli/acycle@b52ea9f510f3be00bde9a0238b9898a1e2315b74 code/guicode/AC.m:L2390-L2391
                        elseif clip_set ==2
                            y(y<clip_value) = clip_value;
%% End copied source
%% Copied from mingsongli/acycle@b52ea9f510f3be00bde9a0238b9898a1e2315b74 code/guicode/AC.m:L2399-L2404
                        end
                        
                    else
                        if clip_set == 0
                            y(y>clip_value) = clip_value;
                            y = y - clip_value;
%% End copied source
%% Copied from mingsongli/acycle@b52ea9f510f3be00bde9a0238b9898a1e2315b74 code/guicode/AC.m:L2406-L2408
                        elseif clip_set ==1
                            time(y>clip_value) = [];
                            y(y>clip_value) = [];
%% End copied source
%% Copied from mingsongli/acycle@b52ea9f510f3be00bde9a0238b9898a1e2315b74 code/guicode/AC.m:L2410-L2411
                        elseif clip_set ==2
                            y(y>clip_value) = clip_value;
%% End copied source
%% Copied from mingsongli/acycle@b52ea9f510f3be00bde9a0238b9898a1e2315b74 code/guicode/AC.m:L2419-L2422
                        end
                    end

                        data1 = [time,y];
%% End copied source
r = struct();
r.data1 = data1;
end
