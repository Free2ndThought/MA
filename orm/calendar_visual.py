import calmap
from datetime import datetime

import pandas
import pandas as pd
import matplotlib.pyplot as plt


def create_per_day_plot():
    csv_file_wholeday = 'per_day_report_wholeday_plot.csv'
    values_wholeday = pd.read_csv(csv_file_wholeday, sep=';').squeeze()
    values_wholeday.index = pandas_weekdays
    # create workday series from csv file
    csv_file_workday = 'per_day_report_workday_plot.csv'
    values_workday = pd.read_csv(csv_file_workday, sep=';').squeeze()
    values_workday.index = pandas_weekdays
    # plot the data
    calmap.calendarplot(values_wholeday, cmap='RdYlGn')
    plt.savefig('wholeday_cal.png', dpi=600)
    calmap.calendarplot(values_workday, cmap='coolwarm')
    plt.savefig('workday_cal.png', dpi=600)


def create_per_device_plot():
    csv_file_device = 'per_day_per_sensor_report.csv'
    values_device = pd.read_csv(csv_file_device, sep=';')
    per_sensor_matrizes = {}
    for sensor_id in range(1,38):
        matrix = values_device[values_device['sensorID'] == sensor_id]
        matrix.set_index('day', inplace=True)
        matrix.index = pandas.to_datetime(matrix.index, format='%d-%m-%Y', dayfirst=True)
        per_sensor_matrizes[sensor_id] = matrix[['wholeday_avg', 'workday_avg']]

    per_user_cals(per_sensor_matrizes)

    printer_cals(per_sensor_matrizes)

    per_devicetype_cals(per_sensor_matrizes)


def printer_cals(per_sensor_matrizes):
    printer_sensors_matrix = per_sensor_matrizes[22].add(per_sensor_matrizes[12])
    print('Printer:')
    print(printer_sensors_matrix)
    fig, axes = calmap.calendarplot(printer_sensors_matrix[['wholeday_avg']].squeeze(), cmap='coolwarm')
    plt.savefig('printer_wholeday_cal.png', dpi=600)
    plt.clf()
    plt.close(fig)
    fig, axes = calmap.calendarplot(printer_sensors_matrix[['workday_avg']].squeeze(), cmap='coolwarm')
    plt.savefig('printer_workday_cal.png', dpi=600)
    plt.clf()
    plt.close(fig)


def per_user_cals(per_sensor_matrizes):
    user_to_sensor_map = {1: [per_sensor_matrizes[1], per_sensor_matrizes[2], per_sensor_matrizes[3]],
                          2: [per_sensor_matrizes[4], per_sensor_matrizes[5], per_sensor_matrizes[6]],
                          3: [per_sensor_matrizes[7], per_sensor_matrizes[8], per_sensor_matrizes[9]],
                          4: [per_sensor_matrizes[10], per_sensor_matrizes[11], per_sensor_matrizes[12]],
                          5: [per_sensor_matrizes[14], per_sensor_matrizes[15]],
                          6: [per_sensor_matrizes[16], per_sensor_matrizes[17], per_sensor_matrizes[18]],
                          7: [per_sensor_matrizes[19], per_sensor_matrizes[20], per_sensor_matrizes[21]],
                          8: [per_sensor_matrizes[23], per_sensor_matrizes[24], per_sensor_matrizes[25]],
                          9: [per_sensor_matrizes[26], per_sensor_matrizes[27], per_sensor_matrizes[28],
                              per_sensor_matrizes[29]],
                          10: [per_sensor_matrizes[30], per_sensor_matrizes[31]],
                          11: [per_sensor_matrizes[33]],
                          12: [per_sensor_matrizes[34]],
                          13: [per_sensor_matrizes[35]],
                          14: [per_sensor_matrizes[36]],
                          15: [per_sensor_matrizes[37]]
                          }
    for user in user_to_sensor_map:
        matrix_list = user_to_sensor_map[user]
        sensor_matrix = matrix_list[0]
        for i in range(1, len(matrix_list)):
            sensor_matrix = sensor_matrix.add(matrix_list[i], fill_value=0)

        print(f'User {str(user)}:')
        print(sensor_matrix)
        fig, axes = calmap.calendarplot(sensor_matrix[['wholeday_avg']].squeeze(), cmap='coolwarm')
        plt.savefig(f'user_{str(user)}_wholeday_cal.png', dpi=600)
        fig.clear()
        plt.clf()
        plt.close(fig)
        fig, axes = calmap.calendarplot(sensor_matrix[['workday_avg']].squeeze(), cmap='coolwarm')
        fig.savefig(f'user_{str(user)}_workday_cal.png', dpi=600)
        fig.clear()
        plt.clf()
        plt.close(fig)

def per_devicetype_cals(per_sensor_matrizes):
    sensor_csv_file = 'sensor_to_workplace.csv'
    sensor_to_workplace_matrix = pd.read_csv(sensor_csv_file, sep=';')
    sensor_to_devicetype_map = {}
    for entry in sensor_to_workplace_matrix.iterrows():
        sensor_id = entry[1]['sensor_id']
        devicetype = entry[1]['device_type']
        if devicetype not in sensor_to_devicetype_map:
            sensor_to_devicetype_map[devicetype] = [per_sensor_matrizes[sensor_id]]
        else:
            sensor_to_devicetype_map[devicetype].append(per_sensor_matrizes[sensor_id])

    for devicetype in sensor_to_devicetype_map:

        matrix_list = sensor_to_devicetype_map[devicetype]

        if devicetype != 'Multiple':
            sensor_matrix = matrix_list[0]
            for i in range(1, len(matrix_list)):
                sensor_matrix = sensor_matrix.add(matrix_list[i], fill_value=0)
            print(f'Devicetype {str(devicetype)}:')
            print(sensor_matrix)
            fig, axes = calmap.calendarplot(sensor_matrix[['wholeday_avg']].squeeze(), cmap='coolwarm')
            plt.savefig(f'devicetype_{str(devicetype)}_wholeday_cal.png', dpi=600)
            fig.clear()
            plt.clf()
            plt.close(fig)
            fig, axes = calmap.calendarplot(sensor_matrix[['workday_avg']].squeeze(), cmap='coolwarm')
            fig.savefig(f'devicetype_{str(devicetype)}_workday_cal.png', dpi=600)
            fig.clear()
            plt.clf()
            plt.close(fig)
        else:
            numbering = 1
            for sensor in matrix_list:
                print(f'user workplace {numbering}')
                print(sensor)
                fig, axes = calmap.calendarplot(sensor[['wholeday_avg']].squeeze(), cmap='coolwarm')
                plt.savefig(f'user_workplace_{numbering}_wholeday_cal.png', dpi=600)
                fig.clear()
                plt.clf()
                plt.close(fig)
                fig, axes = calmap.calendarplot(sensor[['workday_avg']].squeeze(), cmap='coolwarm')
                fig.savefig(f'user_workplace_{numbering}_workday_cal.png', dpi=600)
                fig.clear()
                plt.clf()
                plt.close(fig)
                numbering += 1


if __name__ == '__main__':

    bdate_start = datetime.fromisoformat('2022-06-01')
    bdate_end = datetime.fromisoformat('2022-07-29')
    pandas_weekdays = pd.bdate_range(start=bdate_start, end=bdate_end, freq='B')
    # create wholeday series from csv file
    #create_per_day_plot()
    # create per device series from csv file
    create_per_device_plot()
