import matplotlib.pyplot as plt
import numpy as np
import sys
import os

def main():
    #_, ax = plt.subplots(3, 1, figsize=(19.2,10.8)) # 3 default
    #_, ax = plt.subplots(1, 1, figsize=(9.6,5.4)) # 1
    #_, ax = plt.subplots(2, 1, figsize=(10,7.5))  # 2 compact tall
    _, ax = plt.subplots(2, 1, figsize=(14,7.5))  # 2 wide
    #max_x = 3600
    max_x = 25200
    i = 1
    files = []
    while i < len(sys.argv):
        arg = sys.argv[i]
        if 'max' in arg:
            v = sys.argv[i].split('max')[1]
            max_x = int(v)
        else:
            files.append(arg)
        i+=1

    bar_offset = 0

    for fname in files:
        with open(fname) as f:
            fname = os.path.basename(fname)
            headers = f.readline()
            headers = headers.replace('\n','')
            header_fields = headers.split(',')
            metrics = header_fields[1:]
            print(metrics)

            lines = f.read().splitlines()
            line = eval(lines[-1])
            
            #time = np.array([x for x in range(0,len(line[1]))])
            time = np.array([int(l.split(',')[0]) for l in lines])
            # Delivery rate
            delivery = np.array(line[1])
            # Cumulative
            cumulative = np.array(line[2])
            # Delay E2E
            delay = {}
            delay_x = np.array([])
            delay_y = np.array([])
            for v in line[3].values():
                if v in delay:
                    delay[v] += 1
                else:
                    delay[v] = 1
            for k in sorted(delay, key=delay.get, reverse=True):
                delay_x = np.append(delay_x, [k/60])
                delay_y = np.append(delay_y, [delay[k]])
            # Progress rate
            progress = np.array(line[4],dtype=object)
            progress[-1] = round(sum(progress[-1])/len(progress[-1]),2)

            #f_size = 54277586
            f_size = os.path.getsize('../torrents/file.pdf')
            nodes = 200

            time = np.concatenate(([0],time))
            """
            cumulative = np.concatenate(([0],cumulative))
            ax[0].plot(time[time<=max_x],cumulative[time<=max_x],label='{}'.format(fname))
            ax[0].set_ylabel('Bytes')
            #if max_x == 3600:
            ax[0].axhline(nodes*f_size,linestyle='--',label='Maximum')
            ax[0].set_title('Cumulative download progress')
            #ax[0].legend()
            ax[0].grid()
            """

            size = len(time)
            delay_x = np.append(delay_x, np.arange(len(delay_x),size,1))
            delay_y = np.append(delay_y, np.zeros(size-len(delay_y)))
            delay_x = delay_x*(time[-1]/np.max(delay_x))
            ax[0].bar(delay_x[delay_x<=max_x]+bar_offset,delay_y[delay_x<=max_x],label='{}'.format(fname),width=8)
            bar_offset += 1
            ax[0].set_ylabel('Number of OBUs')
            ax[0].set_title('Number of OBUs that reached 100% in each instant')
            ax[0].legend()
            ax[0].grid()

            progress = np.concatenate(([0],progress))
            ax[1].plot(time[time<=max_x],progress[time<=max_x]/f_size,label='Cumulative progress {}'.format(fname))
            ax[1].set_title('Progress rate (average of download progress across all OBUs)')
            #if max_x == 3600:
            ax[1].axhline(1,linestyle='--',label='Maximum')
            ax[1].set_ylabel('Download percentage')
            #ax[2].legend()
            ax[1].grid()

            plt.xlabel("Time (seconds)")
    plt.show()

if __name__ == "__main__":
    main()
