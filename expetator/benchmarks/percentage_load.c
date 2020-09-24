#include <stdio.h>
#include <stdlib.h>
#include <sys/time.h>
#include <unistd.h>

#define INNER 10000
#define REFERENCE 10000
#define SCALE 10

// Copyright IRIT/UPS/Georges Da Costa 2016

int main(int argc, char**argv) {
  if((argc-1)%2 != 0) {
    printf("Usage : \n");
    printf("./load L1 V1 L2 V2 ...\n");
    printf("with L* Loads (percentage), V* volumes (seconds)\n");
    exit(-1);
  }

  struct timeval t0, t1;
  gettimeofday(&t0, 0);
  float f=0;
  int nb=0;
  while(f<1) {
    int i,j;
    for(i=0; i<REFERENCE; i++)
      for(j=0; j<INNER; j++)
	random();

    gettimeofday(&t1, 0);
    unsigned long elapsed = (t1.tv_sec-t0.tv_sec)*1000000 + t1.tv_usec-t0.tv_usec;
    f = (float)elapsed/1000000;
    nb++;
  }
  unsigned long int reference = (unsigned long) ((nb*(float)REFERENCE)/f);
  //  printf("reference: %lu\n", (unsigned long) reference);

  int pos=0;
  while(pos<argc-1) {
    pos+=2;
    int load=atoi(argv[pos-1]);
    int volume=atoi(argv[pos]);

    load = load * reference / 100;
    
    // printf("load: %d, volume: %d\n", load, volume); 

    struct timeval t0, t1;
    gettimeofday(&t0, 0);

    int total=0;
    
    while(total<volume*SCALE) {
      int i,j;
      for(i=0; i<load/SCALE; i++)
	for(j=0; j<INNER; j++)
	  random();
      total+=1;

      gettimeofday(&t1, 0);
      unsigned long elapsed = (t1.tv_sec-t0.tv_sec)*1000000 + t1.tv_usec-t0.tv_usec;
      
      long e2 = (total*1000000/SCALE)-elapsed;
      if(e2>0)
	usleep(e2);
    }
    gettimeofday(&t1, 0);
    unsigned long elapsed = (t1.tv_sec-t0.tv_sec)*1000000 + t1.tv_usec-t0.tv_usec;
    f = (float)elapsed/1000000;
    printf("%f\n", load/SCALE * total / f);
  }

}
