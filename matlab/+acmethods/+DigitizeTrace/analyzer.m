function [retval, id] = analyzer(params, id)
% DigitizeTrace.analyzer parameters: image seeds srsh shreshn engine.
% Source: https://github.com/mingsongli/acycle/blob/b52ea9f510f3be00bde9a0238b9898a1e2315b74/code/guicode/DataExtractML.m#L755
% Source: https://github.com/mingsongli/acycle/blob/b52ea9f510f3be00bde9a0238b9898a1e2315b74/code/corrcoef/ecocotrackn.m#L1
if nargin < 2, id = []; end
[retval, id] = aclog.invoke('DigitizeTrace-v1.0/analyzer', params, id, @execute);
end

function [r, status] = execute(p)
srsh = p.srsh;
shreshn = p.shreshn;
I=p.image;
if ndims(I)==3
%% Copied from mingsongli/acycle@b52ea9f510f3be00bde9a0238b9898a1e2315b74 code/guicode/DataExtractML.m:L760-L763
    R = I(:,:,1);
    G = I(:,:,2);
    B = I(:,:,3);
    Ig = 0.2989 * R + 0.5870 * G + 0.1140 * B;
%% End copied source
else
    Ig=I;
end
%% Copied from mingsongli/acycle@b52ea9f510f3be00bde9a0238b9898a1e2315b74 code/guicode/DataExtractML.m:L769-L774
    Ig01 = Ig; 
    Ig01(Ig01<shreshn)  = 0; % data
    Ig01(Ig01>=shreshn) = 255; % white bg
    Ig01(Ig01==0)  = 1; % data
    Ig01(Ig01==255)  = 0; % bg
    Ig01 = double(Ig01);
%% End copied source
seeds=round(p.seeds);
validateattributes(seeds,{'numeric'},{'2d','ncols',2,'finite'});
validateattributes(srsh,{'numeric'},{'scalar','positive','finite'});
switch p.engine
    case 'trackline'
%% Copied from mingsongli/acycle@b52ea9f510f3be00bde9a0238b9898a1e2315b74 code/guicode/DataExtractML.m:L781-L781
    [Y] = getPKS(Ig01,2);
%% End copied source
        segments=cell(size(seeds,1),1);
        for i=1:numel(segments)
            x=seeds(i,1); y=seeds(i,2);
%% Copied from mingsongli/acycle@b52ea9f510f3be00bde9a0238b9898a1e2315b74 code/guicode/DataExtractML.m:L810-L810
            [YYY] = trackline(Y',round(x),round(y),srsh);
%% End copied source
            segments{i}=YYY;
        end
    case 'ecocotrackn'
        % The missing digitizer peak map is replaced by centers of vertical ink runs.
        % Trace from each seed in both directions using Li's existing COCO ridge tracker.
        [height,width]=size(Ig01);
        edges=diff([zeros(1,width); Ig01; zeros(1,width)]);
        candidates=cell(1,width);
        for col=1:width
            candidates{col}=(find(edges(:,col)>0)+find(edges(:,col)<0)-1)/2;
        end
        maxCount=max(cellfun(@numel,candidates));
        map=inf(max(1,maxCount),width);
        for col=1:width
            values=candidates{col};
            map(1:numel(values),col)=values;
        end
        segments=cell(size(seeds,1),1);
        for i=1:numel(segments)
            x=seeds(i,1); y=seeds(i,2);
            if x<1 || x>width || y<1 || y>height
                error('Acycle:Digitize:Seed','Seed lies outside the image.');
            end
            if all(abs(map(:,x)-y)>=srsh), segments{i}=zeros(0,2); continue; end
            [left,~]=ecocotrackn(map(:,x:-1:1),srsh,y,[],0);
            [right,~]=ecocotrackn(map(:,x:end),srsh,y,[],0);
            trace=[left(end:-1:2),right]; cols=find(isfinite(trace));
            segments{i}=[cols(:),reshape(trace(cols),[],1)];
        end
    otherwise
        error('Acycle:Digitize:Engine','Unknown digitizer engine.');
end
r=struct('segments',{segments},'pixels',vertcat(segments{:}),'engine',p.engine);
status='done';
if isempty(r.pixels), r=[]; status='cancelled';
elseif any(cellfun(@isempty,segments)), status='incomplete'; end
end
