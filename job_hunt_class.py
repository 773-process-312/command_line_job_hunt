import pandas as pd
import numpy as np
import time
import pickle
import sys
try:
    import Queue as Q  # ver. < 3.0
except ImportError:
    import queue as Q

class QueueObject(object):
    ''' The objects contained in the PriorityQueue.
        Parameters:
            description <str>  - String representing task to be done
            priority <int>     - [1 - 10] 1 is highest priority. 10 lowest.

        ** note : __lt__ must be implemented in py3 in order to compare QueueObjects
    '''
    def __init__(self, description,priority,verbose=True):
        self.description = description
        self.priority = priority
        if verbose:
            print("Added to Queue [{}]".format(self.priority))
    def __lt__(self, other):
         return self.priority < other.priority
    # def __cmp__(self, other): WORKS NO MORE (py2)
    #     #(a > b) - (a < b)
    #     return ((self.priority > other.priority) - (self.priority < other.priority))
    def get_queue_object(self):
        return [self.description,self.priority]
    def __str__(self):
        return self.__repr__()
    def __repr__(self):
        return "{} [{}]".format(self.description,self.priority)



class MyPriorityQueue(object):
    ''' The queue implemented by the job hunt class
        A Priority Queue with some additional methods (read_pickle,to_pickle) and custom __repr__

        *Methods:
            *User functionality:
                pop():                  To remove the top item from the queue use jh.q.pop().
                                        An alternative, if preferred, is jh.q.q.get()
            *Hidden functionality:
                to_pickle(file_name):   Used by jh.save() to save queue. file_name hard coded in job_hunt class
                read_pickle(file_name): Called when job_hunt_class is ran in non-init mode to load previously saved queue.
                                        file_name hard coded in job_hunt class.
    '''
    def __init__(self):
        self.q = Q.PriorityQueue()
    def __repr__(self):
        temp_q = Q.PriorityQueue()
        str_out = ""
        while not self.q.empty():
            next_item = self.q.get()
            temp_q.put(next_item)
            str_out += "{} \n".format(next_item)
        self.q = temp_q
        return str_out
    def put(self,obj):
        self.q.put(obj)
    def to_pickle(self,file_name):
        out_list = []
        temp_q = Q.PriorityQueue()
        while not self.q.empty():
            next_item = self.q.get()
            temp_q.put(next_item)
            out_list.append(next_item.get_queue_object())
        with open(file_name, 'wb') as handle:
            pickle.dump(out_list, handle, protocol=pickle.HIGHEST_PROTOCOL)
        self.q = temp_q
    def read_pickle(self,file_name):
        with open(file_name, 'rb') as handle:
            in_list = pickle.load(handle)
        for qo in in_list:
            self.put(QueueObject(qo[0],qo[1],False))
    def pop(self):
        return self.q.get()



class job_hunt(object):

    def __init__(self,init=False):
        if init:
            self.df = self.df_init()
            self.q = MyPriorityQueue()
        else:
            self.df = self.load_d()
            self.q = self.load_q()
    def df_init(self):
        return pd.DataFrame(data=[],columns=['company','position','date','status','date_lc'])
    def load_d(self):
        return pd.read_pickle('job_search.pickle')
    def load_q(self):
        my_queue = MyPriorityQueue()
        my_queue.read_pickle('job_queue.pickle')
        return my_queue
        # return pd.read_pickle('job_queue.pickle')

    def add_row(self,list_add):
        if len(list_add)==4:
            list_add.append("")
        n_arr = np.array(list_add).reshape(1,len(list_add))
        col = self.df.columns
        pds = pd.DataFrame(n_arr,columns=col)
        self.df = self.df.append(pds,ignore_index=True)
        return self.df

    def add_queue(self,list_add):
        if len(list_add)<2:
            self.q.put(QueueObject(list_add[0], 7))
        else:
            self.q.put(QueueObject(list_add[0], list_add[1]))

    def save(self):
        self.df.to_pickle('job_search.pickle')
        self.q.to_pickle('job_queue.pickle')
        print('job hunt saved.')

    def __str__(self):
        return self.__repr__()

    def __repr__(self):
        str_t = ""
        cols = list(self.df.columns)
        str_t += "__________________________________{} \n\n".format(time.strftime("%Y-%m-%d"))
        str_t += "{}________,   {}___,  {}_________ \n\n".format(cols[2],cols[3],cols[0])
        X =  self.df.values
        for x in X:
            if x[3] == "Closed":
                str_t += "{}  ,   {}   ,  {} ,  {} \n".format(x[2],x[3],x[0],x[4])
            else:
                str_t += "{}  ,   {}  ,  {} \n".format(x[2],x[3],x[0])
        return str_t




if __name__ == '__main__':
    ''' If ran from command line, receive back job_hunt object jh

        *Interacting with jh:
            *main:
                jh                        - Displays the job_hunt summary
                jh.df <Pandas DataFrame>  - The DataFrame conataining all the job_hunt data
                jh.q  <MyPriorityQueue>   - The PriorityQueue that tells you what to work on next

            *methods:
                jh.add_row(<list>)  -  Adds a new row to the job_hunt DataFrame (representing a job you appiled for)
                        parameters:
                            <list>  -  [*<str>] Standard entry is as follows:
                                       ['Company Name', 'Position', 'Date (ex. '2017-07-14')', 'Applied' (literal)]
                jh.add_queue(<list>) - Adds a new "to-do" item to the MyPriorityQueue
                        parameters:
                            <list>  -  [<str>,<int>] Standard entry is as follows:
                                       ['Description of task to do', priority (ex. 4) ]

                                       *priority - [1-10] with 1 being highest priority and 10 being lowest
                jh.q.pop()          -  Removes top item from MyPriorityQueue (after completing the item).
                jh.save()           -  Writes the job_hunt DataFrame and MyPriorityQueue to pickle files respectively

                jh.df.iloc[?,?] = XX  - Update rows by using your Pandas skills (or make your own method if preferred)

        * Feel free to customize to suit your needs.

        Running:
            In ipython:
                    'run job_hunt_class.py'
                or  'run job_hunt_class.py "init"' (if first time)
            From command line proper:
                    'python -i job_hunt_class.py'
                or  'python -i job_hunt_class.py "init"' (if first time)
    '''
    if len(sys.argv) > 1:
        if sys.argv[1]== "init":
            jh = job_hunt(True)
    else:
        jh = job_hunt()
