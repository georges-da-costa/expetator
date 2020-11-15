// Microbenchmark to stress CPU's generation a random number

#include <stdlib.h>
#include <math.h>

int main (int argc, char *argv[])
{
  double i;

  while(1)
    i = rand();

   return i;
}

