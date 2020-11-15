// Microbenchmark to evaluate the impact of register read/write 
// 
// To deploy cache misses check the following funcation call:
// perf stat -a -e cache-references -e cache-misses -e L1-dcache-loads -e L1-dcache-load-misses -e L1-dcache-stores -e L1-dcache-store-misses -e L1-dcache-prefetches -e L1-dcache-prefetch-misses bin/ubench_cpu_l1d

#include <stdlib.h>
#include <stdio.h>
#include <sys/types.h>
#include <dirent.h>

#define CACHE_PATH "/sys/devices/system/cpu/cpu0/cache/"
#define RAM_PATH "/proc/meminfo"
#define PATH_MAX_LENGTH 256
#define MAX_CACHE_LAYERS 3
#define TLB_PG_SIZE 4*1024

// Stores cache sizes into an array in position LAYER-1
// L1 consider only the data or unified memory
unsigned cache_size[MAX_CACHE_LAYERS];
unsigned llc; // Last Layer Cache Level
unsigned ram_size;
long iterations;
int op_id;

unsigned read_size(char* file_path) {
  char path[PATH_MAX_LENGTH];
  unsigned size;
  char mag;
  FILE* fd;

  if ((fd = fopen(file_path, "r")) != NULL) {
    fscanf(fd, "%u", &size);
    fscanf(fd, "%c", &mag);
    fclose(fd);

    if (mag == 'K')
      size *= 1024;
    else if (mag == 'M')
      size *= 1024 * 1024;
  }

  return size;
}

unsigned read_level(char* file_path) {
  FILE* fd;
  unsigned level;

  level = 0;
  if ((fd = fopen(file_path, "r")) != NULL) {
    fscanf(fd, "%u", &level);
    fclose(fd);
  }
  return level;
}

char read_type(char* file_path) {
  char type;
  FILE* fd;

  if ((fd = fopen(file_path, "r")) != NULL) {
    fscanf(fd, "%c", &type);
    fclose(fd);
  }

  return type;
}

void get_cache_size() {
  DIR *dp;
  struct dirent *ep;
  char path[256];
  unsigned level, size;
  char type;
  char magnitude;

  dp = opendir(CACHE_PATH);

  for (level = 0; level < MAX_CACHE_LAYERS; level++) {
    cache_size[level] = 0;
  }

  if (dp != NULL) {
    while (ep = readdir(dp)) {
      sprintf(path, CACHE_PATH "%s/level", ep->d_name);
      level = read_level(path);

      if (level > 0) {
        sprintf(path, CACHE_PATH "%s/type", ep->d_name);
        type = read_type(path);

        if (type == 'D' || type == 'U') {
          sprintf(path, CACHE_PATH "%s/size", ep->d_name);
          size = read_size(path);

          if (level > llc) {
            llc = level;
          }

          cache_size[level - 1] = size;
        }
      }
    }

    (void) closedir(dp);
  } else {
    printf("ERROR: Couldn't open the directory");
    exit(1);
  }
}

// Get RAM size in kB
void get_ram_size() {
  FILE* fd;
  char dull[32];

  ram_size = 0;

  if ((fd = fopen(RAM_PATH, "r")) != NULL) {
    fscanf(fd, "%s", dull);
    fscanf(fd, "%u", &ram_size);
    fclose(fd);
  }
}

void usage(const char *cmd) {
  printf("Usage: %s mem_id [iter]\n", cmd);
  printf("\nOptions:\n");
  printf("  mem_id     memory id: 0-Register, 1-L1d, 2-L2, 3-L3, 4-RAM.\n");
  printf("  iter       number of iterations (default 0: infinity).\n");
  printf("  op_id      operation id: 0-Read, 1-Write, 2-Read/Write.\n");
  printf("\nExample:\n");
  printf("  %s 1 1000000000 1\n", cmd);
  printf("  %s 2 0 0\n", cmd);
  printf("  %s 3 0 2\n", cmd);
}

void read_mem(unsigned sz_max, float *vect) {
  register float pos = 0;
  int i, p = 0;

  if (iterations == 0) {
    // stress cache level
    if (sz_max == 1) {
      while (1) {
        p = (p + TLB_PG_SIZE / sizeof(float)) % sz_max;
        pos = pos * p + p;
      }
    } else {
      while (1) {
        p = (p + TLB_PG_SIZE / sizeof(float)) % sz_max;
        pos = vect[p] * p + p;
      }
    }
  } else {
    // stress cache level
    if (sz_max == 1) {
      for (i = 0; i < iterations; i++) {
        p = (p + TLB_PG_SIZE / sizeof(float)) % sz_max;
        pos = pos * p + p;
      }
    } else {
      for (i = 0; i < iterations; i++) {
        p = (p + TLB_PG_SIZE / sizeof(float)) % sz_max;
        pos = vect[p] * p + p;
      }
    }
  }
}

void write_mem(unsigned sz_max, float *vect) {
  register float pos = 0;
  int i, p = 0;

  if (iterations == 0) {
    // stress cache level
    if (sz_max == 1) {
      while (1) {
        p = (p + TLB_PG_SIZE / sizeof(float)) % sz_max;
        pos = pos * p + p;
      }
    } else {
      while (1) {
        p = (p + TLB_PG_SIZE / sizeof(float)) % sz_max;
        vect[p] = pos * p + p;
      }
    }
  } else {
    // stress cache level
    if (sz_max == 1) {
      for (i = 0; i < iterations; i++) {
        p = (p + TLB_PG_SIZE / sizeof(float)) % sz_max;
        pos = pos * p + p;
      }
    } else {
      for (i = 0; i < iterations; i++) {
        p = (p + TLB_PG_SIZE / sizeof(float)) % sz_max;
        vect[p] = pos * p + p;
      }
    }
  }
}

void readwrite_mem(unsigned sz_max, float *vect) {
  register float pos = 0;
  int i, p = 0;

  if (iterations == 0) {
    // stress cache level
    if (sz_max == 1) {
      while (1) {
        p = (p + TLB_PG_SIZE / sizeof(float)) % sz_max;
        pos = pos * p + p;
      }
    } else {
      while (1) {
        p = (p + TLB_PG_SIZE / sizeof(float)) % sz_max;
        vect[p] = vect[p] * p + p;
      }
    }
  } else {
    // stress cache level
    if (sz_max == 1) {
      for (i = 0; i < iterations; i++) {
        p = (p + TLB_PG_SIZE / sizeof(float)) % sz_max;
        pos = pos * p + p;
      }
    } else {
      for (i = 0; i < iterations; i++) {
        p = (p + TLB_PG_SIZE / sizeof(float)) % sz_max;
        vect[p] = vect[p] * p + p;
      }
    }
  }
}

void stress_mem(int id, unsigned vect_size, float *vect) {
  unsigned sz_min, sz_max = 0;
  register float pos = 0;

  switch (id) {
  case 0: // Register
    sz_min = 0;
    sz_max = 1;
    break;
  case 1: // L1
    sz_min = 0;
    sz_max = cache_size[0] / sizeof(float);
    break;
  case 2: // L2
    sz_min = cache_size[0] / sizeof(float);
    sz_max = cache_size[1] / sizeof(float);
    break;
  case 3: // L3
    sz_min = cache_size[1] / sizeof(float);
    sz_max = cache_size[2] / sizeof(float);
    break;
  case 4: // RAM
    sz_min = cache_size[llc - 1] / sizeof(float);
    sz_max = vect_size;
    break;
  }
  printf("min: %u, max: %u\n", sz_min, sz_max);

  switch (op_id) {
  case 0:
    read_mem(sz_max, vect);
    break;
  case 1:
    write_mem(sz_max, vect);
    break;
  default:
    readwrite_mem(sz_max, vect);
    break;
  }
}

int main(int argc, char *argv[]) {
  float *vect;
  unsigned vect_size = 0;
  unsigned size_kb = 0;
  int id = 0;
  //iterations = 1000000000;
  iterations = 0;
  op_id = 0;

  get_cache_size();
  get_ram_size();

  if (argc != 4) {
    usage(argv[0]);
    exit(1);
  }

  id = atoi(argv[1]);
  iterations = atoi(argv[2]);
  op_id = atoi(argv[3]);

  size_kb = (10 * cache_size[llc - 1]) / 1024;
  if (size_kb > ram_size) {
    size_kb = ram_size;
  }

  vect_size = 1024 * size_kb / sizeof(float);
  vect = (float*) calloc(vect_size, sizeof(float));

  printf("ID:  %u\n", id);
  stress_mem(id, vect_size, vect);

  free(vect);

  return 0;
}

