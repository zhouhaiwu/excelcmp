from math import floor
from pyprind.prog_class import Prog
import time


class ProgBar(Prog):
    """
    Initializes a progress bar object that allows visuzalization
    of an iterational computation in the standard output screen.

    Parameters
    ----------
    iterations : `int`
        Number of iterations for the iterative computation.
    track_time : `bool` (default: `True`)
        Prints elapsed time when loop has finished.
    width : `int` (default: 30)
        Sets the progress bar width in characters.
    stream : `int` (default: 2).
        Setting the output stream.
        Takes `1` for stdout, `2` for stderr, or a custom stream object
    title : `str` (default:  `''`)
        Setting a title for the progress bar.
    monitor : `bool` (default: False)
        Monitors CPU and memory usage if `True` (requires `psutil` package).
    update_interval : float or int (default: None)
        The update_interval in seconds controls how often the progress
        is flushed to the screen.
        Automatic mode if update_interval=None.

    """
    def __init__(self, iterations, track_time=True, width=30, bar_char='#',
                 stream=2, title='', monitor=False, update_interval=None):
        Prog.__init__(self, iterations, track_time,
                      stream, title, monitor, update_interval)
        # 进度条宽度（横向长度）
        self.bar_width = width
        self._adjust_width()
        # 进度条使用的字符
        self.bar_char = bar_char
        # 保存上一进度条的字符数
        self.last_progress = 0
        self._print_labels()
        self._print_progress_bar(0)
        if monitor:
            try:
                self.process.cpu_percent()
                self.process.memory_percent()
            except AttributeError:  # old version of psutil
                self.process.get_cpu_percent()
                self.process.get_memory_percent()
        if self.item_id:
            self._print_item_id()

    def _adjust_width(self):
        # 进度条宽度大于迭代次数则把进度条宽度调整为迭代次数
        """Shrinks bar if number of iterations is less than the bar width"""
        if self.bar_width > self.max_iter:
            self.bar_width = int(self.max_iter)

    def _print_labels(self):
        self._stream_out('0% {} 100%n'.format(' ' * (self.bar_width - 6)))
        self._stream_flush()

    def _print_progress_bar(self, progress):
        # 打印进度条
        remaining = self.bar_width - progress
        self._stream_out('[{}{}]'.format(self.bar_char * int(progress),
                                         ' ' * int(remaining)))
        self._stream_flush()

    def _print(self, force_flush=False):
        # 计算当前进度条的字符数
        progress = floor(self._calc_percent() / 100 * self.bar_width)
        if self.update_interval:
            do_update = time.time() - self.last_time >= self.update_interval
        elif force_flush:
            do_update = True
        else:
            do_update = progress > self.last_progress

        if do_update and self.active:
            self._stream_out('r')
            self._print_progress_bar(progress)
            if self.track:
                self._print_eta()
            if self.item_id:
                self._print_item_id()
        self.last_progress = progress