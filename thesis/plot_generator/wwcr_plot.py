from matplotlib import pyplot as plt
import numpy as np

plt.style.use('seaborn-whitegrid')
plt.rcParams['text.usetex'] = True

if __name__ == '__main__':
    np.random.seed(1)
    noise = np.random.normal(0, 0.1, 96)
    print(noise)
    x = np.linspace(0, 24, 96)    # 96 values from 0 to 24
    y_1 = np.piecewise(x, [x < 8, np.logical_and(8 <= x,x < 18), x >= 18], [0.5, 8, 0.5])
    y_1 = y_1 + noise
    y_2 = np.piecewise(x, [x < 8, np.logical_and(8 <= x,x < 18), x >= 18], [3, 5, 3])
    y_2 = y_2 + noise
    average_y_1 = np.average(y_1)
    wwcr_y_1 = 8/average_y_1
    average_y_2 = np.average(y_2)
    wwcr_y_2 = 5/average_y_2
    integral_y_1 = np.trapz(y_1, x)
    integral_y_2 = np.trapz(y_2, x)
    print(y_1)
    fig, ax = plt.subplots()
    ax.set_xlabel('time in hours')
    ax.set_ylabel('power in Watt')
    ax.set_title('Workday to Weekday Consumption Ratio Example')
    ax.text(0, 5.5, f'\\textbf{{function}} $\\mathbf{{f_1}}$ \n $AVG(f_1)$: {average_y_1:.2f} \n $AVG_w(f_1)$: 8\n WWCR: {wwcr_y_1:.2f} \n $\int_{{{0}}}^{{{24}}}$: {integral_y_1:.2f}', ha='left', va='center', bbox=dict(facecolor='grey', alpha=0.5))
    ax.text(19, 5.5, f'\\textbf{{function}} $\\mathbf{{f_2}}$ \n $AVG(f_2)$: {average_y_2:.2f} \n $AVG_w(f_2)$: 5\n WWCR: {wwcr_y_2:.2f} \n $\int_{{{0}}}^{{{24}}}$: {integral_y_2:.2f}', ha='left', va='center', bbox=dict(facecolor='grey', alpha=0.5))
    ax.text(7, 5.5, '\\textbf{$f_1$}', ha='center', va='center', rotation=45, bbox=dict(boxstyle="rarrow", facecolor='white', alpha=0.5))
    ax.text(12, 4.5, '\\textbf{$f_2$}', ha='center', va='center', rotation=45, bbox=dict(boxstyle="rarrow", facecolor='white', alpha=0.5))
    ax.plot(x, y_1, label='f_1', linewidth=2)
    ax.plot(x, y_2, label='f_2', linewidth=2)
    print("showing plot ...")
    plt.savefig('../images/wwcr_plot.png', dpi=600)
    plt.show()
