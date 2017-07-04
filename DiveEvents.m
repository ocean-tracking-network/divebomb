function [Dives] = DiveEvents(data,filename, win,ThSTD, Fs, AvIn, varargin)
%% Function to find high variation events in N-dimensional time series
%   Input:  - TS: Data vector (time and depth)
%           - LWin: Window length in seconds; best result with 20s
%           - ThStd: Standard deviation threshold (in % of average
%               standard deviation of time series); best result with 2.5
%           - Fs = sampling frequency
%           - AvIn = threshold for surface depth; e.g., 3 m

%
%   Output: - Ev: Structure of event information containing cell arrays:
%                   - Ind: Beginning and end indices of the event.
%                   - TS:  ND time series for the event
%                   - STD: Standard deviation of AMag and then all axes
%           - wSTD: Time series of standard deviation
%
%   Optional:   - 'DoPlot', n: Request for plots:   1- depth series with
%                                                       phases identified
%                                                   2- Std plot
%                                                   3- All plots
%                   - NOTE: To save plots, follow DoPlot indicator by 1
%                           (ie 3 -> 31)

%% Analyze inputs and define default values

%Default to no plot request
DoPlot = 0;
DoSave = 0;



[LTS, nD] = size(data(:,2));
time = data(:,1);
TS = data(:,2);

%Read user input
for i = 1:nargin-6
    if ischar(varargin{i})
        if strcmpi(varargin{i},'DoPlot')
            DoPlot = varargin{i+1};
            if sum([11,21,31,41] == DoPlot) == 1
                DoPlot = floor(DoPlot/10);
                DoSave = 1;
            end
        end
    end
end




%% Setup running window to find events

%Make even window lengths
LWin = win*Fs;
if rem(LWin,2) == 1
    LWin = LWin+1;
end


dSub = LWin;

iW = 1:dSub:length(TS)-LWin;
nWin = length(iW);

%----dive ID's----%
DiveID = nan(LTS,1);
ID = nan(nWin,2);

%% Run through windows to find events

%% Run through first window
i = 1;
iSub = iW(i)+(0:LWin);%Indices of the window
wTS = TS(iSub);%Magnitude and time series
wSTD = std(wTS);%Standard deviations
wAV = mean(wTS); %mean of TS

iSub2 = iW(i+1)+(0:LWin);%Indices of the window
wAV2 = mean(TS(iSub2));%mean of following window


if wSTD < ThSTD
    if wAV > AvIn %bottom dive
        DiveID(iSub) = ones(LWin+1,1)*4;
        ID(i,1) = mean(iSub);
        ID(i,2) = 4;
    elseif wAV < AvIn %surface
        DiveID(iSub) = ones(LWin+1,1)*1;
        ID(i,1) = mean(iSub);
        ID(i,2) = 1;
    end

elseif wSTD > ThSTD %ascent or descent phase
    if wAV < wAV2 %descent phase
        DiveID(iSub) = ones(LWin+1,1)*2; %descent
        ID(i,1) = mean(iSub);
        ID(i,2) = 2; %window ID
    elseif wAV > wAV2 %ascent phase
        DiveID(iSub) = ones(LWin+1,1)*3;
        ID(i,1) = mean(iSub);
        ID(i,2) = 3; %window ID
    end
end

for i = 2:nWin
    %Calculate window parameters
    iSub = iW(i)+(0:LWin);%Indices of the window
    wTS = TS(iSub);%Magnitude and time series
    wSTD = std(wTS);%Standard deviations
    wAV = mean(wTS); %mean of TS


    if wSTD < ThSTD
        if wAV > AvIn %bottom dive
            DiveID(iSub) = ones(LWin+1,1)*4;
            ID(i,1) = mean(iSub);
            ID(i,2) = 4;

        elseif wAV < AvIn %surface
            DiveID(iSub) = ones(LWin+1,1)*1;
            ID(i,1) = mean(iSub);
            ID(i,2) = 1;
        end

    elseif wSTD > ThSTD %ascent or descent phase
        if ID(i-1,2) == 2 || ID(i-1,2) == 1 %window before was descent or surface
            DiveID(iSub) = ones(LWin+1,1)*2; %descent
            ID(i,1) = mean(iSub);
            ID(i,2) = 2; %window ID
        elseif ID(i-1,2) == 4 || ID(i-1,2) == 3 %window before was ascent or diving behaviour
            DiveID(iSub) = ones(LWin+1,1)*3;
            ID(i,1) = mean(iSub);
            ID(i,2) = 3; %window ID
        end
    end
    %Display progress
    if rem(i,floor(nWin/10)) == 0
        fprintf('Analyzed %u%% of the time series.\n',round(100*i/nWin))
    end

end


%----plot dive events----%
if DoPlot == 1
    hf(1) = figure;

    bottom = ID(ID(:,2) == 4,1);
    surface = ID(ID(:,2) == 1,1);
    ascent = ID(ID(:,2) == 3,1);
    descent = ID(ID(:,2) == 2,1);

    close all
    plot(time, TS)
    hold on
    plot(time(bottom), TS(bottom), '+g')
    plot(time(descent), TS(descent), '+r')
    plot(time(ascent), TS(ascent), '+y')
    plot(time(surface), TS(surface), '+m')

    title(sprintf('Dive phases found using ThSTD = %2.2f and AvIn = %2.2f with LWin = %2.2f s for %2.2f',ThSTD, AvIn, win, filename))

end



if DoSave == 1
    SaveFigs('hg',['Dive Phases for', filename]);
end


%----allocate Dive number to each dive-----%
DiveNumber = zeros(length(DiveID),1);

bottomdive = find(DiveID == 4);
newdive = diff(bottomdive);
diff2 = find(diff(newdive) > 0);

for i = 1:length(diff2)
    indnew(i) = bottomdive(diff2(i)+2);
end

DiveNumber(1:indnew(1)-1) = ones(length(DiveNumber(1:indnew(1)-1)),1);

for i = 2:length(indnew)
    DiveNumber(indnew(i-1):indnew(i)-1) = ones(length(DiveNumber(indnew(i-1):indnew(i)-1)),1)*i;
end

%--deal with last dive---%
last_dive = find(DiveNumber == 0);
if length(last_dive)>1
    DiveNumber(last_dive) = ones(length(last_dive),1)*(max(DiveNumber)+1);
end

%----now within each dive we can allocate bottom, surfance and
%descent/ascent ID----%
Dives = [time DiveNumber DiveID];




end
