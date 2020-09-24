#include <mpi.h>
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <time.h>
#include <string.h>

int world_rank;
int world_size;

#ifndef SIZE
#define SIZE 1024*300
#endif

char tmp[SIZE];
char *big_tmp;

void init_mpi(int* argc, char*** argv) {
  MPI_Init(argc, argv);
  MPI_Comm_rank(MPI_COMM_WORLD, &world_rank);
  MPI_Comm_size(MPI_COMM_WORLD, &world_size);
  big_tmp = malloc(SIZE*sizeof(char)*world_size);
  memset(tmp, SIZE, 42);
}

static inline void mpi_com() {
  MPI_Allgather(tmp, SIZE, MPI_BYTE, big_tmp, SIZE, MPI_BYTE, MPI_COMM_WORLD);
}

static inline void mpi_barrier(){
  if(world_rank==world_size-1) {
    usleep(2000);
  }
  MPI_Barrier(MPI_COMM_WORLD);
}

#define MEMMAX   ((1 << 19) - 1)
double tab[2*MEMMAX];
double tab2[2*MEMMAX];
double tab3[2*MEMMAX];
int j=0;
static inline void memory() {
  for(j=0; j<MEMMAX; j++)
    tab3[j]=tab2[j]+2.0*tab[j];
}

static inline void cpu() {
  j=rand()%MEMMAX;
  j=rand()%MEMMAX;
  j=rand()%MEMMAX;
  j=rand()%MEMMAX;
  j=rand()%MEMMAX;
  j=rand()%MEMMAX;
  j=rand()%MEMMAX;
  j=rand()%MEMMAX;
  j=rand()%MEMMAX;
  j=rand()%MEMMAX;
  j=rand()%MEMMAX;
  j=rand()%MEMMAX;
  j=rand()%MEMMAX;
  j=rand()%MEMMAX;
  j=rand()%MEMMAX;
  j=rand()%MEMMAX;
  j=rand()%MEMMAX;
  j=rand()%MEMMAX;
  j=rand()%MEMMAX;
  j=rand()%MEMMAX;
  j=rand()%MEMMAX;
  j=rand()%MEMMAX;
  j=rand()%MEMMAX;
  j=rand()%MEMMAX;
  j=rand()%MEMMAX;
  j=rand()%MEMMAX;
  j=rand()%MEMMAX;
  j=rand()%MEMMAX;
  j=rand()%MEMMAX;
  j=rand()%MEMMAX;
}


void usage(const char* name){
  fprintf(stderr, "Usage: %s [-c ncpu] [-m nmem] [-n nmpi] [-b nbarrier] \n",
	  name);
  exit(EXIT_FAILURE);
}

/* Nova
1 process : cpu : 330 == 10s
1 process : mem : 306 == 10s
2 process même machine : mpi : 24 == 10s
2 process même machine : mpi+openib : idem
2 process sur deux machines : 1 == 10s
32 process sur deux machines : mpi : 1 == 1m45
32 process sur deux machines : mpi+openib idem
*/

/*
mpirun --oversubscribe --mca btl ^openib --machinefile $OAR_NODE_FILE --mca orte_rsh_agent "oarsh" -n 32 ./generic -n 1

or
nova-5.lyon.grid5000.fr slots=1
nova-7.lyon.grid5000.fr slots=1

or
mpirun  --host localhost:10 ....

 */

#define BIGLOOP 1000
int main(int argc, char** argv) {
  int nmpi=0;
  int ncpu=0;
  int nmem=0;
  int nbar=0;
  int opt;

  if (argc==1) usage(argv[0]);

  while ((opt = getopt(argc, argv, "c:m:n:b:")) != -1) {
    switch (opt) {
    case 'c':
      ncpu = atoi(optarg);
      break;
    case 'm':
      nmem = atoi(optarg);
      break;
    case 'n':
      nmpi = atoi(optarg);
      break;
    case 'b':
      nbar=atoi(optarg);
      break;
    default:
      usage(argv[0]);
    }
  }

  init_mpi(&argc, &argv);
  struct timespec ts_ref, ts;
  clock_gettime(CLOCK_MONOTONIC, &ts_ref);

  int nb;

  /*
  for(int i=0; i<BIGLOOP; i++) {
    for(nb=0; nb<nmpi; nb++) mpi_com();
    for(nb=0; nb<nmem; nb++) memory();    
    for(nb=0; nb<nbar; nb++) mpi_barrier();
    for(nb=0; nb<ncpu; nb++) cpu();
  }
  */
  int tmpi, tmem, tbar, tcpu;
  for(int i=0; i<BIGLOOP; i++) {
    tmpi = nmpi; tmem = nmem; tbar = nbar; tcpu = ncpu;
    while(tmpi+tmem+tbar+tcpu > 0){
      if(tmpi>0) { tmpi--; mpi_com(); }
      if(tmem>0) { tmem--; memory(); }
      if(tbar>0) { tbar--; mpi_barrier(); }
      if(ncpu>0) { tcpu--; cpu(); }
    }
  }

  if(world_rank==0) {
    clock_gettime(CLOCK_MONOTONIC, &ts);
    long double current_tempo =   ((long double)(ts.tv_sec-ts_ref.tv_sec))+((long double)(ts.tv_nsec-ts_ref.tv_nsec))/1000000000;
    printf("%Lf\n", current_tempo);
  }
  MPI_Finalize();
}


// -c 120
// -m 2500
// -n 7


// Nova : 10s
// -c 350
// -m 8000


// Nova all nodes : 1min
// -n 1
// -c 1200
// -m 35000

/* time mpirun --machinefile /dev/shm/m ./a.out -m 35000 -n 1 -c 1200
/dev/shm/m : 32 == cores
real	2m26.163s
user	32m6.416s
sys	5m27.728s

-m 35000 real:0m59.131s   user:15m13.312s   sys:0m5.656s
-n 1     real:0m54.096s   user:6m32.928s    sys:6m44.876s
-c 1200  real:0m50.059s   user:11m43.064s   sys:0m1.696s

/*

/* time mpirun  --machinefile /dev/shm/m2 ./a.out -m 35000 -n 1 -c 1200
/dev/shm/m2 : 64 == hyperthread
real	3m38.990s
user	101m59.836s
sys	12m21.300s

-m 35000 real:1m52.471s   user:58m37.784s   sys:0m21.500s
-n 1     real:0m54.545s   user:13m44.444s   sys:14m47.212s
-c 1200  real:1m11.609s   user:35m41.120s   sys:0m3.540s
*/

/* RQ: avec mpirun --mca btl ^openib

time mpirun  --mca btl ^openib --machinefile /dev/shm/m ./a.out -n 1
real	0m53.827s
user	6m38.412s
sys	6m46.088s

time mpirun  --machinefile /dev/shm/m ./a.out -n 1
real	0m53.990s
user	6m43.392s
sys	6m53.344s
*/
