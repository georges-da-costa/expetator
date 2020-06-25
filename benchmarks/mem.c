#include <unistd.h>
#include <time.h>
#include <stdio.h>
#include <stdlib.h>
#include <sys/wait.h>

#ifndef STREAM_ARRAY_SIZE
#   define STREAM_ARRAY_SIZE	10000000
#endif

#ifndef NTIMES
#   define NTIMES	1000
#endif

/*

mpicc -O -DNTIMES=1000 stream2.c -o stream.10M
for i in 1 16 32; do mpirun --use-hwthread-cpus -np $i ./stream.10M ; done

*/

#define STREAM_TYPE double

static STREAM_TYPE	a[STREAM_ARRAY_SIZE],
			b[STREAM_ARRAY_SIZE],
			c[STREAM_ARRAY_SIZE];

int main(int argc, char** argv) {
    int			k;
    ssize_t		j;
    STREAM_TYPE		scalar;

    int nb_processes=1;
    if(argc==2)
      nb_processes = atoi(argv[1]);

    int i;
    for(i=0; i<nb_processes-1; i++)
      if(fork() == 0)
	break;

    // Prefill
    for (j = 0; j < STREAM_ARRAY_SIZE; j++)
      a[j] = 2.0E0 * a[j];

    struct timespec ts_ref, ts;
    clock_gettime(CLOCK_MONOTONIC, &ts_ref);

    scalar = 3.0;
    for (k=0; k<NTIMES; k++)
      for (j=0; j<STREAM_ARRAY_SIZE; j++)
	a[j] = b[j]+scalar*c[j];
    
    if(i==nb_processes-1) {
      clock_gettime(CLOCK_MONOTONIC, &ts);
      long double current_tempo =   ((long double)(ts.tv_sec-ts_ref.tv_sec))+((long double)(ts.tv_nsec-ts_ref.tv_nsec))/1000000000;
      printf("%Lf\n", current_tempo);


      while (wait(NULL) > 0);

    }
}
