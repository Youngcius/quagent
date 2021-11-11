"""
Bar chart demo with pairs of bars grouped for easy comparison.
"""
import numpy as np
import matplotlib as mpl

mpl.use('Agg')  # for backend without gui
import matplotlib.pyplot as plt

plt.rcParams['font.sans-serif'] = ['SimHei']  # set default font for mac


def draw_histogram(a_num, b_num, c_num, d_num, n_groups, path):
    """Draw result.

    :param a_num: tuple of select A users.
                  eg: (12, 2, 34, 12, 78, 13).
    :param n_groups: The length of tuple a_num.
    :param path: The path images would save.
    """
    fig, ax = plt.subplots()
    index = np.arange(n_groups)
    bar_width = 0.2
    opacity = 0.4
    error_config = {'ecolor': '0.3'}

    rects1 = plt.bar(index, a_num, bar_width,
                     alpha=opacity,
                     color='b',
                     error_kw=error_config,
                     label='A')

    rects2 = plt.bar(index + bar_width, b_num, bar_width,
                     alpha=opacity,
                     color='r',
                     error_kw=error_config,
                     label='B')

    rects3 = plt.bar(index + bar_width * 2, c_num, bar_width,
                     alpha=opacity,
                     color='b',
                     error_kw=error_config,
                     label='C')

    rects4 = plt.bar(index + bar_width * 3, d_num, bar_width,
                     alpha=opacity,
                     color='g',
                     error_kw=error_config,
                     label='D')

    def autolabel(rects):
        # attach some text labels
        for rect in rects:
            height = rect.get_height()
            ax.text(rect.get_x() + rect.get_width() / 2.0, 1.05 * height,
                    '%d' % int(height), ha='center', va='bottom')

    autolabel(rects1)
    autolabel(rects2)
    autolabel(rects3)
    autolabel(rects4)

    plt.xlabel(u'题号')
    plt.ylabel(u'人数')
    plt.title(u'答题结果统计')
    # plt.xticks(index + bar_width, ('1', '2', '3', '4', '5', '6'))
    plt.xticks(index + bar_width, tuple(map(str, range(1, n_groups + 1))))
    ax.set_ybound(0, 40)

    plt.tight_layout()
    # plt.show()
    plt.savefig(path)
    plt.clf()  # note: remember plt.clf() to clear buffer
    plt.close()


def draw_piechart(question_info, explode, path):
    """Draw pie chart of each question.

    :param: question_info is a list of users.  eg: [12, 23, 43, 13]
            means 12 people select A, 23 select B, 43 C, 13 D.
    """
    labels = 'A', 'B', 'C', 'D'
    colors = ['yellowgreen', 'gold', 'lightskyblue', 'lightcoral']
    # explode = (0, 0.1, 0, 0) # only "explode" the 2nd slice (i.e. 'Hogs')

    plt.pie(question_info, explode=explode, labels=labels, colors=colors,
            autopct='%1.1f%%', shadow=True)
    # Set aspect ratio to be equal so that pie is drawn as a circle.
    plt.axis('equal')

    # plt.show()
    plt.savefig(path)
    plt.clf()  # note: remember plt.clf() to clear buffer
    plt.close()
