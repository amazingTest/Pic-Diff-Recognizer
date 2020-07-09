import math
import sys
import os
import shutil
import random
import string

def get_batch_indexes(some_list, batch_size=50):
    list_length = len(some_list)
    batch_indexes = []
    batch_length = int(math.ceil(list_length / batch_size))
    start_index = 0
    end_index = batch_size - 1
    for i in range(batch_length):
        if i + 1 == batch_length:
            batch_indexes.append((start_index, list_length))
            break
        batch_indexes.append((start_index, end_index))
        start_index += batch_size
        end_index += batch_size
    return batch_indexes


def get_MD5(file_path):
    files_md5 = os.popen('md5 %s' % file_path).read().strip()
    file_md5 = files_md5.replace('MD5 (%s) = ' % file_path, '')
    return file_md5


def copy_files_in_dir(path, out):
    if not os.path.isdir(out):
        os.makedirs(out)
    for files in os.listdir(path):
        name = os.path.join(path, files)
        back_name = os.path.join(out, files)
        if os.path.isfile(name):
            if os.path.isfile(back_name):
                if get_MD5(name) != get_MD5(back_name):
                    shutil.copyfile(name, back_name)
            else:
                shutil.copyfile(name, back_name)
        else:
            if not os.path.isdir(back_name):
                os.makedirs(back_name)
            copy_files_in_dir(name, back_name)


def processBar(num, total, message):
    rate = num / total
    rate_num = int(rate * 100)
    if rate == 0:
        r = f'\r{message}\n%s>%d%%' % ('=' * rate_num, rate_num,)
    else:
        r = '\r%s>%d%%' % ('=' * rate_num, rate_num,)
    if rate_num == 100:
        r += '\n'
    sys.stdout.write(r)


def getKey(digit=16):
    a = string.ascii_letters + string.digits
    key = random.sample(a, digit)
    keys = "".join(key)
    return keys



def get_month_end_timestamp(d_t):
    timestamp = None
    try:
        timestamp = d_t.replace(day=31, hour=23, minute=59, second=59, microsecond=0).timestamp()
    except ValueError:
        try:
            timestamp = d_t.replace(day=30, hour=23, minute=59, second=59, microsecond=0).timestamp()
        except ValueError:
            try:
                timestamp = d_t.replace(day=29, hour=23, minute=59, second=59, microsecond=0).timestamp()
            except ValueError:
                try:
                    timestamp = d_t.replace(day=28, hour=23, minute=59, second=59, microsecond=0).timestamp()
                except BaseException:
                    print('get timestamp error！')
                    return timestamp
    return round(int(timestamp))


def get_months_end_time_stamps(start_date_time, count):
    time_stamps = []
    time_info = {'year': start_date_time.year, 'month': start_date_time.month, 'changing_year': False}
    date_time = start_date_time
    for i in range(count):
        date_time = date_time.replace(year=time_info['year'], month=time_info['month']) if time_info['changing_year']\
            else date_time.replace(month=time_info['month'])
        month_end_time_stamp = get_month_end_timestamp(date_time)
        time_stamps.append(month_end_time_stamp)

        if time_info['month'] is not 12:
            time_info['month'] += 1
            time_info['changing_year'] = False
        else:
            time_info['year'] += 1
            time_info['month'] = 1
            time_info['changing_year'] = True

    return time_stamps


# [{1588287599: 'Cq2o3v8I097rTik6'}, {1590965999: 'rNWJemBG4xdSQj8T'}........]
def generate_secret_key_for_every_month_end(start_date_time, count):
    result = [{i: getKey()} for i in get_months_end_time_stamps(start_date_time, count)]
    return result


if __name__ == '__main__':
    pass
    # d_t = datetime.datetime.today()
    # re = generate_secret_key_for_every_month_end(d_t, 120)
    # print(re)
