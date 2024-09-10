"""
CMPS 2200  Recitation 1

In this recitation, we will implement various methods of searching and compare their runtimes.
"""

### imports
import time
import random
import matplotlib.pyplot as plt
import itertools
from concurrent.futures import ProcessPoolExecutor

###

def linear_search(mylist, key):
    """ done. 
    Searches for key in mylist. Returns the smallest index so that mylist[index]=key, or -1 if no index exists.
    """
    for i,v in enumerate(mylist):
        if v == key:
            return i
    return -1

def binary_search(mylist, key):
    """ done. 
    Assume that mylist is sorted and returns the smallest index such that mylist[index]=key, or -1 if no index exists.
    """
    return _binary_search(mylist, key, 0, len(mylist))

def _binary_search(mylist, key, left, right):
    """
    Recursive implementation of binary search.

    Params:
      mylist....a sorted list to search
      key.......search key
      left......left index into list to search
      right.....right index into list to search. So we know mylist[right]>key

    Returns:
      index of key in mylist, or -1 if not present.
    """
    if right >= left:
      length = (left + right)//2
      # print("key: ", key, "length list ", mylist[length] )
      if length > len(mylist) -1:
           return -1 
      elif key == mylist[length]:
           return length
      elif key > mylist[length]:
            return _binary_search(mylist, key, length + 1, right)
      else:
            return _binary_search(mylist, key, left, length - 1)   
    else:
        return -1

def iterative_binary_search(mylist, key):
  '''done.
  Iterative implementation of binary search. Assumes mylist is sorted.
  The behavior should be the same as the behavior of binary_search
  But it should be faster due to avoiding overhead.
  This does not necessarily return the smallest index such that mylist[index]=key
  '''
  current_lower_bound = 0
  current_upper_bound = len(mylist)
  while current_upper_bound!= current_lower_bound:
    middle = (current_lower_bound + current_upper_bound) // 2
    if key<mylist[middle]:
        current_upper_bound = middle
    elif key>mylist[middle]:
        current_lower_bound = middle +1
    elif mylist[middle] == key:
        return middle
  return -1


def time_search(search_fn, args):
    """
    Return the number of seconds to run this
    search function on this list.

    Note 1: `sort_fn` parameter is a function.
    Note 2: args is a list of arguments for the search function.
    Note 3: time.time() returns the current time in seconds.

    input:
      sort_fn.....the search function
      args........the list of arguments for sort_fn.

    Returns:
      the number of milliseconds it takes to run this
      search function on this input.
    If you want to cleanly handle the possibility that different functions expect different numbers of arguments, see https://www.bitecode.dev/p/the-splat-operator-or-args-and-kwargs
    Otherwise, just assume that args is of the form [mylist,key].
    """
    start =time.perf_counter()
    search_fn(args[0], args[1])
    end = time.perf_counter()
    return (end - start)
   
#-----
#Parallel search functions
def create_parallel_search_function_with_num_processes(num_processes):
   '''done.
   A wrapper around parallel search so that it can be easily run with only 2 arguments, mylist and key.
   Returns a function with the value of num_processes curried in.
   '''
   def function_to_return(mylist,key):
      return parallel_search(mylist,key,num_processes)
   return function_to_return
def parallel_search(mylist, key, num_processes):#copied and modified from Module1/
    '''done.
    Assumes mylist is a list (as above)
    key is an element, possibly in the list.
    num_processes is a positive integer that indicates how many processes to start.'''
    interval= len(mylist)//num_processes +1 #each process searches a sublist of length interval. The kth process searches k*interval:(k+1)*interval.

    functions_and_arguments_to_perform_in_parallel = [(_processors_linear_search, [mylist, interval, k, key] ) for k in range(num_processes)]
    results= _in_parallel(
       functions_and_arguments_to_perform_in_parallel, num_processes=num_processes
    )
    # combine results
    for index, r in enumerate(results):
      if r != -1:
        return index*interval + r
    return -1


def _processors_linear_search(args):#This function is called on each processor in parallel search. The underscore means that you're not supposed to call it directly.
  '''done.
  A wrapper around linear search so that it takes the full list, together with an index k and an interval (an integer) 
  such that this processor's task is to search the elements between interval*k and interval*(k+1)-1.
  I moved slicing mylist into this function, which is performed by each processor.
  I worry that slicing outside of this function would not be performed in parallel, and this would slow the function down.
  '''
  mylist,interval,k,key=args[0],args[1],args[2],args[3]
  return linear_search(mylist[interval*k:interval*(k+1)],key)

def _in_parallel(funcs_and_args, num_processes=2): #This is a function used by parallel search.
    '''done.
    funcs and args is a list of pairs, (func,arg) of functions and their arguments to perform asynchronously.
    Returns a list of the results of applying the function func to the argument arg.
    '''
    with ProcessPoolExecutor(max_workers=num_processes) as executor:
        futures = [executor.submit(func, arg) for func, arg in funcs_and_args]
        return [future.result() for future in futures]
    

#----
#Plotting functions
def plot_parallel_runtimes(runtime_type="average", num_processes=[1,2,5]):
  '''
  done
  params:
    runtime_type..... How to choose the key (either "average" or "worst case")
    num_processes.... A list of integers that represents the number of processes to use.
  returns None
  Has the side effect of creating and saving a plot of the runtimes
  '''
  for num_processes in [1,2,5]:
    list_lengths = list(range(0,1_000_000, 100_000))
    if runtime_type=="average":
      inputs = [[range(i), random.randint(0,i), num_processes] for i in list_lengths] #Average case
    elif runtime_type=="worst case":
      inputs = [[range(i), i, num_processes] for i in list_lengths] #Worst case
    else: 
      print("What sort of runtime, average or worst case?")
      return None
    outputs = []
    for input in inputs:
        outputs.append(time_search(parallel_search, input))
    plt.plot(list_lengths, outputs, label=f'{runtime_type} runtime for parallel search with {num_processes} processes')
#plt.text(94,1000,'$n_0$', fontsize=18, color='g')

  plt.xlabel("list length")
  plt.ylabel('runtime (seconds)')
  plt.title(f'{runtime_type} runtimes for varying number of processes')
  plt.legend()
  plt.tight_layout()
  plt.show()
  plt.savefig('multiprocessor_plot.png') 


#plot_parallel_runtimes(runtime_type="worst case") #Run this line to see how different numbers of processors affect performance.

def compare_search(search_function1, search_function2, inputs):
    """
    Compare the running time of two search functions.
    parameters
      search_function1...... a function of 2 variables (the first function to time)
      search_function2...... a function of 2 variables (the other function to time)
      inputs................ a list of pairs (mylist, -1)
    Returns:
      None
    Has the side effect of creating and saving a plot. On the x axis, put the sizes of the lists. On the y axis, put the runtimes.

    To implement, you'll use the time_search function to time each call. Put the results in a list and plot. Then repeat for search_function2.
    """
    runtimes1 = []
    runtimes2 = []
    xaxis = []
    for mylist, key in inputs:
        list_size = len(mylist)
        xaxis.append(list_size)  # Track the list size for the x-axis
        
        # Time both search functions
        time1 = time_search(search_function1, [mylist, key])
        time2 = time_search(search_function2, [mylist, key])

        runtimes1.append(time1)
        runtimes2.append(time2)
    plt.plot(xaxis, runtimes1, label='Search Function 1', marker='o')
    plt.plot(xaxis, runtimes2, label='Search Function 2', marker='x')
    
    plt.xlabel('Length of List')
    plt.ylabel('Runtime (seconds)')
    plt.title('Comparison of Search Functions')
    plt.legend()
    plt.show()

def generate_plots_for_all_pairs(list_of_functions):
   '''Assumes list_of_functions is a list of search functions to time.
   Creates a plot comparing every pair. Saves the plot.
   Returns None
   '''
   list_lengths = list(range(0,1_000_000, 100_000)) #You might consider reducing these numbers while you test your code.
   inputs =[(range(i),-1) for i in list_lengths]

   for f1,f2 in itertools.combinations(list_of_functions,2):
      compare_search(f1,f2,inputs)

  #----TOP LEVEL
   ### We define a list of functions to study.
parallelsearch1= create_parallel_search_function_with_num_processes(1) #searching in parallel with 1 processor (like linear search, but with some overhead)
parallelsearch1.__name__="parallel_1_process" #fixing the name
parallelsearch2= create_parallel_search_function_with_num_processes(2) #searching in parallel with 2 processors.
parallelsearch2.__name__="parallel_2_processes"
parallelsearch5= create_parallel_search_function_with_num_processes(5) #searching in parallel with 5 processors.
parallelsearch5.__name__="parallel_5_processes"
# functions_to_study = [linear_search, binary_search,iterative_binary_search]
functions_to_study = [parallelsearch1,parallelsearch2,parallelsearch5]

generate_plots_for_all_pairs(functions_to_study)

#---TESTS
#We also need to check that these functions are correct.
def test_functions_correctness(functions_to_study):
    for f in functions_to_study:
      print(f)
      assert f([1,2,3,4,5], 5) == 4
      assert f([1,2,3,4,5], 1) == 0
      assert f([1,2,3,4,5], 6) == -1
      #TODO add two more test cases
      assert f([1,4,6,7,8,10,11,14,15,220], 8) == 4
      assert f([1,4,6,7,8,10,11,14,15,220], 100) == -1

test_functions_correctness(functions_to_study)
