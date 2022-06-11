# knocker.py
# Based on the repository Steve-FTPKnocker.
# Written by Steve D. J. on 2022/6/9 for FTP_Explorer.

import ftplib
import threading
from file_indexer import FileIndexer


def num2ip(num):
    """ Calculate IP from a number.

    :param num: an integer between 0 and 4,294,967,295(2^32 - 1) (int)
    :return: ip (list, like [0, 0, 0, 0])
    """
    ip = [0, 0, 0, 0]
    ip[0] = int(num / 16777216)
    ip[1] = int((num % 16777216) / 65536)
    ip[2] = int((num % 65536) / 256)
    ip[3] = int(num % 256)

    return ip


def ip2num(ip):
    """ Get an integer from an IP.

    :param ip: ip (list, like [0, 0, 0, 0])
    :return: num, an integer between 0 and 4,294,967,295(2^32 - 1) (int)
    """
    num = int(ip[0]) * 16777216 + int(ip[1]) * 65536 + int(ip[2]) * 256 + int(ip[3])

    return num


class Knocker:
    """ Traverse the given IPs and find hosts supporting anonymous accessing with multi-threading.

    -start_ip: the first IP to knock (str, default='42.192.44.52').
    -end_ip: the last IP to knock (str, default='42.192.44.52').
    -thread_num: number of threads used to knock (int, default=1).
    -ip_groups: dictionary, key=thread_ct, value={'start_ip': [0, 0, 0, 0], 'end_ip': [0, 0, 0, 0]}. IPs in one group
        is for one thread to knock.
    -ftp_hosts: a list to cache found hosts.
    """
    def __init__(self, start_ip='42.192.44.52', end_ip='42.192.44.52', thread_num=1):
        """ Initialize the Knocker object.

        :param start_ip: the first IP to knock (str, default='42.192.44.52')
        :param end_ip: the last IP to knock (str, default='42.192.44.52')
        :param thread_num: number of threads used to knock (int, default=1)
        """
        self.start_ip = start_ip
        self.end_ip = end_ip
        self.thread_num = thread_num
        self.ip_groups = {}
        for thread_ct in range(0, self.thread_num):
            self.ip_groups[thread_ct] = {'start_ip': [0, 0, 0, 0], 'end_ip': [0, 0, 0, 0]}
        self.assign_workload()
        self.ftp_hosts = []

    def assign_workload(self):
        """ Assign knocking workloads to threads, after executing this method the value of member ip_groups will be
        updated.

        :return: None
        """
        start_ip_parts = self.start_ip.split('.')
        end_ip_parts = self.end_ip.split('.')
        start_ip_num = ip2num(start_ip_parts)
        end_ip_num = ip2num(end_ip_parts)
        total_ip_num = end_ip_num - start_ip_num
        ip_left = total_ip_num % self.thread_num
        ip_num_4_1_thread = (total_ip_num - ip_left) / self.thread_num
        for thread_ct in range(0, self.thread_num):
            if thread_ct == 0:
                for i in range(0, 4):
                    self.ip_groups[thread_ct]['start_ip'][i] = int(start_ip_parts[i])
                thread_start_ip_num = ip2num(self.ip_groups[thread_ct]['start_ip'])
            else:
                thread_start_ip_num = ip2num(self.ip_groups[thread_ct-1]['end_ip']) + 1
                self.ip_groups[thread_ct]['start_ip'] = num2ip(thread_start_ip_num)
            if thread_ct != self.thread_num - 1:
                thread_end_ip_num = thread_start_ip_num + ip_num_4_1_thread
            else:
                thread_end_ip_num = thread_start_ip_num + ip_num_4_1_thread + ip_left
            self.ip_groups[thread_ct]['end_ip'] = num2ip(thread_end_ip_num)

    def knock(self, ip):
        """ Check a host supporting anonymous accessing or not. Inspired by the method from
        https://github.com/kennell/ftpknocker.

        :param ip: the ip of a host (str, like '0.0.0.0')
        :return: None
        """
        try:
            ftp = ftplib.FTP()
            ftp.connect(ip, 21, 2.0)
            if '230' in ftp.login(user='anonymous', passwd='example@email.com'):
                self.ftp_hosts.append(ip)
                print(ip)
                ftp.quit()
        except ftplib.all_errors:
            pass

    def task_4_1_thread(self, thread_ct):
        """ This method is packed to be called in threading.Thread().
        Here's how one knocking thread works.

        :param thread_ct: index of the thread (int)
        :return: None
        """
        for i in range(self.ip_groups[thread_ct]['start_ip'][0], self.ip_groups[thread_ct]['end_ip'][0]+1):
            for j in range(self.ip_groups[thread_ct]['start_ip'][1], self.ip_groups[thread_ct]['end_ip'][1]+1):
                for k in range(self.ip_groups[thread_ct]['start_ip'][2], self.ip_groups[thread_ct]['end_ip'][2]+1):
                    for m in range(self.ip_groups[thread_ct]['start_ip'][3], self.ip_groups[thread_ct]['end_ip'][3]+1):
                        ip = str(i) + '.' + str(j) + '.' + str(k) + '.' + str(m)
                        print("Thread " + str(thread_ct) + ": knocking on " + ip)
                        self.knock(ip)

                    self.save_result()

    def save_result(self):
        """ Write hosts that have been found from memory to disk.

        :return: None
        """
        file = open('./result.txt', 'w')
        for host in self.ftp_hosts:
            file.write(host)
            file.write('\n')
        file.close()
        # self.ftp_hosts = []

    def run_knocker(self):
        """ Start multi-threading knocking task.

        :return: None
        """
        thread_list = []
        for thread_ct in range(0, self.thread_num):
            thread = threading.Thread(target=self.task_4_1_thread, args=(thread_ct,))
            thread_list.append(thread)
            thread.start()
        for thread in thread_list:
            thread.join()

    def index_while_knocking(self, ip):
        """ Check a host supporting anonymous accessing or not, index file structure if supported. Inspired by the
        method from https://github.com/kennell/ftpknocker.

        :param ip: the ip of a host (str, like '0.0.0.0')
        :return: None
        """
        try:
            ftp = ftplib.FTP()
            ftp.connect(ip, 21, 2.0)
            if '230' in ftp.login(user='anonymous', passwd='example@email.com'):
                self.ftp_hosts.append(ip)
                print(ip)
                indexer = FileIndexer(ip)
                indexer.index()
                indexer.save_file_tree()
                ftp.quit()
        except ftplib.all_errors:
            pass


if __name__ == '__main__':
    my_knocker = Knocker('42.192.44.0', '43.192.44.255', 16)
    my_knocker.run_knocker()
