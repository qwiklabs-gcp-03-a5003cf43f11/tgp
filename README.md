Please do not use this branch as it is currently being used for testing purposes.

# tgp

*tgp* is a task-granularity profiler for multi-threaded, task-parallel applications running on the Java Virtual Machine (JVM).

*tgp* detects each task created by an application, collecting its granularity either in terms of bytecode count, i.e., the number of bytecode instructions executed, or reference-cycles count, i.e., the number of cycles elapsed during task execution, collected at the nominal frequency of the CPU (even in case of frequency scaling).

*tgp* assists developers in locating performance drawbacks related to suboptimal task granularity. On the one hand, *tgp* helps detecting situations where many small tasks carry out few computations, potentially introducing parallelization overheads due to significant interference and contention between them. On the other hand, *tgp* helps detecting situations where only few large tasks are spawned, each of them performing substantial computations, potentially resulting in low CPU utilization or load imbalance.

In addition, *tgp* profiles calling contexts, i.e., all methods open on the call stack upon the creation, submission, or execution of a task. This information helps the user locate classes and methods to modify to optimize task granularity.
 
## Table of Contents

1. [Terminology](#terminology)
2. [Profiling Modes](#profiling-modes)
3. [Metrics](#metrics)
4. [Requirements](#requirements)
5. [Testing *tgp*](#testing-tgp)
    * [Usage](#usage)
       + [Bytecode Profiling](#bytecode-profiling)
       + [Reference-cycles Profiling](#reference-cycles-profiling)
       + [JVM- and OS-layer Metrics](#jvm--and-os-layer-metrics)
       + [Calling-context Profiling](#calling-context-profiling)
       + [Output](#output)
6. [Profiling Your Own Application](#profiling-your-own-application)
7. [Output Files](#output-files)
    * [Task Trace](#task-trace)
       + [Output for Bytecode and Reference-cycles Profiling](#output-for-bytecode-and-reference-cycles-profiling)
       + [Output for Calling-context Profiling](#output-for-calling-context-profiling)
    * [CPU Trace](#cpu-trace)
    * [CS Trace](#cs-trace)
    * [GC Trace](#gc-trace)
8. [Additional Tests](#additional-tests)
9. [About](#about)

## Terminology

**Task**: *tgp* considers as task every subtype of the interfaces java.lang.Runnable and java.util.concurrent.Callable, or the abstract class java.util.concurrent.ForkJoinTask.

**Task Granularity**: task granularity represents the amount of work carried out by each parallel task. In *tgp*, task granularity is defined as all the computations performed in the dynamic extent of the methods Runnable.run, Callable.call, and ForkJoinTask.exec, that are collectively known as *execution methods*.

**Task Execution**: a task is denoted as *executed* if at least one of its execution method is executed by a thread to (normal or abnormal) completion.

**Task Execution Framework**: any subtype of the interface java.util.concurrent.Executor. The term *task submission* denotes the submission of a task to a task execution framework.

## Profiling Modes

*tgp* profiles a target application in three different and mutually exclusive modes:

* **Bytecode profiling:** in this mode, *tgp* profiles task granularity in terms of bytecode count. This mode has the advantage of being platform-independent and does not require any hardware support. However, bytecode count cannot account the execution of methods without a bytecode representation (such as native methods) and is less accurate than reference-cycle count. For more details on bytecode profiling, see section [Output for Bytecode and Reference-cycles Profiling](#output-for-bytecode-and-reference-cycles-profiling).

* **Reference-cycles profiling:** in this mode, *tgp* profiles task granularity in terms of reference-cycle count. This mode has the advantage of accounting the execution of native methods, and can more accurately estimate the work performed by each task. As a downside, it requires the presence of Hardware Performance Counters (HPCs) in the underlying architecture, and it is platform-dependent (as the collected values of task granularity depend on the nominal frequency of the CPU). For more details on reference-cycles profiling, see section [Output for Bytecode and Reference-cycles Profiling](#output-for-bytecode-and-reference-cycles-profiling).

* **Calling-context profiling:** in this mode, *tgp* profiles the calling context upon the creation, submission, and execution of each task. This profiling mode points the user to classes and methods where modifications may be required to optimize task granularity. For more details on calling-context profiling, see section [Output for Calling-context Profiling](#output-for-calling-context-profiling).  

## Metrics

*tgp* profiles metrics from different layers of the system stack, as follows (see the [Output Files](#output-files) section for detailed information about the traces generated by *tgp*):

### Application Layer

*tgp* collects several thread- and task-level information, which are further detailed [here](#output-for-bytecode-and-reference-cycles-profiling). In the bytecode profiling mode, *tgp* collects the bytecode count of each created task. In the calling-context profiling mode, *tgp* profiles the calling contexts upon the creation, submission, and execution of each created task.

### Framework Layer

*tgp* profiles all task submissions, detecting the usage of task execution frameworks.

### JVM Layer

*tgp* detects all time intervals when the garbage collector (GC) executes a [*stop-the-world collection*](http://www.oracle.com/webfolder/technetwork/tutorials/obe/java/gc01/index.html).

### OS Layer

*tgp* profiles CPU utilization (separating user and kernel components) and the number of context switches (CS) experienced by the target application. The former allows one to determine whether the CPU is well utilized by the application. Context switches can be used as a measure of contention between tasks, as an excessive number of context switches are an indication that tasks executing in parallel significantly interfere with each other due to the presence of numerous blocking primitives (caused e.g. by I/O activities, synchronization, and message passing).

### Hardware Layer

In the reference-cycles profiling mode, *tgp* profiles the reference-cycle count of each task to measure its granularity.

## Requirements

*tgp* requires a Linux or MacOS operating system, [`ant`](https://ant.apache.org/), Java 7 or higher installed and the `$JAVA_HOME` variable properly set.

For bytecode or calling-context profiling, there is no further requirement.

For reference-cycle profiling, *tgp* must run on an architecture where HPCs are available, and the [PAPI](http://icl.utk.edu/papi/) library must be installed. Reference-cycle profiling is supported only on the Linux operating system.

To profile CPU utilization, [*top*](https://linux.die.net/man/1/top) needs to be installed, while to profile context switches [*perf*](https://perf.wiki.kernel.org/index.php/Main_Page) is needed. Both metrics can be profiled only on the Linux operating system.

## Testing *tgp*

### Usage

To use *tgp*, clone or download this repository, open the terminal and change the working directory to the *tgp* root directory.

By default, for all the profiling modes, *tgp* profiles a test application which is shipped with this release.

#### Bytecode Profiling

To profile the test application using bytecode count as a measure of task-granularity, run the following command:

`ant profile-task-bc`

#### Reference-cycles Profiling

Alternatively, to profile the test application using reference-cycle count as a measure of task-granularity, run the following command:

`ant profile-task-rc`

#### Calling-context Profiling

Finally, to profile calling contexts, run the following command:

`ant profile-cc`

#### JVM- and OS-layer Metrics

Profiling of metrics at the JVM- and OS-layer is disabled by default. To collect such metrics, change the variables in *metrics.sh* as follows:

* `PROFILE_CS="no"`: set to **"yes"** if you want to profile context switches, **"no"** otherwise
* `PROFILE_CPU="no"`: set to **"yes"** if you want to profile CPU utilization, **"no"** otherwise
* `PROFILE_GC="no"`: set to **"yes"** if you want to profile GC activities, **"no"** otherwise

#### Output

Upon the termination of the profiled application, the *traces/* directory should contain at least the *tasks.csv* file. Depending on the activated metrics, other traces may be available (see [Output Files](#output-files) section).

## Profiling Your Own Application

To profile your own application with *tgp*, set the variables in the *application.sh* file as follows.

* `APP_CLASSPATH="classpath-of-application"`: provide the classpath of the target application
* `APP_FLAGS="flags-of-application"`: provide flags to be passed to the JVM executing the target application, if any 
* `APP_MAIN_CLASS="MainClass"`: provide the name of the main class 
* `APP_ARGS="arguments-of-application"`: provide arguments for the target application, if the application requires them

To profile a target application from a location other than the tgp root directory, set the following variable:

* `ROOT_PATH="path/to/tgp"`: provide the path to the root directory of tgp

Then, run tgp by using the following command instead of the ones listed in section [Usage](#usage):

`ant -buildfile <path/to/tgp/build.xml> <profile-task-bc|profile-task-rc|profile-cc>`

Here is an example of how variables in *application.sh* should be set to profile an application with *tgp* which is normally executed as follows:

`java -cp myapp.jar:mysecondappjar.jar:myfolder -Xms256m -Xmx1g MyMainClass arg1 arg2`

assuming that the root folder of *tgp* is located at `~/tgp/`.

```
ROOT_PATH="~/tgp/"
APP_CLASSPATH="myapp.jar:mysecondappjar.jar:myfolder"
APP_FLAGS="-Xms256m -Xmx1g"
APP_MAIN_CLASS="MyMainClass"
APP_ARGS="arg1 arg2”
```

## Output Files

*tgp* generates *.csv* files in the */traces* directory as follows (note that the directory will be overwritten at each profiling):

### Task Trace

The *tasks.csv* file contains information about all created tasks. Each row refers to a single task, thus the number of rows (excluding the header) indicates the number of tasks created by the target application. 

There are two different versions of this file, depending on the selected profiling mode:

#### Output for Bytecode and Reference-cycles Profiling

The file is composed by several columns as follows:

* ID: a unique JVM-generated code (hashCode) for each task
* Class: the class of the task
* Outer Task ID: the ID of the outer task (-1 if the task is not executed, 0 if the task is not nested) [1]
* Execution N.: an ordinal representing the i-th task execution [2]
* Creation thread ID: the ID of the thread which created the task
* Creation thread class: the class of the thread which created the task
* Creation thread name: the name of the thread which created the task
* Execution thread ID: the ID of the thread which executed the task (-1 if the task was created but not executed)
* Execution thread class: the class of the thread which executed the task (null if the task was not executed)
* Execution thread name: the name of the thread which executed the task (null if the task was not executed)
* Executor ID: the ID of the task execution framework the task was submitted to (-1 if the task was not submitted)
* Executor class: the class of the task execution framework the task was submitted to (null if the task was not submitted)
* Entry execution time: the timestamp when task execution started (-1 if the task was not executed)
* Exit execution time: the timestamp when task execution completed (-1 if the task was not executed)
* Granularity: the granularity of the task measured either in bytecode or reference-cycle count, depending on the chosen profiling mode
* Is Thread: 'T' if the task extends java.lang.Thread, 'F' otherwise [3]
* Is Runnable: 'T' if the task implements java.lang.Runnable, 'F' otherwise
* Is Callable: 'T' if the task implements java.lang.Callable, 'F' otherwise
* Is ForkJoinTask: 'T' if the task extends java.util.concurrent.ForkJoinTask, 'F' otherwise
* Is run() executed: 'T' if the task is a subtype of java.lang.Runnable and was executed by calling the run() method, 'F' otherwise
* Is call() executed: 'T' if the task is a subtype of java.lang.Callable and was executed by calling the call() method, 'F' otherwise
* Is exec() executed: 'T' if the task is a subtype of java.util.concurrent.ForkJoinTask and was executed by calling the exec() method, 'F' otherwise

[1]: the purpose of this column is to identify *nested tasks*. A task is nested if it fully executes inside the dynamic extent of the execution method of another task, which is called *outer task*. This column contains the ID of the outer task, if the task is nested. Information on the outer task can be found in another row of this file. 

[2]: a task can be executed multiple times (i.e., its execution method is executed to completion more than once). Each task execution appears in this file on a different row. The value *i* of this field denotes that this row contains metrics related to the *i*-th execution of this task.

[3]: since java.lang.Thread implements java.lang.Runnable, every Java thread is also a task. The field discriminates threads from other tasks. 

#### Output for Calling-context Profiling 

The file is composed by several columns as follows:

* ID: a unique JVM-generated code (hashCode) for each task
* Class: the class of the task
* Execution N.: an ordinal representing the i-th task execution. See note [2] above.
* Calling Context (init): the calling context, collected upon the creation of this task
* Calling Context (submit): the calling context, collected upon the submission of this task (null if the task was not submitted)
* Calling Context (exec): the calling context, collected upon the execution of this task (null if the task was not executed)

Calling contexts are represented as a string containing all methods open on the call stack when the calling context was collected. Different methods are separated by the symbol `!`.

Here is an example of how the column *Calling Context (init)* may look like:

```
ch/usi/dag/tgp/test/Example.main([Ljava/lang/String;)V!ch/usi/dag/tgp/test/Example$MyTask.<init>([Ljava/lang/Object;)V!
```

The methods are written following the representation of method descriptors defined in the [Java class file format](https://docs.oracle.com/javase/specs/jvms/se8/html/jvms-4.html#jvms-4.3).

In the example, method *main*, defined in class *ch.usi.dag.tgp.test.Example*, which takes an array (`[`) of *String* (`Ljava/lang/String;`) as input parameter and with return type *void* (`V`), calls a constructor (*<init>*) of class *MyTask* (an inner class, defined inside *ch.usi.dag.tgp.test.Example*), which takes an array (`[`) of *Object* (`Ljava/lang/Object;`) as input parameter.

To exemplify how calling context profiling can help the optimization of task granularity, consider the following scenario. *MyTask* is a task whose purpose is to processes some data, passed as input of a constructor as an array of `Object`. The granularity of *MyTask* depends on the kind and the size of such array, since larger arrays would require more computations to be performed by *MyTask* to process all data inside, and vice versa.

Suppose that the granularity of *MyTask* has been classified by the user as too large, and thus needs to be optimized. To do so, one can decrease the amount of data processed by *MyTask*. To this end, one may need to modify the code where the task constructor is called. Such code is contained in the method appearing right before *MyTask.<init>* (i.e., *Example.main*) in the above calling context, which triggers the creation of a new *MyTask* by calling its constructor, passing an array of *Object* as input parameter. The user can then optimize task granularity by modifying *Example.main*, e.g. decreasing the size of the array passed to *MyTask*.  

Other calling contexts (submission and execution) are useful for understanding which methods trigger the submission and the execution of a task, respectively. During task-granularity optimization, one may need to modify the code handling the objects returned after the execution of the task, which can be included in the methods where task submission or execution occurred. Such methods can be easily found by examining calling contexts, following an approach similar to the one exemplified above.  


### CPU Trace

The *cpu.csv* file contains data about CPU utilization, associated with a timestamp (in nanoseconds). Each row refers to a new measurement. The file has the following structure:

```
Timestamp (ns),CPU utilization (user),CPU utilization (kernel)
8055531757501863,50.0,8.3
8055531939110288,33.3,8.3
8055532113909654,8.3,16.7
8055532289063103,0.0,12.5
```

The first column reports a timestamp in nanoseconds, the second column reports CPU utilization by user code, the third column reports CPU utilization by kernel code. CPU utilization ranges from 0 to 100. This metric is sampled approximatively every 150ms.

### CS Trace

The *cs.csv* file contains data about the context switches experienced by the target application. Each row refers to a new measurement. The file has the following structure:

```
Timestamp (ns),Context Switches
8219428637912867,36
8219431141069173,10
8219431241181367,66
8219431341308954,100
```

The first column reports a timestamp in nanoseconds, while the second column reports the number of context switches experienced by the target application since the last measurement.
Context switches are measured every 100ms.

### GC Trace

The *gc.csv* file contains timestamps representing the start and termination of each stop-the-world garbage collection. Each two rows refer to a different GC collection. The file has the following structure:

```
Start GC,7341135166188457
End GC,7341135226213341
Start GC,7341135412676293
End GC,7341135420910871
Start GC,7341135837793799
End GC,7341135855849462
```

The first column represents the event profiled (i.e., the start or the end of a collection cycle), while the second column contains the timestamp associated to the event. 

**Note**: if GC profiling is enabled but this trace is not produced, then no stop-the-world collection occurred during the execution of the target application.

## Additional Tests

This release is shipped with 12 test classes. By default, *tgp* profiles class *TestRunAndJoin* in any profiling mode selected.

You can change the test class to be profiled (see [Profiling Your Own Application](#profiling-your-own-application)) to try *tgp* on different use cases. To do so, modify *application.sh* file as follows:

`APP_MAIN_CLASS="fully-qualified-name-of-test-class"`

You can run the following test classes (all of them defined in package ch.usi.dag.tgp.test):
* TestNestedThreads
* TestJoinAndThreadPool
* TestThreadStarted
* TestRunnableAndCallable
* TestNestedExecution
* TestExecutor
* TestRecursiveTask
* TestMultipleSubmission
* TestSynchronizedExecution
* TestProducerConsumer
* TestRunAndJoin
* TestMultipleTaskExecutions

For example, to profile class *TestNestedThreads*, modify the *application.sh* file as follows:

`APP_MAIN_CLASS="ch.usi.dag.tgp.test.TestNestedThreads"`

## About

*tgp* is developed and maintained by the Dynamic Analysis Group (DAG) of the Faculty of Informatics at [Università della Svizzera italiana (USI)](http://dag.inf.usi.ch/), Lugano, Switzerland. 

### Project Lead

 * Andrea Rosà (andrea [dot] rosa [at] usi [dot] ch)

### Contributors

 * Eduardo Rosales (rosale [at] usi [dot] ch)
 * Federico van Swaaij (federico [dot] van [dot] swaaij [at] usi [dot] ch)

**Note**: Please refer to this [article](https://doi.org/10.1145/3168828) for additional information about *tgp*.