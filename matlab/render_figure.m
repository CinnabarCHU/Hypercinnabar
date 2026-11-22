function render_figure(id,profile,root,outdir)
% Figures are rebuilt as native, editable MATLAB axes. IDs distinguish the
% two figures numbered 2. Physical widths refer to the saved page.
if ~exist(outdir,'dir'), mkdir(outdir); end
set(groot,'defaultFigureVisible','off','defaultAxesFontName','Times New Roman', ...
 'defaultTextInterpreter','none','defaultLegendInterpreter','none','defaultTextFontName','Times New Roman','defaultAxesFontSize',9,'defaultTextFontSize',9);
isSupp=startsWith(id,'S');
sizeMM=struct('F1',[173 134],'F2h',[190 71],'F2iso',[177 203],'F3',[178 90], ...
 'F4',[184 162],'F5',[190 102],'F6',[180 165],'F7',[190 132],'F8',[170 185], ...
 'S1',[162 211],'S2',[162 166],'S3',[162 221],'S4',[162 194],'S5',[162 173], ...
 'S6',[162 210],'S7',[162 214]);
mm=sizeMM.(id); fig=figure('Color','w','Units','centimeters','Position',[1 1 mm/10], ...
    'PaperUnits','centimeters','PaperSize',mm/10,'PaperPosition',[0 0 mm/10], ...
    'PaperPositionMode','manual','Renderer','painters','Name',[id ' - ' profile],'NumberTitle','off');
closeFigure=onCleanup(@()close(fig)); fig.InvertHardcopy='off';
if isSupp, set(fig,'DefaultAxesFontSize',8,'DefaultTextFontSize',8); end
c=[.53 .68 .20;.11 .27 .54;.78 .17 .16;.93 .52 .14];
prefix=regexprep(profile,'-(caption|negative|native|bulk)$','');
if ismember(id,{'F1','F2h','F8','S6'}), orbit=load(fullfile(root,'fields','orbits.mat')); end
if ismember(id,{'F2iso','F3','F4','F5','F6','S1','S2','S3','S4','S5'})
    n=4; if ismember(id,{'F3','F6','S1','S2','S5'}), n=2; end
    q=cell(1,n);
    for k=1:n, q{k}=load(fullfile(root,'fields',prefix,sprintf('series%d.mat',k))); end
end
switch id
case 'F1'
    for j=1:3
        ax=panel([.12 .694-(j-1)*.301 .852 .209]); draworbit(ax,orbit,j);
        if j==1, orbit_key(ax,[.535 .966]); end
    end
case 'F2h'
    for j=1:2
        ax=panel([.105+(j-1)*.490 .218 .382 .625]); horbit(ax,orbit.(['h' num2str(j)]),j,true);
        letter(ax,char(96+j));
    end
case 'F2iso'
    bottoms=[.817 .686 .505 .345 .215 .069]; heights=[.12 .088 .126 .12 .088 .100];
    for j=1:6
        k=1+(j>3); a=q{k}; ax=panel([.154 bottoms(j) .814 heights(j)]);
        typ=mod(j-1,3); t=a.t/1000;
        if typ==0
            plot(ax,a.pda(:,1)/1000,a.pda(:,2),'Color',c(k,:),'LineWidth',1.15); ylim(ax,[-.04 .72]);
            pda_arcs(ax,k,.49,.065); ylabel(ax,{'Short eccentricity','band power'});
        elseif typ==1
            h(1)=plot(ax,t,a.y,'Color',light(c(k,:),.52),'LineWidth',.35); hold(ax,'on');
            h(2)=plot(ax,t,2*a.g(:,1),'Color',c(k,:),'LineWidth',1.5);
            h(3)=plot(ax,t,2*a.g(:,2),'Color',light(c(k,:),.32),'LineWidth',.9);
            ylim(ax,[-1.6 .8]); ylabel(ax,iso(k));
            if j==2
                key(ax,h,{'Residual','Long band ($2\times$)','Short band ($2\times$)'},[.54 .980],3);
            end
        else
            plot(ax,a.raw(:,1)/1000,a.raw(:,2),'Color',light(c(k,:),.45),'LineWidth',.35); hold(ax,'on');
            plot(ax,t,a.trend,'Color',c(k,:),'LineWidth',1.15); ylim(ax,[-2.5 2.5]); ylabel(ax,iso_unit(k));
            if k==2, set(ax,'YDir','reverse'); end
        end
        xlim(ax,[39.5 65.5]); set(ax,'XTick',40:2:64); grid(ax,'on');
        if typ<2, ax.XTickLabel=[]; end
        if j==6, xlabel(ax,'Age (Ma)'); end
        letter(ax,char(103-j));
    end
case {'F3','S2'}
    for k=1:2
        if isSupp, pos=[.136 .582-(k-1)*.481 .823 .329]; center=[.546 .512];
        else, pos=[.095+(k-1)*.495 .198 .386 .596]; center=[.534 .958]; end
        ax=panel(pos); h=spectrum(ax,q{k},k,isSupp); letter(ax,char(96+k));
        if k==1 && ~isempty(h)
            labels={'$5\%$ FDR','$99\%\,\chi^{2}$','$95\%\,\chi^{2}$','SWA background','Power'};
            if isSupp, labels{end+1}='Exceeds both thresholds'; end
            key(ax,h,labels,center,3+2*~isSupp);
        end
    end
case 'F4'
    bottoms=[.788 .612 .372 .195];
    for j=1:4
        k=5-j; ax=panel([.164 bottoms(j) .805 .135]); hold(ax,'on'); letter(ax,char(96+k));
        windows=[41 42.3;43.4 44.4;45.6 47.5;52.2 53;53.55 54.15;55.1 55.85;56.55 57.5;58.2 59;59.8 60.55;61.5 62.3;63.2 64.1];
        for w=windows', patch(ax,w([1 2 2 1]),[0 0 1.5 1.5],[.99 .964 .89],'EdgeColor','none'); end
        a=q{k}; if ~isfield(a,'pda'), statusline(ax,'Window count exceeds revision limit');continue,end
        plot(ax,a.pda(:,1)/1000,a.pda(:,2),'Color',c(k,:),'LineWidth',1.25);
        yl=[.55 .55 1 1]; ylim(ax,[0 yl(k)*1.30]); xlim(ax,[40 65]);
        pda_arcs(ax,k,yl(k)*.91,yl(k)*.10); ax.XTick=[]; ylabel(ax,shortname(k));
    end
    note(.30,.558,'$\approx 2.4\,\mathrm{Myr}$');
    note(.56,.558,'$\leftarrow$ Resonance transition $\rightarrow$');
    note(.82,.558,'$\approx 1.2\,\mathrm{Myr}$');
    stages(panel([.164 .092 .805 .064]),40,65);
case {'F5','S4'}
    for k=1:4
        if isSupp
            col=mod(k-1,2); x=.101+col*.483; y=.588-floor((k-1)/2)*.482;
            ht=.321; sw=.072; gap=.012; mw=.274; showAge=col==0;
        else
            x=.084+(k-1)*.234; y=.157; ht=.681; sw=.039; gap=.008; mw=.169; showAge=k==1;
        end
        side=panel([x y sw ht]); map=panel([x+sw+gap y mw ht]); s=evo_field(q{k},profile);
        evo_panel(map,side,q{k},s,k,c(k,:),~isSupp,endsWith(profile,'-native'),showAge);
        letter(side,char(96+k));
        if isSupp, xlabel(map,'Frequency (cycles/Myr)'); end
    end
    if ~isSupp, note(.545,.044,'Frequency (cycles/Myr)'); end
case {'F6','S5'}
    for k=1:2
        y=.579-(k-1)*.482;
        ax=panel([.129 y .593 .344]); axg=panel([.758 y .113 .344]);
        isotope_wave(ax,axg,q{k}.cwt,k,c(k,:),isSupp); letter(ax,char(96+k));
    end
case {'F7','S7'}
    for k=1:5
        if isSupp
            x=.14; y=.824-(k-1)*.186; ww=.735; hh=.111;
        else
            col=mod(k-1,2); x=.096+col*.478; y=.720-floor((k-1)/2)*.318; ww=.341; hh=.194;
        end
        ax=panel([x y ww hh]); a=load(fullfile(root,'fields','wtc',sprintf('pair%d.mat',k)));
        coherent(ax,a,k,endsWith(profile,'negative'),~isSupp); letter(ax,char(96+k));
        if (isSupp && k<5) || (~isSupp && k<4), xlabel(ax,''); end
        if ~isSupp && mod(k,2)==0, ylabel(ax,''); end
    end
    if ~isSupp
        ax=panel([.578 .067 .362 .218]); legendphase(ax); letter(ax,'f');
    end
case 'F8'
    l=load(fullfile(root,'data','figure8_sources.mat')); l.kt_primary=readmatrix(fullfile(root,'data','kt2014_panel1c.csv')); if endsWith(profile,'records')
        l.raw_kt=readmatrix(fullfile(root,'data','kt2014_observations.csv'));
        l.raw_pac=readmatrix(fullfile(root,'data','w2018_1209.csv'));
        l.raw_atl=readmatrix(fullfile(root,'data','w2017_atlantic.csv'));
    end
    composite8(orbit,l,endsWith(profile,'bulk'));
case 'S1'
    for k=1:2
        a=q{k}; x=.118+(k-1)*.494; width=.343;
        ax=panel([x .727 width .185]); ax.Tag=sprintf('sampling-%d',k);
        dt=diff(a.raw(:,1)); histogram(ax,dt,'BinEdges',[0:.5:10 12 15 20 30 50 100 250], ...
            'FaceColor',c(k,:),'EdgeColor','none'); xlim(ax,[0 25]);
        xline(ax,median(dt),'--','Color',[.15 .15 .15],'LineWidth',.9);
        xlabel(ax,'Sampling interval (kyr)'); ylabel(ax,'Count');
        title(ax,[iso(k) ' sampling']); letter(ax,char(96+k));
        ax=panel([x .412 width .182]); ax.Tag=sprintf('trend-%d',k);
        h(1)=plot(ax,a.raw(:,1)/1000,a.raw(:,2),'Color',light(c(k,:),.51),'LineWidth',.5); hold(ax,'on');
        h(2)=plot(ax,a.t/1000,a.trend,'Color',c(k,:),'LineWidth',1.3); xlim(ax,[40 65]);
        xlabel(ax,'Age (Ma)'); ylabel(ax,iso_unit(k)); title(ax,'4 Myr LOWESS'); letter(ax,char(98+k));
        key(ax,h,{'Observations','LOWESS trend'},[x+width/2 .652],2);
        ax=panel([x .096 width .185]); ax.Tag=sprintf('petm-%d',k);
        dx=a.t/1000; changed=a.y~=a.residual;
        h(1)=plot(ax,dx,a.residual,'--','Color',[.24 .24 .24],'LineWidth',1.05); hold(ax,'on');
        h(2)=plot(ax,dx,a.y,'Color',c(k,:),'LineWidth',1.18);
        % Mark revised samples, including the start and end of the interval.
        plot(ax,dx(changed),a.y(changed),'.','MarkerSize',3.3,'Color',c(k,:));
        xlim(ax,[55.75 56.012]); ax.XTick=[55.8 55.9 56.0]; ax.XTickLabel={'55.8','55.9','56.0'};
        inView=dx>=55.75 & dx<=56.012; vals=[a.residual(inView);a.y(inView)]; lim=[min(vals) max(vals)];
        ylim(ax,lim+[-1 1]*max(.08,diff(lim)*.09)); xlabel(ax,'Age (Ma)'); ylabel(ax,'Residual (‰)');
        title(ax,sprintf('PETM replacement (%d)',nnz(changed))); letter(ax,char(100+k));
        key(ax,h,{'Before','After'},[x+width/2 .332],2);
    end
case 'S3'
    for k=1:2
        a=q{k}; ax=panel([.160 .831-(k-1)*.133 .804 .084]); hold(ax,'on');
        for j=1:2, h(j)=plot(ax,a.t/1000,a.g(:,j),'Color',light(c(k,:),.32*(j-1)),'LineWidth',1.05,'LineStyle',pick(j,'-','--')); end
        xlim(ax,[40 65]); ylabel(ax,iso(k)); letter(ax,char(96+k)); ax.XTickLabel=[];
        if k==1, key(ax,h,{'Long band','Short band'},[.557 .971],2); end
    end
    for k=1:4
        a=q{k}; ax=panel([.160 .531-(k-1)*.151 .804 .104]); letter(ax,char(98+k));
        if ~isfield(a,'pda'), statusline(ax,'Window count exceeds revision limit'); continue,end
        plot(ax,a.pda(:,1)/1000,a.pda(:,2),'Color',c(k,:)); hold(ax,'on');
        [pk,tx]=findpeaks(a.pda(:,2),a.pda(:,1)/1000,'MinPeakDistance',.9,'MinPeakProminence',.055);
        plot(ax,tx,pk,'.','Color',c(k,:)); 
        for j=2:numel(tx)
            text(ax,mean(tx(j-1:j)),max(pk)*1.17,sprintf('%.1f',diff(tx(j-1:j))), ...
                'FontSize',6.3,'HorizontalAlignment','center','Tag','interval');
        end
        xlim(ax,[40 65]); ylim(ax,[0 max(max(a.pda(:,2))*1.45,eps)]); ylabel(ax,shortname(k));
        if k==4, xlabel(ax,'Age (Ma)'); else, ax.XTickLabel=[]; end
    end
case 'S6'
    for j=1:3
        ax=panel([.148 .826-(j-1)*.158 .810 .102]); draworbit(ax,orbit,j); letter(ax,char(96+j));
        if j==1, orbit_key(ax,[.546 .978]); end
    end
    for j=1:2
        ax=panel([.148 .276-(j-1)*.193 .810 .116]); horbit(ax,orbit.(['h' num2str(j)]),j,false);
        letter(ax,char(99+j));
    end
end
apply_interpreters(fig);
drawnow;
savefig(fig,fullfile(outdir,'plot.fig'),'compact');
print(fig,fullfile(outdir,'plot.svg'),'-dsvg','-painters');
chk=openfig(fullfile(outdir,'plot.fig'),'invisible');
cleanupCheck=onCleanup(@()close(chk));
assert(~isempty(findall(chk,'Type','axes')));
if strcmp(getenv('ACYCLE_LAYOUT_METRICS'),'1'), layout_metrics(chk,id,profile,outdir); end
end

function ax=panel(pos)
ax=axes('Units','normalized','Position',pos,'PositionConstraint','innerposition', ...
    'Box','on','Layer','top','TickDir','out','NextPlot','add','Tag','data-panel');
end
function letter(ax,t)
% Keep the letter at a fixed physical distance from the frame on wide and narrow axes.
f=ancestor(ax,'figure'); p=ax.Position; dims=f.PaperSize*10;
text(ax,-2.6/(dims(1)*p(3)),1+1.5/(dims(2)*p(4)),t,'Units','normalized', ...
    'HorizontalAlignment','right','VerticalAlignment','bottom','FontName','Arial', ...
    'FontWeight','bold','FontSize',9,'Clipping','off','Tag','panel-letter');
end
function note(x,y,txt)
f=gcf; obj=annotation(f,'textbox',[x-.10 y-.02 .20 .04],'String',txt, ...
    'FitBoxToText','on','LineStyle','none','Margin',0,'FontSize',8,'Tag','band-note', ...
    'HorizontalAlignment','center','VerticalAlignment','middle','Interpreter',interpreter(txt));
drawnow; p=obj.Position; p(1:2)=[x-p(3)/2 y-p(4)/2]; obj.Position=p;
end
function statusline(ax,txt)
axis(ax,'off'); text(ax,.5,.5,txt,'Units','normalized','HorizontalAlignment','center','FontSize',8,'Tag','status');
end
function lg=key(ax,lines,labels,center,ncols)
lg=legend(ax,lines,labels,'NumColumns',ncols,'Orientation','horizontal','Box','off', ...
    'AutoUpdate','off','Interpreter',interpreter(labels),'FontSize',7,'Tag','plot-key');
lg.ItemTokenSize=[12 8]; lg.Units='normalized'; drawnow;
p=lg.Position; lg.Position=[center(1)-p(3)/2 center(2)-p(4)/2 p(3) p(4)];
end
function t=iso(k)
labels={'$\delta^{13}\mathrm{C}$','$\delta^{18}\mathrm{O}$'}; t=labels{k};
end
function t=iso_unit(k)
t=iso(k); t=[t(1:end-1) '\;({}^{0}\!/\!_{00})$'];
end
function t=name(k)
if k<=2, t=['Benthic ' iso(k)]; else, t=pick(k-2,'ZB18a eccentricity','La10c eccentricity'); end
end
function t=shortname(k)
if k<=2, t=iso(k); else, t=pick(k-2,'ZB18a','La10c'); end
end
function value=interpreter(str)
if any(contains(string(str),'$'),'all'), value='latex'; else, value='none'; end
end
function apply_interpreters(fig)
for h=reshape(findall(fig,'Type','text'),1,[])
    h.Interpreter=interpreter(h.String);
end
end
function a=light(c,x),a=c*(1-x)+x;end
function v=pick(j,a,b),if j==1,v=a;else,v=b;end,end

function draworbit(ax,o,j)
names={'La10a','La10b','La10c','ZB18a','ZB20a','ZB20b'};
col=[.835 .369 0;.902 .624 0;.533 .133 .333;0 .447 .698;.337 .706 .914;0 .62 .451]; left=-45-5*j;hold(ax,'on');
for i=1:6,z=o.(names{i});x=-z(:,1);use=x>=left&x<=left+5;plot(ax,x(use),z(use,2),'Color',light(col(i,:),.4),'LineWidth',.4);end
h=gobjects(1,6);
for i=1:6,z=o.(names{i});x=-z(:,1);use=x>=left&x<=left+5;h(i)=plot(ax,x(use),z(use,3),'Color',col(i,:),'LineWidth',1.65);end
xlim(ax,[left left+5]);ylim(ax,[0 .08]);ax.YTick=0:.02:.08;ylabel(ax,'$e_{\oplus}$');if j==3,xlabel(ax,'Time (Myr)');end
setappdata(ax,'orbital_lines',h);
end
function orbit_key(ax,pt)
names={'La10a','La10b','La10c','ZB18a','ZB20a','ZB20b'};
h=getappdata(ax,'orbital_lines'); idx=[4 1 5 2 6 3]; key(ax,h(idx),names(idx),pt,6);
end

function horbit(ax,d,k,annotated)
v=max(-8,min(6,floor(double(d.logpower))));imagesc(ax,d.t,log2(d.scale),v);set(ax,'YDir','reverse');hold(ax,'on');colormap(ax,jet(15));clim(ax,[-8 6]);
ticks=[73 174 232 304];set(ax,'YTick',log2(ticks),'YTickLabel',string(ticks));xlim(ax,[38 67]);xlabel(ax,'Age (Ma)');ylabel(ax,'Period (kyr)');
titles={'ZB18a','La10c'};title(ax,[titles{k} '   $h=e\sin(\varpi)$']);
ff=4*pi/(6+sqrt(38));plot(ax,d.t,log2(max(d.coi,eps)),'k','LineWidth',.6);
if annotated
    for m=1:size(d.arc_age,1),a=d.arc_age(m,:);if mean(a)>48.3 && mean(a)<52,continue,end;plot(ax,a,log2(d.arc_period(m,:)/ff),'k','LineWidth',1.2);end
    text(ax,42.8,log2(61),'$\approx 2.4$','FontWeight','bold');text(ax,55.1,log2(61),'$\approx 1.5$','FontWeight','bold');
    if k==2,text(ax,58.3,log2(61),'$\approx 2.0$','FontWeight','bold');end
    for j=1:4,gt={'$g_{3},\,g_{4}$','$g_{2}$','$g_{1}$','$g_{5}$'};text(ax,38.25,log2(ticks(j)),gt{j},'Color','w','FontSize',7);end
end
ylim(ax,log2([d.scale(1) d.scale(end)]));
end
function h=spectrum(ax,z,k,supp)
h=gobjects(0);title(ax,name(k));
if ~isfield(z,'sp')
    statusline(ax,{'SWA/FDR unavailable','in this revision'});return
end
s=z.sp; s=s(s(:,1)<=.005,:); hold(ax,'on');
h(1)=plot(ax,s(:,1)*1000,s(:,6),'--','Color',[.78 .03 .08],'LineWidth',1.25);
h(2)=plot(ax,s(:,1)*1000,s(:,5),'-.','Color',[.04 .39 .61],'LineWidth',.85);
h(3)=plot(ax,s(:,1)*1000,s(:,4),'--','Color',[.88 .39 .11],'LineWidth',.85);
h(4)=plot(ax,s(:,1)*1000,s(:,3),'Color',[.30 .30 .30],'LineWidth',.8);
h(5)=plot(ax,s(:,1)*1000,s(:,2),'k','LineWidth',.8);
if supp
    use=islocalmax(s(:,2))&s(:,2)>s(:,4)&s(:,2)>s(:,6);
    h(6)=plot(ax,s(use,1)*1000,s(use,2),'o','MarkerSize',3,'Color',[.5 .1 .1]);
end
xlim(ax,[0 5]); ylim(ax,[0 max(max(s(:,2))*1.40,1e-10)]);
ylabel(ax,'Power'); xlabel(ax,'Frequency (cycles/Myr)');
bands=[.00038 .00055;.000665 .000785;.00235 .00258];
if k==2, bands(1:2,:)=[.000385 .000605;.0007 .00091]; end
labelx=[.32 1.26 2.53]; labely=[.90 .75 .72]*ax.YLim(2);
for i=1:3
    ix=find(s(:,1)>=bands(i,1)&s(:,1)<=bands(i,2)); if isempty(ix),continue,end
    if ~supp && k==2 && i==1
        candidates=ix(islocalmax(s(ix,2))); [~,near]=min(abs(1./s(candidates,1)-2200));
        if ~isempty(near), ix=candidates(near); end
    end
    [v,ii]=max(s(ix,2)); freq=s(ix(ii),1)*1000; period=1000/freq;
    if supp, tx=sprintf('%.0f kyr',period);
    else, tags={'$\approx 2.2\,\mathrm{Myr}$',pick(k,'$\approx 1.4\,\mathrm{Myr}$','$\approx 1.3\,\mathrm{Myr}$'),'405 kyr'}; tx=tags{i}; end
    xx=labelx(i); yy=max(labely(i),v+.11*ax.YLim(2));
    line(ax,[freq xx],[v yy-.035*ax.YLim(2)],'Color',[.34 .34 .34],'LineWidth',.5,'HandleVisibility','off');
    text(ax,xx,yy,tx,'FontSize',6.6,'HorizontalAlignment','center','VerticalAlignment','bottom','Tag','peak-label');
end
end

function pda_arcs(ax,k,h,dy)
% Coordinates of the interpreted intervals are artwork annotations in the source.
ends1={ [40.7 43.1 45.1 47.1],[51.9 53.2 54.5 55.8 57.8 59.0 61.0 62.4 64.4]};
ends2={ [40.45 42.85 44.85 46.85],[52.0 53.3 54.6 55.9 57.1 58.3 59.5 61.5 62.8 64.8]};
ends3={ [40.4 43.1 45.1 47.8],[51.9 53.2 54.5 55.8 57.4 59.0 60.9 62.3 64.3]};
ends4={ [40.4 43.1 45.1 47.8],[51.9 53.2 54.5 55.8 57.8 59.8 61.8 63.2 64.6]};
all={ends1,ends2,ends3,ends4};arcs=all{k};hold(ax,'on');theta=linspace(0,pi,30);
for set=1:2, e=arcs{set};for j=1:numel(e)-1
 x=linspace(e(j),e(j+1),30);plot(ax,x,h+dy*sin(theta),'--','Color',[.35 .35 .35],'LineWidth',.65);
 if ~(k>=3&&set==1&&j==3),label=e(j+1)-e(j);if k>=3&&set==1&&j==1,label=2.4;end
 text(ax,mean(x),h+dy,sprintf('%.1f',label),'HorizontalAlignment','center','VerticalAlignment','bottom','FontSize',6.2,'Tag','interval');end
end,end
end
function stages(ax,lo,hi)
hold(ax,'on'); ages=[40 41.2 47.6 56 59.5 62.05 65]; labels={'Ba.','Lutetian','Ypresian','Th.','Se.','Da.'};
for k=1:6,rectangle(ax,'Position',[ages(k) .5 diff(ages(k:k+1)) .5]);text(ax,mean(ages(k:k+1)),.75,labels{k},'HorizontalAlignment','center','FontSize',8);end
for r=[40 56;56 65]',rectangle(ax,'Position',[r(1) 0 diff(r) .5]);end
text(ax,48,.25,'Eocene','HorizontalAlignment','center');text(ax,60.5,.25,'Paleocene','HorizontalAlignment','center');
xlim(ax,[lo hi]);ylim(ax,[0 1]);ax.YTick=[];xlabel(ax,'Age (Ma)');
end
function s=evo_field(q,profile)
j=1;if contains(profile,'caption') && numel(q.evo)>1,j=2;end;s=q.evo(j);
end
function evo_panel(ax,side,q,s,k,col,mark,pure,showAge)
if pure&&isfield(q,'native_lowpass_error')
    axis(side,'off');statusline(ax,{'$f_{\mathrm{low}}=0$','unsupported'});title(ax,shortname(k));return
end
plot(side,s.tan,q.t/1000,'Color',col,'LineWidth',.7);ylim(side,[40 65]);set(side,'YDir','reverse');side.XTick=[]; if showAge, ylabel(side,'Age (Ma)'); else, side.YTickLabel=[]; end
imagesc(ax,s.f*1000,s.age/1000,s.amp);set(ax,'YDir','reverse');colormap(ax,parula(128));clim(ax,[0 1]);ylim(ax,[40 65]);xlim(ax,[0 1.8]);
ax.YTickLabel=[]; ax.XTick=[0 .5 1 1.5]; title(ax,shortname(k));
if mark
    hold(ax,'on');yy=46.6+.2*(k>2);
    for y=[yy 51.6],yline(ax,y,'w--','LineWidth',1);text(ax,1.69,y-.42,sprintf('%.1f Ma',y),'HorizontalAlignment','right','VerticalAlignment','bottom','Color','w','FontSize',6,'Tag','age-line-label');end
    x0=[.74 .70 .73 .80];x1=[.42 .64 .51 .55];quiver(ax,x0(k),51.35,x1(k)-x0(k),yy-51.1,0,'Color',[.8 .15 .12],'MaxHeadSize',.45,'LineWidth',1);
end
end
function isotope_wave(ax,axg,w,k,col,supp)
v=double(w.color);y=log2(w.period);x=w.t/1000;
% The main graphic has a normalized colour bar. The two linear transforms
% of GUI log2 power are calibrated to the colour-bar positions in its artwork.
z=log2(max(v,realmin));
if supp
    imagesc(ax,x,y,z);clim(ax,[-16 0]);
else
    offset=[.97887 .96468];slope=[.018870 .024777];
    u=max(0,min(1,offset(k)+slope(k)*z));cm=parula(256);
    idx=1+round(255*u);rgb=reshape(cm(idx(:),:),[size(u) 3]);
    exterior=w.period(:)>w.coi(:)';rgb=rgb.*(1-.33*exterior)+.33*exterior;
    image(ax,[x(1) x(end)],[y(1) y(end)],rgb);clim(ax,[0 1]);
end
set(ax,'YDir','normal');colormap(ax,parula(256));hold(ax,'on');
contour(ax,x,y,double(w.signif),[1 1],'k','LineWidth',.8);
plot(ax,x,log2(max(w.coi,eps)),'Color',[.22 .22 .22],'LineWidth',.75);
yt=[95 125 405 1200 2400];set(ax,'YTick',log2(yt),'YTickLabel',string(yt),'YLim',log2([64 5000]),'XLim',[40 65]);
xlabel(ax,'Age (Ma)');ylabel(ax,'Period (kyr)');title(ax,name(k));
if supp,fac=1;else,fac=pick(k,1e4,1e5);end
plot(axg,fac*w.global_power,y,'Color',col,'LineWidth',1);axg.YLim=ax.YLim;axg.YTick=[];
if supp,xlabel(axg,'Global power');else,xlabel(axg,pick(k,'Power ($10^{-4}$)','Power ($10^{-5}$)'));end
if ~supp
 for p=[2200,pick(k,1400,1300)]
     yline(ax,log2(p),'--','Color',[.52 .52 .52]);
     text(ax,41.1,log2(p),sprintf('$\\approx %.1f\\,\\mathrm{Myr}$',p/1000),'FontSize',7, ...
         'VerticalAlignment','middle','BackgroundColor','w','Margin',.65,'Tag','wave-period');
 end
end
pos=ax.Position; cb=colorbar(ax,'Position',[.912 pos(2) .014 pos(4)]); ax.Position=pos;cb.FontSize=6;if supp,cb.Ticks=-16:4:0;else,cb.Ticks=0:.2:1;end
end
function coherent(ax,a,k,neg,compact)
x=a.t(:)'/1000;y=log2(a.period(:));v=double(a.r2); cmap=parula(128);
idx=1+round(min(1,max(0,v))*127); rgb=reshape(cmap(idx(:),:),[size(v) 3]);
outside=a.period(:)>a.coi(:)'; rgb=rgb.*(1-.48*outside)+.48*outside;
image(ax,[x(1) x(end)],[y(1) y(end)],rgb);hold(ax,'on');ax.YDir='reverse';colormap(ax,cmap);clim(ax,[0 1]);
contour(ax,x,y,double(a.sig),[1 1],'k','LineWidth',.85);plot(ax,x,log2(max(a.coi,eps)),'Color',[.27 .27 .27],'LineWidth',.6);
theta=a.phase;if neg&&k<5,theta=theta+pi;end
[xx,yy]=meshgrid(a.arrow_age/1000,log2(a.arrow_period));
% Positive mathematical phase points toward greater period on these reversed axes,
% giving the same downward direction as Grinsted phaseplot.
width=diff([40 65]);height=log2(5000/64);pos=ax.Position;fpos=gcf().Position;
u=.0033*width*cos(theta); v=.0033*height*pos(3)*fpos(3)/(pos(4)*fpos(4))*sin(theta);
% Draw heads in normalized screen coordinates, including reversed period axis.
thin=1;if ~compact,thin=2;end
ii=1:thin:size(xx,2);xx=xx(:,ii);yy=yy(:,ii);u=u(:,ii);v=v(:,ii);
sy=height*pos(3)*fpos(3)/(width*pos(4)*fpos(4));
xx=xx(:)';yy=yy(:)';u=u(:)';v=v(:)';nn=nan(size(xx));
px=[xx-u;xx+u;nn;xx+.25*u+.32*v/sy;xx+u;xx+.25*u-.32*v/sy;nn]; ...
    py=[yy-v;yy+v;nn;yy+.25*v-.32*u*sy;yy+v;yy+.25*v+.32*u*sy;nn];
line(ax,px(:),py(:),'Color',[.16 .22 .20],'LineWidth',.32);
xlim(ax,[40 65]);ylim(ax,log2([64 5000]));yt=[128 256 512 1024 2048 4096];ax.YTick=log2(yt);ax.YTickLabel=string(yt);
xlabel(ax,'Age (Ma)');ylabel(ax,'Period (kyr)');n={['ZB18a vs ' iso(1)],['La10c vs ' iso(1)],['ZB18a vs ' iso(2)], ...
    ['La10c vs ' iso(2)],[iso(1) ' vs ' iso(2)]};
title(ax,n{k}); cb=colorbar(ax,'Position',[pos(1)+pos(3)+.009 pos(2) .008 pos(4)]);
ax.Position=pos; cb.FontSize=6; cb.Ticks=[0 .5 1];
end
function legendphase(ax)
axis(ax,'off'); xlim(ax,[0 1]); ylim(ax,[0 1]); hold(ax,'on');
for j=1:2
    x=.22+(j-1)*.56; y=.50;
    for d=[-1 0;1 0;0 -1;0 1]'
        quiver(ax,x,y,.112*d(1),.21*d(2),0,'k','LineWidth',.9,'MaxHeadSize',.55);
    end
    text(ax,x,.81,pick(j,[iso(2) ' leads'],'Isotope leads'),'HorizontalAlignment','center','FontSize',7,'Tag','phase-key');
    text(ax,x,.18,pick(j,[iso(1) ' leads'],'Eccentricity leads'),'HorizontalAlignment','center','FontSize',7,'Tag','phase-key');
    text(ax,x+.122,y,'$0^{\circ}$','FontSize',6.5,'Tag','phase-key');
    text(ax,x-.122,y,'$180^{\circ}$','FontSize',6.5,'HorizontalAlignment','right','Tag','phase-key');
end
end

function composite8(o,l,bulk)
ax=panel([.090 .745 .784 .155]);hold(ax,'on');names={'La2004','La10a','La10b','La10c','La10d','ZB18a'};
cols=[.18 .18 .18;.85 .17 .18;.2 .32 .83;.16 .7 .2;.1 .78 .82;.84 .02 .78];
for j=1:6,d=o.(names{j});h(j)=plot(ax,d(:,1),d(:,4),'Color',cols(j,:),'LineWidth',.65+1.65*(j==6));end
xlim(ax,[42 60]);set(ax,'XAxisLocation','top','YAxisLocation','right');xlabel(ax,'Age (Ma)');ylabel(ax,'Eccentricity');key(ax,h,names,[.495 .716],6);letter(ax,'a');
ax=panel([.090 .488 .784 .193]);b=o.h8;
% h8 is uniformly spaced in log2(period); interpolate onto the displayed
% linear period axis to reproduce the 20, 40, 60, 80, 100 kyr scale.
pp=linspace(16,108,160);v=interp1(b.period,double(b.logpower),pp);imagesc(ax,b.t,pp,max(-8,min(6,floor(v))));colormap(ax,jet(15));clim(ax,[-8 6]);
xlim(ax,[42 60]);ylim(ax,[16 108]);ax.YDir='reverse';ax.YAxisLocation='right';ax.XTick=[];ylabel(ax,'Period (kyr)');hold(ax,'on');b=o.h1;
for j=1:size(b.arc_age,1),t=b.arc_age(j,:);if mean(t)>48.2&&mean(t)<52.4,continue,end;plot(ax,t,b.arc_period(j,:),'k','LineWidth',1.25);end
text(ax,43,58,'$\approx 2.4\,\mathrm{Myr}$','FontWeight','bold');text(ax,53.1,58,'$\approx 1.5\,\mathrm{Myr}$','FontWeight','bold');letter(ax,'b');
ax=panel([.090+.784/6 .273 .784*5/6 .175]);w=l.westerhold;hold(ax,'on');
zones=[49.17 49.55;51.38 51.97;52.84 53.23;54.26 54.64;55.74 56.14;58.04 58.43;59.38 59.76];
for w0=zones',patch(ax,w0([1 2 2 1]),[-1.3 -1.3 2.85 2.85],[.89 .89 .89],'EdgeColor','none');end
for j=1:2
    ids=[2 3]+2*(j-1);ok=w(:,1)>=45&w(:,1)<=60&all(isfinite(w(:,ids)),2);
    x=w(ok,1);a=w(ok,ids);fill(ax,[x;flipud(x)],[a(:,1);flipud(a(:,2))],pick(j,[1 .78 .78],[.72 .72 .72]),'EdgeColor','none');
end
if isfield(l,'raw_pac')
    % Direct observations from DS01 and an explicit Gaussian display choice.
    records={l.raw_pac,l.raw_atl(:,2:3)};
    tones=[.10 .28 .50;.65 .17 .08];
    for j=1:2
        d=records{j};scatter(ax,d(:,1),d(:,2),1.5,light(tones(j,:),.52),'filled');
        [ages,~,ix]=unique(d(:,1));values=accumarray(ix,d(:,2),[],@mean);
        grid=ceil(ages(1)*500)/500:.002:floor(ages(end)*500)/500;
        v=interp1(ages,values,grid);support=-500:500;kernel=exp(-.5*(support*.002/.20).^2);
        sm=conv(v,kernel,'same')./conv(ones(size(v)),kernel,'same');
        plot(ax,grid,sm,'Color',tones(j,:),'LineWidth',1.15);
    end
end
if ~isfield(l,'raw_pac')
    plot(ax,w(:,1),w(:,6),'r','LineWidth',1.35);plot(ax,w(:,1),w(:,7),'k','LineWidth',1.35);
end
xlim(ax,[45 60]);ylim(ax,[-1.3 2.85]);ax.YAxisLocation='right';ax.XTick=[];ylabel(ax,iso_unit(1));letter(ax,'c');
ax=panel([.090+.784/6 .134 .784*5/6 .109]);if bulk,xy=l.kt1258(:,[1 5]);else,xy=l.kt_primary;end
hold(ax,'on');
for w0=zones',patch(ax,w0([1 2 2 1]),[-1 -1 0 0],[.89 .89 .89],'EdgeColor','none');end
if isfield(l,'raw_kt')
    d=l.raw_kt;cols=[.18 .38 .50;.05 .46 .33;.45 .26 .18];
    for site=1:3
        z=d(d(:,1)==site,:);t=z(:,2);y=z(:,3);
        % Constant inter-site isotope offsets cancel in the detrending.
        avg=arrayfun(@(at)mean(y(abs(t-at)<=1)),t);res=y-avg;
        valid=true(size(t));if site==3,valid=t<55.33|t>55.53;end
        cutoff=mean(res(valid))-std(res(valid)); e=min(res-cutoff,0);
        % Retain all available sites, including their overlap.
        plot(ax,t,e,'Color',cols(site,:),'LineWidth',.6);
    end
else
    plot(ax,xy(:,1),xy(:,2),'Color',[.31 .31 .31],'LineWidth',.75);
end
ylim(ax,[-1 0]);ax.YDir='reverse';xlim(ax,[45 60]);ylabel(ax,iso_unit(1));ax.XTick=[];letter(ax,'d');
ax=panel([.090+.784/6 .106 .784*5/6 .013]);hold(ax,'on');
pol=[46.24 47.85;48.99 49.76;50.81 50.96;51.06 51.79;52.63 52.97;53.08 53.19;53.42 53.94;57.09 57.64;58.93 59.25];
for b=pol',rectangle(ax,'Position',[b(1) 0 diff(b) 1],'FaceColor','k');end
xlim(ax,[45 60]);ylim(ax,[0 1]);ax.XTick=[];ax.YTick=[];
ax=panel([.090+.784/6 .079 .784*5/6 .023]);hold(ax,'on');
for b=[45 56;56 60]',rectangle(ax,'Position',[b(1) 0 diff(b) 1],'FaceColor',[.96 .82 .63]);end
text(ax,50,.5,'Eocene','HorizontalAlignment','center','FontSize',7);text(ax,58,.5,'Paleocene','HorizontalAlignment','center','FontSize',7);
xlim(ax,[45 60]);ylim(ax,[0 1]); ax.YTick=[]; ax.XTick=46:2:60; xlabel(ax,'Age (Ma)');
end
