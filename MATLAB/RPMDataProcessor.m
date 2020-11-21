close all;
clear;

data = readmatrix("20201120 Two consecutive rising edges before permitting polling/20201120_square_15s_w_20ms_polling_delay.csv");
% tachometer_RPM = 5913;
raw_sensor_RPM = data(:,2);
raw_delta_us = data(:,1);
rolling_average_10_RPM = movmean(raw_sensor_RPM,[9 0]);
rolling_average_50_RPM = movmean(raw_sensor_RPM,[49 0]);
rolling_average_100_RPM = movmean(raw_sensor_RPM,[99 0]);

figure;
hold on;
plot(raw_delta_us);
hold off;

figure;
hold on;
rows_to_delete = raw_delta_us > 10000 | raw_delta_us < 500;
filtered_delta_us = raw_delta_us;
filtered_delta_us(rows_to_delete) = [];
plot(filtered_delta_us)
hold off;

figure;
hold on;
plot(raw_sensor_RPM);
plot(rolling_average_10_RPM);
plot(rolling_average_50_RPM);
plot(rolling_average_100_RPM);
% plot(tachometer_RPM*ones(10235,1));
title("Measured RPM across samples, 50% power, no propeller attached");
legend("Unfiltered RPM", "10-sample trailing average RPM", "50-sample trailing average", "100-sample trailing average", "Tachometer measurement");
grid on;
xlabel("Sample");
ylabel("RPM");
hold off;

figure;
hold on;
rows_to_delete = raw_sensor_RPM > 15000 | raw_sensor_RPM < 1000;
filtered_sensor_RPM = raw_sensor_RPM;
filtered_sensor_RPM(rows_to_delete) = [];
rolling_average_10_RPM = movmean(filtered_sensor_RPM,[9 0]);
rolling_average_50_RPM = movmean(filtered_sensor_RPM,[49 0]);
rolling_average_100_RPM = movmean(filtered_sensor_RPM,[99 0]);
plot(filtered_sensor_RPM);
plot(rolling_average_10_RPM);
plot(rolling_average_50_RPM);
plot(rolling_average_100_RPM);
hold off;