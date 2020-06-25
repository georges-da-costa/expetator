#include <stdio.h>
#include <time.h>
#include <string.h>
#include <stdlib.h>
#include <unistd.h>
#include <signal.h>
#include <sys/wait.h>

int current_nop;

void show_nop(int none){
  printf("%d\n", current_nop/10);
  exit(EXIT_SUCCESS);
}

int main(int argc, char **argv) {

  long double nops = 10*1000; // in 1000 operations per seconds
  long double total_nop=1 * nops; // (in number of operations)
  int nb_processes = 1;
  
  if(argc == 3) {
    nops = atol(argv[1]);
    total_nop = atof(argv[2])*nops;
  }
  if(argc == 4) {
    nops = atol(argv[1]);
    total_nop = atof(argv[2])*nops;
    nb_processes = atoi(argv[3]);
  }
  else if (argc == 2 && strcmp(argv[1], "--test")==0) {
    signal(SIGALRM, show_nop);
    current_nop = 0;
    struct timespec ts;

    alarm(10);
    while(1) {
      int a;
      for(int _tmp=0; _tmp<10000; _tmp++)
	a=rand();
      clock_gettime(CLOCK_MONOTONIC, &ts);

      current_nop++;
    }
  } else {
    char *name=argv[0];
    printf("Usage : %s --test \nor      %s numberOpsPerSecond DurationSecondIfUnderloaded\n", name, name);
    return(EXIT_SUCCESS);
  }

  long double current_tempo, goal_tempo;


    int i;
    for(i=0; i<nb_processes-1; i++)
      if(fork() == 0)
	break;

  
    struct timespec ts_ref, ts;
    clock_gettime(CLOCK_MONOTONIC, &ts_ref);

    for(current_nop=0; current_nop<total_nop; current_nop++) {
      int a;
      for(int _tmp=0; _tmp<10000; _tmp++)
	a=rand();

      clock_gettime(CLOCK_MONOTONIC, &ts);

      current_tempo =   ((long double)(ts.tv_sec-ts_ref.tv_sec))+((long double)(ts.tv_nsec-ts_ref.tv_nsec))/1000000000;

      goal_tempo = current_nop/nops;

      useconds_t delta=1000000*(goal_tempo - current_tempo);
      if(goal_tempo > current_tempo) {
	usleep(delta);
      }
    }


    if(i==nb_processes-1) {
      clock_gettime(CLOCK_MONOTONIC, &ts);
      current_tempo =   ((long double)(ts.tv_sec-ts_ref.tv_sec))+((long double)(ts.tv_nsec-ts_ref.tv_nsec))/1000000000;
      printf("%Lf\n", current_tempo);

      while (wait(NULL) > 0);
	    
    }

    return(EXIT_SUCCESS);
}
