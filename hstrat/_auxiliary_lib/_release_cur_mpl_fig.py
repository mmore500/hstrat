from matplotlib import pyplot as plt


# adapted from https://stackoverflow.com/a/61039272
# fixes warning
# Figures created through the pyplot interface (`matplotlib.pyplot.figure`) are
# retained until explicitly closed and may consume too much memory.
def release_cur_mpl_fig():
    plt.clf()
    plt.close()
