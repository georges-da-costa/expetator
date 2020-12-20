#include <mpi.h>
#include <unistd.h>

#define TIME 30
#define NB 2

int main(int argc, char **argv) {
  MPI_Init(&argc, &argv);
  
  double low = (int) (TIME/(2*NB+1));
  double high = (TIME-low*(NB+1))/NB;

  MPI_Barrier(MPI_COMM_WORLD);
  for (int i=0; i<NB; i++) {
    usleep(low*1000*1000);
    MPI_Barrier(MPI_COMM_WORLD);
    double reference = MPI_Wtime();
    while( MPI_Wtime()-reference < high);
    MPI_Barrier(MPI_COMM_WORLD);
  }
  sleep(low);
  MPI_Barrier(MPI_COMM_WORLD);

  MPI_Finalize();
  return 0;
}

