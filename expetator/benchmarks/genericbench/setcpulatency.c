#include <stdio.h>
#include <stdint.h>
#include <stdlib.h>
#include <unistd.h>

#include <fcntl.h>

int main(int argc, char **argv) {
  int32_t l;
  int fd;
  
  if (argc != 2) {
    fprintf(stderr, "Usage: %s <latency in us>\n"
                    "\n  Writing a maximum allowable latency of 0 will "
                    "keep the processors in C0 (like using kernel "
                    "parameter ―idle=poll), andwriting 1 should force "
                    "the processors to C1 when idle. "
                    "Higher values could also be written to restrict "
                    "the use of C-states with latency greater than the "
                    "value written.", argv[0]);
    return 2;
  }
  
  l = atoi(argv[1]);
  printf("setting latency to %d us\n", l);
  fd = open("/dev/cpu_dma_latency", O_WRONLY);
  if (fd < 0) {
    perror("open /dev/cpu_dma_latency");
    return 1;
  }

  if (write(fd, &l, sizeof(l)) != sizeof(l)) {
    perror("write to /dev/cpu_dma_latency");
    return 1;
  }

  while (1) pause();
}
