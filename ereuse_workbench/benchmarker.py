import subprocess

from .utils import convert_capacity


class Benchmarker:
    """
    Set of method that run standard tests to assess the relative
    performance of components or the entire machine.

    See each method to know what they benchmark.
    """
    BENCHMARK_HDD_COMMON = 'bs=1M', 'count=256', 'oflag=dsync'

    def benchmark_hdd(self, disk):
        """
        Computers the reading and writing speed of a hard-drive by
        writing and reading a piece of the hard-drive.

        This method does not destroy existing data.
        """
        # Read
        cmd_read = ('dd', 'if=%s' % disk, 'of=/dev/null') + self.BENCHMARK_HDD_COMMON
        p = subprocess.Popen(cmd_read, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        _, err = p.communicate()
        reading = self._benchmark_hdd_to_mb(err)

        # Write
        cmd_write = ('dd', 'of=%s' % disk, 'if=%s' % disk) + self.BENCHMARK_HDD_COMMON
        p = subprocess.Popen(cmd_write, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        _, err = p.communicate()
        writing = self._benchmark_hdd_to_mb(err)

        return {
            '@type': 'BenchmarkHardDrive',
            'readingSpeed': reading,
            'writingSpeed': writing,
        }

    @staticmethod
    def _benchmark_hdd_to_mb(output: bytes) -> float:
        output = output.decode()
        value = float(output.split()[-2].replace(',', '.'))
        speed = convert_capacity(value, output.split()[-1][0:2], 'MB')
        assert 1 < speed < 300, '{} doesn\'t seem like normal HDD speed'.format(speed)
        return speed

    @staticmethod
    def processor():
        """Gets the BogoMips of the processor."""
        # https://en.wikipedia.org/wiki/BogoMips
        # score = sum(cpu.bogomips for cpu in device.cpus)
        mips = []
        with open('/proc/cpuinfo') as f:
            for line in f:
                if line.startswith('bogomips'):
                    mips.append(float(line.split(':')[1]))

        return sum(mips)
