clc 
close all
clear all

% computational tolerance
tolerance = 1e-10;

m_person = 50; % kg (up to 90 kg)
m_bike = 25; % kg
v = 15; % km/h
fs = 2e1; % Hz
t = 4; % s
s_break = 2; % m

max_deg = 320; % deg
bit_width = 8;

break_factor = 40; % N/deg
servo_v = 0.80/60; % s/deg (6V0) 
% servo_v = 0.16/60; % s/deg (7V4) 

%-----------------------------------------------------------------------------%

Ts = 1/fs;
v_ms = v/3.6;

dt_tmp = 2*s_break/v_ms 
dt = dt_tmp - mod(dt_tmp, 2*Ts)
s_break_new = dt*v_ms/2

t0_vec = [0:Ts:t-Ts];
t1_vec = [0:Ts:dt];

% it's a rise constant of the acceleration [m/s^3]
aa = break_factor/(servo_v*(m_person+m_bike))

% calculate, when the acceleration is constant
c = 4*v_ms/-aa+dt^2

if (c < 0)
    error("the break distance is too short for the given servo parameters and person weight")
end

x_tmp = sqrt(c)
x = x_tmp - mod(x_tmp, 2*Ts)

aa_new = v_ms*4/(dt^2-x^2)
servo_v = break_factor/(aa_new*(m_person+m_bike))

a_new = 2*v_ms/(x+dt)
tt = (dt - x)/2

% remove the precision error
tt = round(tt/Ts)*Ts

% linear breaking
% a_decel = ((0 - v_ms)/dt);
% a = ones(1,length(t1_vec))*a_decel;

a = -1*[aa_new*[0:Ts:tt] a_new*ones(1, floor(x/Ts)) aa_new*[tt-Ts:-Ts:0]];

%-----------------------------------------------------------------------------%

v1_vec_tmp = cumtrapz(a)*Ts;

% calculate linear decelaration
v0_vec = v_ms*ones(1, length(t0_vec));
v1_vec = v0_vec(end) + v1_vec_tmp; 
v2_vec = zeros(1, length(t0_vec));

v_vec = [v0_vec v1_vec v2_vec];
t_vec = [0:length(v_vec)-1]*Ts;

s_vec_tmp = cumtrapz(v_vec)*Ts;
s_vec = s_vec_tmp - mod(s_vec_tmp, tolerance);

a_vec = diff(v_vec)./diff(t_vec);
f = abs(a_vec*(m_person+m_bike));
pwm = (f*max_deg)/(power(2,bit_width)*break_factor);

% estimated break distance
s_break = (v_ms*dt)/2

% check the result from the chart
s0 = v_ms*t - mod(v_ms*t, tolerance)
s_break_check = s_vec(end)-s0

% Check of start of the breaking sequence
touch_point_inx = find(s_vec >= (s0 + s_break_new));
s_vec(touch_point_inx)(1)

% here just for debugging purposes
test_v = v_vec(touch_point_inx(1))
test_t = t_vec(touch_point_inx(1))

figure()
subplot(2,1,1)
plot(t_vec, v_vec, "b-o", 'linewidth', 2)
hold on
plot(test_t, test_v, "kx", 'markersize', 20)

settings = [
    "Servo speed: " num2str(servo_v) " [s/deg]\n" ...
    "Decceleration: " num2str(a_new) " [m/s^2]\n" ...
    "weight: " num2str(m_person+m_bike) " [kg]\n" ...
    "Break factor: " num2str(break_factor) " [N/deg]\n" ...
    "Break distance: " num2str(s_break_new) " [m]\n" ...
    "Break time: " num2str(2*tt+x) " [s]\n" ]

text (2*t+dt-4, v_ms-2, settings, 'fontsize', 20);

ylabel("velocity [m/s]")
xlabel("time [s]")
grid on

subplot(2,1,2)
plot(t_vec, s_vec, "b-o", 'linewidth', 2)
ylabel("distance [m]")
xlabel("time [s]")
grid on


figure()
subplot(3,1,1)
plot(t_vec(1:end-1), a_vec, "b-o", 'linewidth', 2)
ylabel("acceleration [m/s^2]")
xlabel("time [s]")
grid on

subplot(3,1,2)
plot(t_vec(1:end-1), f, "b-o", 'linewidth', 2)
ylabel("force [N]")
xlabel("time [s]")
grid on

subplot(3,1,3)
plot(t_vec(1:end-1), pwm, "b-o", 'linewidth', 2)
ylabel("pwm [-]")
xlabel("time [s]")
grid on
