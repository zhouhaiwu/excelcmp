import time
import sys
import os

try:
    import psutil
    psutil_import = True
except ImportError:
    psutil_import = False


class Prog():
    def __init__(self, iterations, track_time, stream, title,
                 monitor, update_interval=None):
        """ Initializes tracking object. """
        # 迭代次数计数
        self.cnt = 0
        self.title = title
        # 总迭代次数
        self.max_iter = iterations
        # bool 值，指示是否打印总计时间
        self.track = track_time
        self.start = time.time()
        self.end = None
        self.item_id = None
        # 保存预计剩余时间
        self.eta = None
        self.total_time = 0.0
        self.last_time = self.start
        self.monitor = monitor
        # 存储将要使用的输出流
        self.stream = stream
        # 指示进度是否仍在计算中
        self.active = True
        self._stream_out = None
        self._stream_flush = None
        self._check_stream()
        self._print_title()
        # 更新间隔
        self.update_interval = update_interval

        if monitor:
            if not psutil_import:
                raise ValueError('psutil package is required when using'
                                 ' the `monitor` option.')
            else:
                self.process = psutil.Process()
        if self.track:
            self.eta = 1

    def update(self, iterations=1, item_id=None, force_flush=False):
        # 更新进度信息（进度条，进度百分比）
        """
        Updates the progress bar / percentage indicator.

        Parameters
        ----------
        iterations : int (default: 1)
            default argument can be changed to integer values
            >=1 in order to update the progress indicators more than once
            per iteration.
        item_id : str (default: None)
            Print an item_id sring behind the progress bar
        force_flush : bool (default: False)
            If True, flushes the progress indicator to the output screen
            in each iteration.

        """
        self.item_id = item_id
        self.cnt += iterations
        self._print(force_flush=force_flush)
        # 确认是否完成，已完成则进行收尾工作
        self._finish()

    def _check_stream(self):
        # 确认使用哪个输出流
        """Determines which output stream (stdout, stderr, or custom) to use"""
        if self.stream:
            try:
                if self.stream == 1 and os.isatty(sys.stdout.fileno()):
                    self._stream_out = sys.stdout.write
                    self._stream_flush = sys.stdout.flush
                elif self.stream == 2 and os.isatty(sys.stderr.fileno()):
                    self._stream_out = sys.stderr.write
                    self._stream_flush = sys.stderr.flush
                elif self.stream is not None and hasattr(self.stream, 'write'):
                    self._stream_out = self.stream.write
                    self._stream_flush = self.stream.flush
        else:
            print('Warning: No valid output stream.')

    def _elapsed(self):
        # 返回已花费时间
        """ Returns elapsed time at update. """
        self.last_time = time.time()
        return self.last_time - self.start

    def _calc_eta(self):
        # 计算预计完成剩余时间
        """ Calculates estimated time left until completion. """
        elapsed = self._elapsed()
        if self.cnt == 0 or elapsed < 0.001:
            return None
        rate = self.cnt / elapsed
        self.eta = (self.max_iter - self.cnt) / rate

    def _calc_percent(self):
        # 计算完成百分比
        """Calculates the rel. progress in percent with 2 decimal points."""
        return round(self.cnt / self.max_iter * 100, 2)

    def _get_time(self, _time):
        # 获得格式化后的时间
        if (_time = self.max_iter:
            self.total_time = self._elapsed()
            self.end = time.time()
            # 为了强制刷新进度条，见 progbar 与 progpercent 类中的 _print()
            self.last_progress -= 1  # to force a refreshed _print()
            self._print()
            if self.track:
                self._stream_out('nTotal time elapsed: ' +
                                 self._get_time(self.total_time))
            self._stream_out('n')
            self.active = False

    def _print_title(self):
        # 打印标题
        """ Prints tracking title at initialization. """
        if self.title:
            self._stream_out('{}n'.format(self.title))
            self._stream_flush()

    def _print_eta(self):
        # 打印预计剩余时间
        """ Prints the estimated time left."""
        self._calc_eta()
        self._stream_out(' | ETA: ' + self._get_time(self.eta))
        self._stream_flush()

    def _print_item_id(self):
        """ Prints an item id behind the tracking object."""
        self._stream_out(' | Item ID: %s' % self.item_id)
        self._stream_flush()

    def __repr__(self):
        str_start = time.strftime('%m/%d/%Y %H:%M:%S',
                                  time.localtime(self.start))
        str_end = time.strftime('%m/%d/%Y %H:%M:%S',
                                time.localtime(self.end))
        self._stream_flush()

        time_info = 'Title: {}n'
                    '  Started: {}n'
                    '  Finished: {}n'
                    '  Total time elapsed: '.format(self.title,
                                                    str_start,
                                                    str_end)
                    + self._get_time(self.total_time)
        if self.monitor:
                cpu_total = self.process.cpu_percent()
                mem_total = self.process.memory_percent()
                cpu_mem_info = '  CPU %: {:.2f}n'
                               '  Memory %: {:.2f}'.format(cpu_total, mem_total)

            return time_info + 'n' + cpu_mem_info
        else:
            return time_info

    def __str__(self):
        return self.__repr__()